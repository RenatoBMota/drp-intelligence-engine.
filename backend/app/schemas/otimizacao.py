import uuid

from pydantic import BaseModel

from app.optimization.lp import CUSTO_COMPRA_EXTERNA_PADRAO


class OtimizarSkuRequest(BaseModel):
    custo_compra_externa: float = CUSTO_COMPRA_EXTERNA_PADRAO


class SimularCenarioRequest(BaseModel):
    ofertas_override: dict[str, float] | None = None
    demandas_override: dict[str, float] | None = None
    rotas_desativadas: list[str] | None = None
    custo_compra_externa: float = CUSTO_COMPRA_EXTERNA_PADRAO


class FluxoAlocadoRead(BaseModel):
    origem: str
    destino: str
    quantidade: float
    custo_unitario: float


class ResultadoOtimizacaoRead(BaseModel):
    sucesso: bool
    fluxos: list[FluxoAlocadoRead]
    custo_total: float
    quantidade_via_rede: float
    quantidade_via_compra_externa: float
    mensagem: str


class ItemPrioridadeRead(BaseModel):
    severidade: str
    mensagem: str
