import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.auditoria import TipoAutor
from app.models.drp import StatusOrdem, StatusRuptura


class RecalcularRequest(BaseModel):
    sku_id: uuid.UUID
    cd_id: uuid.UUID | None = None
    filial_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def _validar_elo(self) -> "RecalcularRequest":
        if (self.cd_id is None) == (self.filial_id is None):
            raise ValueError("Informe exatamente um elo: cd_id OU filial_id")
        return self


class StatusEstoqueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sku_id: uuid.UUID
    cd_id: uuid.UUID | None
    filial_id: uuid.UUID | None
    necessidade_liquida: float
    status: StatusRuptura
    calculado_em: datetime


class OrdemTransferenciaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sku_id: uuid.UUID
    origem_cd_id: uuid.UUID | None
    origem_filial_id: uuid.UUID | None
    destino_cd_id: uuid.UUID | None
    destino_filial_id: uuid.UUID | None
    quantidade: float
    data_embarque_sugerida: date
    data_chegada_estimada: date
    status: StatusOrdem
    score_criticidade: float
    justificativa: str


class OrdemCompraRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sku_id: uuid.UUID
    fornecedor_id: uuid.UUID
    destino_cd_id: uuid.UUID | None
    destino_filial_id: uuid.UUID | None
    quantidade: float
    data_solicitacao: date
    data_previsao: date
    status: StatusOrdem
    score_criticidade: float
    justificativa: str


class RecalcularResponse(BaseModel):
    status_estoque: StatusEstoqueRead
    ordem_transferencia: OrdemTransferenciaRead | None
    ordem_compra: OrdemCompraRead | None
    silenciado_motivo: str | None


class AtualizarStatusOrdemRequest(BaseModel):
    status: StatusOrdem


class MotivoSilenciamentoCreate(BaseModel):
    sku_id: uuid.UUID
    motivo: str
    escopo: str
    data_inicio: date
    data_fim: date | None = None
    usuario_id: uuid.UUID | None = None


class MotivoSilenciamentoRead(MotivoSilenciamentoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class LogDecisaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entidade: str
    entidade_id: uuid.UUID
    acao: str
    motivo: str | None
    tipo_autor: TipoAutor
