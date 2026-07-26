"""Simulação de cenários what-if (roadmap seção 6.5/9, issue #32): parte
do estado real (oferta/demanda/rotas de `coletar_dados_sku`) e aplica
sobreposições hipotéticas antes de rodar o mesmo otimizador da issue #30 —
nada é persistido no banco."""

import uuid
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.optimization.lp import CUSTO_COMPRA_EXTERNA_PADRAO, ResultadoOtimizacao, otimizar_transferencias
from app.optimization.service import coletar_dados_sku


@dataclass
class CenarioHipotetico:
    ofertas_override: dict[str, float] | None = None
    """Substitui (não soma) a oferta de elos específicos — chave é
    `CD:<uuid>` ou `FILIAL:<uuid>` (ver `optimization.grafo.chave_elo`)."""
    demandas_override: dict[str, float] | None = None
    rotas_desativadas: list[str] | None = None
    """Ids de Rota (string) a excluir da simulação — ex.: simular a rota
    fora do ar."""
    custo_compra_externa: float = CUSTO_COMPRA_EXTERNA_PADRAO


async def simular_cenario(
    db: AsyncSession, sku_id: uuid.UUID, cenario: CenarioHipotetico
) -> ResultadoOtimizacao:
    ofertas, demandas, rotas = await coletar_dados_sku(db, sku_id)

    if cenario.ofertas_override:
        ofertas = {**ofertas, **cenario.ofertas_override}
    if cenario.demandas_override:
        demandas = {**demandas, **cenario.demandas_override}
    if cenario.rotas_desativadas:
        rotas = [r for r in rotas if r.id not in cenario.rotas_desativadas]

    return otimizar_transferencias(ofertas, demandas, rotas, custo_compra_externa=cenario.custo_compra_externa)
