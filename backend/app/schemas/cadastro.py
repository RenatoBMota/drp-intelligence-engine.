import uuid

from pydantic import BaseModel, ConfigDict

from app.models.cadastro import (
    Comprabilidade,
    CriticidadeResultado,
    CustoAquisicao,
    FrequenciaSaida,
)


class CentroDistribuicaoCreate(BaseModel):
    codigo: str
    nome: str


class CentroDistribuicaoRead(CentroDistribuicaoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class FilialCreate(BaseModel):
    codigo: str
    nome: str
    cd_supridor_id: uuid.UUID | None = None


class FilialRead(FilialCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class FornecedorCreate(BaseModel):
    razao_social: str
    nome_fantasia: str | None = None
    cnpj: str
    grupo_compras_id: uuid.UUID | None = None
    previsao_gatilho_dias: int | None = None
    pedido_minimo_valor: float | None = None


class FornecedorRead(FornecedorCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


class SkuCreate(BaseModel):
    codigo: str
    descricao: str
    unidade_medida: str = "UN"
    fornecedor_id: uuid.UUID | None = None
    departamento_id: uuid.UUID | None = None
    segmento_id: uuid.UUID | None = None
    comprador_id: uuid.UUID | None = None
    sku_similar_id: uuid.UUID | None = None
    custo_aquisicao: CustoAquisicao | None = None
    criticidade_resultado: CriticidadeResultado | None = None
    comprabilidade: Comprabilidade | None = None
    frequencia_saida: FrequenciaSaida | None = None
    perfil_demanda: str | None = None
    lead_time_dias: int | None = None
    estoque_seguranca: float | None = None
    ponto_pedido: float | None = None
    estoque_maximo: float | None = None
    cobertura_estoque_manual_dias: float | None = None


class SkuRead(SkuCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ativo: bool
