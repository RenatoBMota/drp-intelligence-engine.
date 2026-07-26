"""Motor de decisão: Transferência interna vs. Compra externa (roadmap
seção 6.4) e geração das ordens correspondentes (seção 6.6) — issues #22,
#24, #25.

Simplificação de escopo: o domínio "Transporte" do roadmap (seção 8: rotas,
lead time por rota, capacidade) ainda não foi modelado — por isso o lead
time de transferência interna usa uma constante padrão, e a busca por elo
doador não considera capacidade de transporte nem custo de rota (isso é
otimização de rede, explicitamente Fase 4 no roadmap seção 6.5/7).
"""

import uuid
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cadastro import Filial, Sku
from app.models.drp import OrdemCompra, OrdemTransferencia, StatusOrdem
from app.models.estoque import SaldoEstoque

LEAD_TIME_TRANSFERENCIA_PADRAO_DIAS = 2


@dataclass
class EloRef:
    cd_id: uuid.UUID | None = None
    filial_id: uuid.UUID | None = None

    def __post_init__(self) -> None:
        if (self.cd_id is None) == (self.filial_id is None):
            raise ValueError("EloRef precisa de exatamente um entre cd_id/filial_id")


async def _encontrar_elo_doador(
    db: AsyncSession, sku: Sku, elo_destino: EloRef, necessidade: float
) -> EloRef | None:
    ponto_pedido = float(sku.ponto_pedido or 0)

    stmt = select(SaldoEstoque).where(SaldoEstoque.sku_id == sku.id)
    result = await db.execute(stmt)
    saldos = result.scalars().all()

    candidatos: list[tuple[EloRef, float]] = []
    for saldo in saldos:
        elo = EloRef(cd_id=saldo.cd_id, filial_id=saldo.filial_id)
        if elo.cd_id == elo_destino.cd_id and elo.filial_id == elo_destino.filial_id:
            continue
        excedente = float(saldo.quantidade) - ponto_pedido
        if excedente >= necessidade:
            candidatos.append((elo, excedente))

    if not candidatos:
        return None

    # Preferência: o CD supridor natural da filial de destino, se ele for
    # um dos candidatos com excedente suficiente.
    if elo_destino.filial_id is not None:
        filial_destino = await db.get(Filial, elo_destino.filial_id)
        if filial_destino is not None and filial_destino.cd_supridor_id is not None:
            for elo, _ in candidatos:
                if elo.cd_id == filial_destino.cd_supridor_id:
                    return elo

    # Sem CD supridor natural disponível: escolhe quem tem maior excedente.
    candidatos.sort(key=lambda par: par[1], reverse=True)
    return candidatos[0][0]


async def decidir_ressuprimento(
    db: AsyncSession,
    sku: Sku,
    elo_destino: EloRef,
    necessidade: float,
    score_criticidade: float,
) -> tuple[OrdemTransferencia | OrdemCompra, str]:
    """Decide entre transferência interna e compra externa, persiste a
    ordem e retorna (ordem, justificativa) para a trilha de auditoria."""

    hoje = date.today()
    elo_doador = await _encontrar_elo_doador(db, sku, elo_destino, necessidade)

    if elo_doador is not None:
        justificativa = (
            f"Necessidade líquida de {necessidade:.2f} un. suprida por transferência interna: "
            f"elo doador com excedente identificado acima do ponto de pedido."
        )
        ordem = OrdemTransferencia(
            sku_id=sku.id,
            origem_cd_id=elo_doador.cd_id,
            origem_filial_id=elo_doador.filial_id,
            destino_cd_id=elo_destino.cd_id,
            destino_filial_id=elo_destino.filial_id,
            quantidade=necessidade,
            data_embarque_sugerida=hoje,
            data_chegada_estimada=hoje + timedelta(days=LEAD_TIME_TRANSFERENCIA_PADRAO_DIAS),
            status=StatusOrdem.SUGERIDA,
            score_criticidade=score_criticidade,
            justificativa=justificativa,
        )
    else:
        if sku.fornecedor_id is None:
            raise ValueError(
                f"SKU {sku.codigo} não tem fornecedor cadastrado e nenhum elo doador foi "
                "encontrado na rede — não é possível gerar ordem de compra nem de transferência."
            )
        lead_time = sku.lead_time_dias or LEAD_TIME_TRANSFERENCIA_PADRAO_DIAS
        justificativa = (
            f"Necessidade líquida de {necessidade:.2f} un. sem elo doador com excedente na rede — "
            "compra externa ao fornecedor cadastrado."
        )
        ordem = OrdemCompra(
            sku_id=sku.id,
            fornecedor_id=sku.fornecedor_id,
            destino_cd_id=elo_destino.cd_id,
            destino_filial_id=elo_destino.filial_id,
            quantidade=necessidade,
            data_solicitacao=hoje,
            data_previsao=hoje + timedelta(days=lead_time),
            status=StatusOrdem.SUGERIDA,
            score_criticidade=score_criticidade,
            justificativa=justificativa,
        )

    db.add(ordem)
    await db.flush()
    return ordem, justificativa
