"""Indicadores herdados do benchmark Systock (roadmap seção 10.2, issue
#36): Status Mensal, No Moving, Status Produto, Perda de Venda x Ruptura,
Percepção de Compras (Análise por Compradores, seção 4.9)."""

import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.snapshots import ultimos_snapshots
from app.models.cadastro import Sku
from app.models.drp import OrdemCompra, StatusEstoqueSnapshot, StatusRuptura
from app.models.forecast import HistoricoVendas

_STATUS_RUPTURA = {
    StatusRuptura.RUPTURA,
    StatusRuptura.RUPTURA_DRP,
    StatusRuptura.ELEVADA_EXPOSICAO_RUPTURA,
}


async def status_mensal(db: AsyncSession) -> list[dict]:
    """Distribuição de status por mês de cálculo — todo o histórico de
    StatusEstoqueSnapshot, não só o mais recente (para ver a evolução)."""
    result = await db.execute(select(StatusEstoqueSnapshot))
    contagem: dict[tuple[str, str], int] = defaultdict(int)
    for snapshot in result.scalars().all():
        mes = snapshot.calculado_em.strftime("%Y-%m")
        contagem[(mes, snapshot.status.value)] += 1
    return [
        {"mes": mes, "status": status, "quantidade": qtd}
        for (mes, status), qtd in sorted(contagem.items())
    ]


async def no_moving(db: AsyncSession, dias: int = 90) -> list[Sku]:
    """SKUs ativos sem nenhuma venda registrada nos últimos `dias` dias —
    candidatos a saneamento/inativação (roadmap seções 4.11 e 11)."""
    desde = date.today() - timedelta(days=dias)

    skus_ativos = (await db.execute(select(Sku).where(Sku.ativo.is_(True)))).scalars().all()
    com_venda = (
        (await db.execute(select(HistoricoVendas.sku_id).where(HistoricoVendas.data >= desde)))
        .scalars()
        .all()
    )
    ids_com_venda = set(com_venda)
    return [sku for sku in skus_ativos if sku.id not in ids_com_venda]


async def status_produto(db: AsyncSession, sku_id: uuid.UUID | None = None) -> list:
    """Status atual (snapshot mais recente) por SKU/elo."""
    snapshots = await ultimos_snapshots(db)
    if sku_id is not None:
        snapshots = [s for s in snapshots if s.sku_id == sku_id]
    return snapshots


@dataclass
class PerdaVendaRuptura:
    necessidade_nao_atendida_total: float
    n_elos_em_ruptura: int


async def perda_venda_ruptura(db: AsyncSession) -> PerdaVendaRuptura:
    """Proxy de perda de venda por ruptura (roadmap seção 10.2): soma da
    necessidade líquida não atendida nos elos em algum grau de ruptura.
    É uma proxy em **unidades**, não em R$ — a Fase 1 não modelou preço de
    venda do SKU, então não dá para converter em perda financeira ainda."""
    snapshots = await ultimos_snapshots(db)
    em_ruptura = [s for s in snapshots if s.status in _STATUS_RUPTURA]
    total = sum(max(float(s.necessidade_liquida), 0.0) for s in em_ruptura)
    return PerdaVendaRuptura(necessidade_nao_atendida_total=total, n_elos_em_ruptura=len(em_ruptura))


_CATEGORIA_POR_STATUS = {
    StatusRuptura.EXCESSO: "COMPRA_COM_ELEVADA_PREMATURIDADE",
    StatusRuptura.ADEQUADO: "COMPRA_COM_ELEVADA_PREMATURIDADE",
    StatusRuptura.BAIXA_EXPOSICAO_RUPTURA: "COMPRA_EM_PONTO_DE_PEDIDO",
    StatusRuptura.ELEVADA_EXPOSICAO_RUPTURA: "COMPRA_EM_EXPOSICAO_A_RUPTURA",
    StatusRuptura.RUPTURA_DRP: "COMPRA_EM_EXPOSICAO_A_RUPTURA",
    StatusRuptura.RUPTURA: "COMPRA_EM_RUPTURA",
}


async def analise_compradores(db: AsyncSession) -> dict[str, Counter]:
    """Percepção de Compras / Eficiência do Comprador (roadmap seção 4.9):
    classifica cada Ordem de Compra pelo status do elo no momento em que
    foi gerada, agrupado por comprador (`Sku.comprador_id`).

    Categorias: Primeira Compra, Compra com Elevada Prematuridade, Compra
    em Ponto de Pedido (o alvo), Compra em Exposição a Ruptura, Compra em
    Ruptura, Sem Comportamento (quando não há snapshot correspondente).
    """
    ordens = (
        (await db.execute(select(OrdemCompra).order_by(OrdemCompra.created_at)))
        .scalars()
        .all()
    )
    todos_snapshots = (await db.execute(select(StatusEstoqueSnapshot))).scalars().all()
    snapshots_por_sku = defaultdict(list)
    for snap in todos_snapshots:
        snapshots_por_sku[snap.sku_id].append(snap)

    skus = {sku.id: sku for sku in (await db.execute(select(Sku))).scalars().all()}

    resultado: dict[str, Counter] = defaultdict(Counter)
    skus_ja_compradas: set[uuid.UUID] = set()

    for ordem in ordens:
        sku_da_ordem = skus.get(ordem.sku_id)
        comprador_id = (
            str(sku_da_ordem.comprador_id)
            if sku_da_ordem is not None and sku_da_ordem.comprador_id is not None
            else "SEM_COMPRADOR"
        )

        if ordem.sku_id not in skus_ja_compradas:
            categoria = "PRIMEIRA_COMPRA"
        else:
            candidatos = [
                s for s in snapshots_por_sku.get(ordem.sku_id, [])
                if s.calculado_em <= ordem.created_at
            ]
            if not candidatos:
                categoria = "SEM_COMPORTAMENTO"
            else:
                snapshot_mais_proximo = max(candidatos, key=lambda s: s.calculado_em)
                categoria = _CATEGORIA_POR_STATUS.get(snapshot_mais_proximo.status, "SEM_COMPORTAMENTO")

        skus_ja_compradas.add(ordem.sku_id)
        resultado[comprador_id][categoria] += 1

    return resultado
