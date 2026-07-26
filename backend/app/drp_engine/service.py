"""Orquestração do Motor DRP: o ponto de entrada `recalcular_sku_elo` junta
necessidade líquida (issue #20), status (issue #21, incluindo Ruptura por
DRP), priorização (issue #23), decisão de ressuprimento (issue #22) e
overrides de negócio — Silenciar Produto e Cobertura de Estoque Manual
(issue #29) — e grava a trilha de auditoria (issue #26).

Recalculo incremental orientado a eventos (issue #27): esta função é
desenhada para ser chamada tanto sob demanda (endpoint da API) quanto por
um gatilho futuro (venda registrada, entrada de NF, atualização de
trânsito) — é idempotente e barata o suficiente para isso. A ligação com
um barramento de eventos real (fila/Celery, citados no roadmap seção 3)
ainda não existe; hoje o disparo é manual, via API.
"""

import uuid
from dataclasses import dataclass
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.drp_engine.decisao import EloRef, decidir_ressuprimento
from app.drp_engine.necessidade import calcular_necessidade_liquida
from app.drp_engine.priorizacao import calcular_score
from app.drp_engine.status import avaliar_ruptura_rede, classificar_status_local
from app.forecasting.service import gerar_projecao
from app.models.auditoria import LogDecisao, MotivoSilenciamento, TipoAutor
from app.models.cadastro import Filial, Sku
from app.models.drp import OrdemCompra, OrdemTransferencia, StatusEstoqueSnapshot, StatusRuptura
from app.models.estoque import EstoqueTransito, SaldoEstoque
from app.models.forecast import Projecao


def _cobertura_dias(saldo: float, demanda_projetada: float, horizonte_dias: int, override: float | None) -> float:
    if override is not None:
        return float(override)
    if demanda_projetada <= 0:
        return float("inf") if saldo > 0 else 0.0
    demanda_diaria = demanda_projetada / horizonte_dias
    return saldo / demanda_diaria if demanda_diaria > 0 else float("inf")


async def _saldo_disponivel(db: AsyncSession, sku_id: uuid.UUID, elo: EloRef) -> float:
    """Soma todas as linhas de saldo do elo (não assume uma única linha por
    sku/elo — o modelo não impõe essa restrição)."""
    stmt = select(SaldoEstoque.quantidade).where(SaldoEstoque.sku_id == sku_id)
    stmt = stmt.where(SaldoEstoque.cd_id == elo.cd_id) if elo.cd_id else stmt.where(
        SaldoEstoque.filial_id == elo.filial_id
    )
    result = await db.execute(stmt)
    return float(sum(float(q) for q in result.scalars().all()))


async def _estoque_transito(db: AsyncSession, sku_id: uuid.UUID, elo: EloRef) -> float:
    stmt = select(EstoqueTransito).where(EstoqueTransito.sku_id == sku_id)
    stmt = (
        stmt.where(EstoqueTransito.destino_cd_id == elo.cd_id)
        if elo.cd_id
        else stmt.where(EstoqueTransito.destino_filial_id == elo.filial_id)
    )
    result = await db.execute(stmt)
    pendente = 0.0
    for registro in result.scalars().all():
        pendente += float(registro.quantidade_solicitada) - float(registro.quantidade_recebida)
    return max(pendente, 0.0)


async def _demanda_projetada(db: AsyncSession, sku_id: uuid.UUID, elo: EloRef, horizonte_dias: int) -> float:
    stmt = select(Projecao).where(Projecao.sku_id == sku_id)
    stmt = (
        stmt.where(Projecao.cd_id == elo.cd_id)
        if elo.cd_id
        else stmt.where(Projecao.filial_id == elo.filial_id)
    )
    stmt = stmt.order_by(Projecao.gerado_em.desc()).limit(1)
    result = await db.execute(stmt)
    projecao = result.scalar_one_or_none()
    if projecao is not None:
        return float(projecao.quantidade_projetada)

    # Sem projeção calculada ainda para este elo — gera uma agora (Fase 3
    # consome a saída da Fase 2 sob demanda) em vez de assumir demanda zero.
    nova = await gerar_projecao(
        db, sku_id=sku_id, horizonte_dias=horizonte_dias, cd_id=elo.cd_id, filial_id=elo.filial_id
    )
    return float(nova.quantidade_projetada)


@dataclass
class AvaliacaoElo:
    necessidade: float
    status: StatusRuptura
    saldo: float
    cobertura_dias: float


async def _avaliar_elo(db: AsyncSession, sku: Sku, elo: EloRef, horizonte_dias: int) -> AvaliacaoElo:
    """Cálculo somente-leitura de necessidade/status para um elo — usado
    tanto para o elo principal quanto para agregar a necessidade das
    filiais de um CD ao avaliar Ruptura por DRP."""
    saldo = await _saldo_disponivel(db, sku.id, elo)
    transito = await _estoque_transito(db, sku.id, elo)
    demanda = await _demanda_projetada(db, sku.id, elo, horizonte_dias)

    estoque_seguranca = float(sku.estoque_seguranca or 0)
    necessidade = calcular_necessidade_liquida(demanda, estoque_seguranca, saldo, transito)

    cobertura = _cobertura_dias(
        saldo, demanda, horizonte_dias,
        float(sku.cobertura_estoque_manual_dias) if sku.cobertura_estoque_manual_dias is not None else None,
    )
    status_local = classificar_status_local(
        saldo,
        float(sku.estoque_maximo or 0),
        float(sku.ponto_pedido or 0),
        cobertura,
        float(sku.lead_time_dias or horizonte_dias),
    )
    return AvaliacaoElo(necessidade=necessidade, status=status_local, saldo=saldo, cobertura_dias=cobertura)


