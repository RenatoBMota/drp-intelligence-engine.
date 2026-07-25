import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.forecast import CurvaAbc, CurvaPqr, EscopoAjuste


class HistoricoVendasCreate(BaseModel):
    sku_id: uuid.UUID
    cd_id: uuid.UUID | None = None
    filial_id: uuid.UUID | None = None
    data: date
    quantidade: float

    @model_validator(mode="after")
    def _validar_elo(self) -> "HistoricoVendasCreate":
        if (self.cd_id is None) == (self.filial_id is None):
            raise ValueError("Informe exatamente um elo: cd_id OU filial_id")
        return self


class HistoricoVendasRead(HistoricoVendasCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class ProjecaoGerarRequest(BaseModel):
    sku_id: uuid.UUID
    horizonte_dias: int
    cd_id: uuid.UUID | None = None
    filial_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def _validar_elo(self) -> "ProjecaoGerarRequest":
        if (self.cd_id is None) == (self.filial_id is None):
            raise ValueError("Informe exatamente um elo: cd_id OU filial_id")
        return self


class ProjecaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sku_id: uuid.UUID
    cd_id: uuid.UUID | None
    filial_id: uuid.UUID | None
    horizonte_dias: int
    quantidade_projetada: float
    modelo_utilizado: str
    ajuste_aplicado_pct: float | None
    sku_similar_utilizado_id: uuid.UUID | None
    gerado_em: datetime


class AjusteProjecaoCreate(BaseModel):
    escopo: EscopoAjuste
    percentual: float
    data_limite: date
    sku_id: uuid.UUID | None = None
    fornecedor_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def _validar_escopo(self) -> "AjusteProjecaoCreate":
        if self.escopo == EscopoAjuste.ITEM and self.sku_id is None:
            raise ValueError("escopo ITEM exige sku_id")
        if self.escopo == EscopoAjuste.FORNECEDOR and self.fornecedor_id is None:
            raise ValueError("escopo FORNECEDOR exige fornecedor_id")
        return self


class AjusteProjecaoRead(AjusteProjecaoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ativo: bool


class ClassificacaoItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sku_id: uuid.UUID
    curva_abc: CurvaAbc
    curva_pqr: CurvaPqr
    coeficiente_variacao: float | None
    calculado_em: datetime


class EstoqueSegurancaEstatisticoRequest(BaseModel):
    nivel_servico: float
    desvio_padrao_demanda: float
    lead_time_dias: float


class EstoqueSegurancaMonteCarloRequest(BaseModel):
    sku_id: uuid.UUID
    lead_time_dias: int
    nivel_servico: float
    cd_id: uuid.UUID | None = None
    filial_id: uuid.UUID | None = None
    n_simulacoes: int = 10_000

    @model_validator(mode="after")
    def _validar_elo(self) -> "EstoqueSegurancaMonteCarloRequest":
        if (self.cd_id is None) == (self.filial_id is None):
            raise ValueError("Informe exatamente um elo: cd_id OU filial_id")
        return self


class EstoqueSegurancaResponse(BaseModel):
    estoque_seguranca: float
    n_pontos_historico: int | None = None
