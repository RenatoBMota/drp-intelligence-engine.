"""Relatórios herdados do benchmark Systock (roadmap seção 10.3, issue
#37). Não cobertos aqui, por dependerem de dado que a Fase 1 não modelou:
- **Saving de Compras**: precisa de preço/custo unitário do SKU.
- **Oportunidade de Vendas**: não tem definição objetiva no roadmap além
  do nome — precisaria de uma regra de negócio mais específica.
"""

import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.snapshots import ultimos_snapshots
from app.models.cadastro import Sku
from app.models.drp import OrdemCompra, OrdemTransferencia, StatusOrdem, StatusRuptura
from app.models.estoque import SaldoEstoque
from app.models.forecast import ClassificacaoItem, HistoricoVendas, Projecao


async def ruptura_geral(db: AsyncSession) -> dict[str, int]:
    """Contagem de elos por status — visão geral de ruptura da rede."""
    snapshots = await ultimos_snapshots(db)
    return dict(Counter(s.status.value for s in snapshots))


async def excesso_estoque(db: AsyncSession):
    snapshots = await ultimos_snapshots(db)
    return [s for s in snapshots if s.status == StatusRuptura.EXCESSO]


async def movimentacao_produtos(db: AsyncSession, dias: int = 90) -> list[dict]:
    """Análise de Vendas / Movimentação de Produtos: quantidade total
    vendida por SKU nos últimos `dias` dias."""
    desde = date.today() - timedelta(days=dias)
    stmt = select(HistoricoVendas.sku_id, HistoricoVendas.quantidade).where(HistoricoVendas.data >= desde)
    result = await db.execute(stmt)

    totais: dict[uuid.UUID, float] = defaultdict(float)
    for sku_id, quantidade in result.all():
        totais[sku_id] += float(quantidade)

    return [{"sku_id": str(sku_id), "quantidade_vendida": qtd} for sku_id, qtd in totais.items()]


async def curva_abc_pqr(db: AsyncSession) -> list[ClassificacaoItem]:
    """Última classificação ABC/PQR calculada por SKU (reaproveita a
    Fase 2 — issue #19 — não recalcula)."""
    stmt = select(ClassificacaoItem).order_by(ClassificacaoItem.calculado_em.desc())
    result = await db.execute(stmt)

    vistos: set[uuid.UUID] = set()
    ultimos: list[ClassificacaoItem] = []
    for item in result.scalars().all():
        if item.sku_id in vistos:
            continue
        vistos.add(item.sku_id)
        ultimos.append(item)
    return ultimos


async def sugestao_inativacao(db: AsyncSession, dias: int = 90) -> list[Sku]:
    from app.analytics.indicadores import no_moving

    return await no_moving(db, dias=dias)


@dataclass
class CoberturaEstoqueItem:
    sku_id: uuid.UUID
    cd_id: uuid.UUID | None
    filial_id: uuid.UUID | None
    saldo: float
    cobertura_dias: float | None


async def cobertura_estoque(db: AsyncSession) -> list[CoberturaEstoqueItem]:
    """Cobertura de estoque (roadmap seção 10.3) a partir do saldo atual e
    da projeção mais recente já calculada — não dispara novo forecast
    (relatório é leitura, não deve ter efeito colateral de escrita)."""
    saldos = (await db.execute(select(SaldoEstoque))).scalars().all()

    projecoes = (await db.execute(select(Projecao).order_by(Projecao.gerado_em.desc()))).scalars().all()
    projecao_por_elo: dict[tuple[uuid.UUID, uuid.UUID | None, uuid.UUID | None], Projecao] = {}
    for projecao in projecoes:
        chave = (projecao.sku_id, projecao.cd_id, projecao.filial_id)
        if chave not in projecao_por_elo:
            projecao_por_elo[chave] = projecao

    itens = []
    for saldo in saldos:
        chave = (saldo.sku_id, saldo.cd_id, saldo.filial_id)
        projecao = projecao_por_elo.get(chave)
        cobertura = None
        if projecao is not None and projecao.quantidade_projetada > 0:
            demanda_diaria = float(projecao.quantidade_projetada) / projecao.horizonte_dias
            cobertura = float(saldo.quantidade) / demanda_diaria if demanda_diaria > 0 else None
        itens.append(
            CoberturaEstoqueItem(
                sku_id=saldo.sku_id,
                cd_id=saldo.cd_id,
                filial_id=saldo.filial_id,
                saldo=float(saldo.quantidade),
                cobertura_dias=cobertura,
            )
        )
    return itens


async def pedidos_pendentes(db: AsyncSession) -> dict[str, list]:
    transferencias = (
        await db.execute(
            select(OrdemTransferencia).where(
                OrdemTransferencia.status.notin_([StatusOrdem.CONCLUIDA, StatusOrdem.CANCELADA])
            )
        )
    ).scalars().all()
    compras = (
        await db.execute(
            select(OrdemCompra).where(OrdemCompra.status.notin_([StatusOrdem.CONCLUIDA, StatusOrdem.CANCELADA]))
        )
    ).scalars().all()
    return {"transferencias": list(transferencias), "compras": list(compras)}


@dataclass
class IndicadorOtif:
    n_ordens_concluidas: int
    n_no_prazo: int
    otif: float | None


async def indicador_otif(db: AsyncSession) -> IndicadorOtif:
    """OTIF simplificado (roadmap seção 10.3): % de ordens concluídas
    dentro do prazo planejado. "In Full" é assumido verdadeiro para toda
    ordem concluída — o modelo de Ordem não guarda quantidade efetivamente
    recebida separada da solicitada, então não dá pra medir entrega
    parcial ainda; é só o "On Time" da sigla, de fato."""
    transferencias = (
        await db.execute(
            select(OrdemTransferencia).where(
                OrdemTransferencia.status == StatusOrdem.CONCLUIDA,
                OrdemTransferencia.data_conclusao.is_not(None),
            )
        )
    ).scalars().all()
    compras = (
        await db.execute(
            select(OrdemCompra).where(
                OrdemCompra.status == StatusOrdem.CONCLUIDA,
                OrdemCompra.data_conclusao.is_not(None),
            )
        )
    ).scalars().all()

    total = len(transferencias) + len(compras)
    if total == 0:
        return IndicadorOtif(0, 0, None)

    no_prazo = sum(1 for o in transferencias if o.data_conclusao <= o.data_chegada_estimada)
    no_prazo += sum(1 for o in compras if o.data_conclusao <= o.data_previsao)

    return IndicadorOtif(n_ordens_concluidas=total, n_no_prazo=no_prazo, otif=no_prazo / total)
