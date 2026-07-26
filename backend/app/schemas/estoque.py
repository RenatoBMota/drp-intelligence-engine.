import uuid

from pydantic import BaseModel, ConfigDict, model_validator


class SaldoEstoqueSet(BaseModel):
    sku_id: uuid.UUID
    cd_id: uuid.UUID | None = None
    filial_id: uuid.UUID | None = None
    quantidade: float

    @model_validator(mode="after")
    def _validar_elo(self) -> "SaldoEstoqueSet":
        if (self.cd_id is None) == (self.filial_id is None):
            raise ValueError("Informe exatamente um elo: cd_id OU filial_id")
        return self


class SaldoEstoqueRead(SaldoEstoqueSet):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
