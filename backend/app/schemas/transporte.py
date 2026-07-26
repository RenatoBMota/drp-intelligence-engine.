import uuid

from pydantic import BaseModel, ConfigDict, model_validator


class RotaCreate(BaseModel):
    origem_cd_id: uuid.UUID | None = None
    origem_filial_id: uuid.UUID | None = None
    destino_cd_id: uuid.UUID | None = None
    destino_filial_id: uuid.UUID | None = None
    capacidade_maxima: float
    custo_unitario: float
    lead_time_dias: int

    @model_validator(mode="after")
    def _validar_elos(self) -> "RotaCreate":
        if (self.origem_cd_id is None) == (self.origem_filial_id is None):
            raise ValueError("Origem precisa de exatamente um entre origem_cd_id/origem_filial_id")
        if (self.destino_cd_id is None) == (self.destino_filial_id is None):
            raise ValueError("Destino precisa de exatamente um entre destino_cd_id/destino_filial_id")
        return self


class RotaRead(RotaCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ativa: bool