async def _sku_silenciado(db: AsyncSession, sku_id: uuid.UUID) -> MotivoSilenciamento | None:
    hoje = date.today()
    stmt = select(MotivoSilenciamento).where(
        MotivoSilenciamento.sku_id == sku_id,
        MotivoSilenciamento.data_inicio <= hoje,
    )
    result = await db.execute(stmt)
    for motivo in result.scalars().all():
        if motivo.data_fim is None or motivo.data_fim >= hoje:
            return motivo
    return None


@dataclass
class ResultadoRecalculo:
    snapshot: StatusEstoqueSnapshot
    ordem: OrdemTransferencia | OrdemCompra | None
    silenciado_motivo: str | None


async def recalcular_sku_elo(
    db: AsyncSession,
    sku_id: uuid.UUID,
    cd_id: uuid.UUID | None = None,
    filial_id: uuid.UUID | None = None,
) -> ResultadoRecalculo:
    sku = await db.get(Sku, sku_id)
    if sku is None:
        raise ValueError(f"SKU {sku_id} não encontrado")

    elo = EloRef(cd_id=cd_id, filial_id=filial_id)
    horizonte_dias = int(sku.lead_time_dias or 7)

    avaliacao = await _avaliar_elo(db, sku, elo, horizonte_dias)
    necessidade = avaliacao.necessidade
    status_final = avaliacao.status

    # Ruptura por DRP (seção 3.1): só avaliada quando o elo é uma filial
    # com CD supridor e o status local não já indica ruptura/exposição.
    if filial_id is not None and avaliacao.status in (
        StatusRuptura.ADEQUADO,
        StatusRuptura.EXCESSO,
    ):
        filial = await db.get(Filial, filial_id)
        if filial is not None and filial.cd_supridor_id is not None:
            stmt_irmas = select(Filial.id).where(Filial.cd_supridor_id == filial.cd_supridor_id)
            irmas = (await db.execute(stmt_irmas)).scalars().all()

            necessidade_agregada = 0.0
            for filial_irma_id in irmas:
                avaliacao_irma = await _avaliar_elo(
                    db, sku, EloRef(filial_id=filial_irma_id), horizonte_dias
                )
                necessidade_agregada += max(avaliacao_irma.necessidade, 0.0)

            saldo_cd = await _saldo_disponivel(db, sku_id, EloRef(cd_id=filial.cd_supridor_id))
            if avaliar_ruptura_rede(necessidade_agregada, saldo_cd):
                status_final = StatusRuptura.RUPTURA_DRP

    agora = datetime.now(timezone.utc)
    snapshot = StatusEstoqueSnapshot(
        sku_id=sku_id,
        cd_id=cd_id,
        filial_id=filial_id,
        necessidade_liquida=necessidade,
        status=status_final,
        calculado_em=agora,
    )
    db.add(snapshot)

    ordem: OrdemTransferencia | OrdemCompra | None = None
    silenciado_motivo: str | None = None

    if necessidade > 0 and not sku.ativo:
        silenciado_motivo = "SKU inativado (roadmap seção 4.11/11 — governança e saneamento)"
        db.add(
            LogDecisao(
                entidade="sku",
                entidade_id=sku_id,
                acao="SUGESTAO_SUPRIMIDA_SKU_INATIVO",
                motivo=f"Necessidade de {necessidade:.2f} un. não gerou ordem: SKU inativo.",
                tipo_autor=TipoAutor.SISTEMA,
            )
        )
    elif necessidade > 0:
        motivo_silenciamento = await _sku_silenciado(db, sku_id)
        if motivo_silenciamento is not None:
            silenciado_motivo = motivo_silenciamento.motivo
            db.add(
                LogDecisao(
                    entidade="sku",
                    entidade_id=sku_id,
                    acao="SUGESTAO_SUPRIMIDA_SILENCIAMENTO",
                    motivo=f"Necessidade de {necessidade:.2f} un. não gerou ordem: {motivo_silenciamento.motivo}",
                    tipo_autor=TipoAutor.SISTEMA,
                )
            )
        else:
            score = calcular_score(
                sku.criticidade_resultado,
                sku.custo_aquisicao,
                cobertura_atual_dias=avaliacao.cobertura_dias,
                frequencia_saida=sku.frequencia_saida,
            )
            ordem, justificativa = await decidir_ressuprimento(db, sku, elo, necessidade, score)
            tipo_ordem = "ordem_transferencia" if isinstance(ordem, OrdemTransferencia) else "ordem_compra"
            db.add(
                LogDecisao(
                    entidade=tipo_ordem,
                    entidade_id=ordem.id,
                    acao="ORDEM_GERADA",
                    motivo=justificativa,
                    tipo_autor=TipoAutor.SISTEMA,
                )
            )

    await db.commit()
    await db.refresh(snapshot)
    if ordem is not None:
        await db.refresh(ordem)

    return ResultadoRecalculo(snapshot=snapshot, ordem=ordem, silenciado_motivo=silenciado_motivo)
