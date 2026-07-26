"""Liga o otimizador LP (lp.py) aos dados reais do banco: saldo/necessidade
por elo e rotas cadastradas, para um SKU específico."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.snapshots import ultimos_snapshots
from app.models.cadastro import Sku
from app.models.estoque import SaldoEstoque
from app.models.transporte import Rota
from app.optimization.grafo import chave_elo
from app.optimization.lp import (
    CUSTO_COMPRA_EXTERNA_PADRAO,
    ResultadoOtimizacao,
    RotaDisponivel,
    otimizar_transferencias,
)


async def _rotas_disponiveis(db: AsyncSession) -> list[RotaDisponivel]:
    result = await db.execute(select(Rota).where(Rota.ativa.is_(True)))
    rotas = []
    for rota in result.scalars().all():
        origem = chave_elo(rota.origem_cd_id, rota.origem_filial_id)
        destino = chave_elo(rota.destino_cd_id, rota.destino_filial_id)
        rotas.append(
            RotaDisponivel(
                origem=origem, destino=destino,
                capacidade=float(rota.capacidade_maxima), custo_unitario=float(rota.custo_unitario),
                id=str(rota.id),
            )
        )
    return rotas


async def coletar_dados_sku(
    db: AsyncSession, sku_id: uuid.UUID
) -> tuple[dict[str, float], dict[str, float], list[RotaDisponivel]]:
    """Estado real atual (oferta/demanda/rotas) para um SKU — usado tanto
    pela otimização (issue #30) quanto como ponto de partida da simulação
    de cenários (issue #32)."""
    sku = await db.get(Sku, sku_id)
    if sku is None:
        raise ValueError(f"SKU {sku_id} não encontrado")

    saldos = (await db.execute(select(SaldoEstoque).where(SaldoEstoque.sku_id == sku_id))).scalars().all()
    ponto_pedido = float(sku.ponto_pedido or 0)
    ofertas = {}
    for saldo in saldos:
        excedente = float(saldo.quantidade) - ponto_pedido
        if excedente > 0:
            ofertas[chave_elo(saldo.cd_id, saldo.filial_id)] = excedente

    snapshots = [s for s in await ultimos_snapshots(db) if s.sku_id == sku_id]
    demandas = {
        chave_elo(s.cd_id, s.filial_id): float(s.necessidade_liquida)
        for s in snapshots
        if s.necessidade_liquida > 0
    }

    rotas = await _rotas_disponiveis(db)
    return ofertas, demandas, rotas


async def otimizar_sku(
    db: AsyncSession, sku_id: uuid.UUID, custo_compra_externa: float = CUSTO_COMPRA_EXTERNA_PADRAO
) -> ResultadoOtimizacao:
    ofertas, demandas, rotas = await coletar_dados_sku(db, sku_id)
    return otimizar_transferencias(ofertas, demandas, rotas, custo_compra_externa=custo_compra_externa)
