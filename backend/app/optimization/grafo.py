"""Modelagem da rede como grafo dirigido e Fluxo de Rede (roadmap seção 7,
issue #31): nós são elos (CD ou Filial), arestas são Rotas ativas, com
peso = custo unitário e capacidade = capacidade máxima da rota."""

import uuid

import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transporte import Rota


def chave_elo(cd_id: uuid.UUID | None, filial_id: uuid.UUID | None) -> str:
    if cd_id is not None:
        return f"CD:{cd_id}"
    if filial_id is not None:
        return f"FILIAL:{filial_id}"
    raise ValueError("Elo precisa de cd_id ou filial_id")


async def construir_grafo(db: AsyncSession) -> nx.DiGraph:
    grafo = nx.DiGraph()
    result = await db.execute(select(Rota).where(Rota.ativa.is_(True)))
    for rota in result.scalars().all():
        origem = chave_elo(rota.origem_cd_id, rota.origem_filial_id)
        destino = chave_elo(rota.destino_cd_id, rota.destino_filial_id)
        grafo.add_edge(
            origem,
            destino,
            weight=float(rota.custo_unitario),
            capacity=float(rota.capacidade_maxima),
            lead_time_dias=rota.lead_time_dias,
            rota_id=str(rota.id),
        )
    return grafo


def caminho_mais_barato(grafo: nx.DiGraph, origem: str, destino: str) -> dict | None:
    """Menor custo de transporte entre dois elos, via Dijkstra (peso =
    custo_unitario da rota)."""
    try:
        caminho = nx.shortest_path(grafo, origem, destino, weight="weight")
        custo = nx.shortest_path_length(grafo, origem, destino, weight="weight")
    except (nx.NodeNotFound, nx.NetworkXNoPath):
        return None
    return {"caminho": caminho, "custo_total": custo}


def fluxo_maximo(grafo: nx.DiGraph, origem: str, destino: str) -> dict | None:
    """Quantidade máxima transportável entre dois elos respeitando a
    capacidade de cada rota no caminho (algoritmo de fluxo máximo)."""
    if origem not in grafo or destino not in grafo:
        return None
    try:
        valor, fluxo_por_aresta = nx.maximum_flow(grafo, origem, destino, capacity="capacity")
    except nx.NetworkXError:
        return None
    return {"fluxo_maximo": valor, "fluxo_por_aresta": fluxo_por_aresta}
