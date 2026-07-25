"""Domínio Cadastro (roadmap seção 8): SKU, Fornecedor, Comprador, Grupo de
Compras, Segmento, Departamento, Filial, CD.
"""

import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, UUIDPkMixin


class CustoAquisicao(str, enum.Enum):
    ELEVADO = "ELEVADO"
    INTERMEDIARIO = "INTERMEDIARIO"
    BAIXO = "BAIXO"


class CriticidadeResultado(str, enum.Enum):
    VITAL = "VITAL"
    INTERMEDIARIO = "INTERMEDIARIO"
    ORDINARIO = "ORDINARIO"


class Comprabilidade(str, enum.Enum):
    COMPLEXO = "COMPLEXO"
    DIFICIL = "DIFICIL"
    PREVISIVEL = "PREVISIVEL"


class FrequenciaSaida(str, enum.Enum):
    POPULAR = "POPULAR"
    INTERMEDIARIA = "INTERMEDIARIA"
    RARO = "RARO"


class DataLimitePedido(str, enum.Enum):
    NENHUM = "NENHUM"
    INICIO_MES = "INICIO_MES"
    QUINZENAL = "QUINZENAL"
    FIM_MES = "FIM_MES"
    OUTRO = "OUTRO"


class Segmento(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "segmentos"

    nome: Mapped[str] = mapped_column(String(120), unique=True)


class Departamento(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "departamentos"

    nome: Mapped[str] = mapped_column(String(120), unique=True)


class GrupoCompras(UUIDPkMixin, TimestampMixin, Base):
    """Agrupamento lógico de fornecedores/filiais para análise e compra
    conjunta (roadmap seção 4.2)."""

    __tablename__ = "grupos_compras"

    nome: Mapped[str] = mapped_column(String(120), unique=True)
    descricao: Mapped[str | None] = mapped_column(String(500))


class CentroDistribuicao(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "centros_distribuicao"

    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nome: Mapped[str] = mapped_column(String(120))

    filiais: Mapped[list["Filial"]] = relationship(back_populates="cd_supridor")


class Filial(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "filiais"

    codigo: Mapped[str] = mapped_column(String(20), unique=True)
    nome: Mapped[str] = mapped_column(String(120))
    cd_supridor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )

    cd_supridor: Mapped[CentroDistribuicao | None] = relationship(
        back_populates="filiais"
    )


class Fornecedor(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "fornecedores"

    razao_social: Mapped[str] = mapped_column(String(200))
    nome_fantasia: Mapped[str | None] = mapped_column(String(200))
    cnpj: Mapped[str] = mapped_column(String(20), unique=True)
    grupo_compras_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos_compras.id")
    )

    # Configuração do Fornecedor (roadmap seção 4.8)
    previsao_gatilho_dias: Mapped[int | None] = mapped_column()
    pedido_minimo_valor: Mapped[float | None] = mapped_column(Numeric(14, 2))
    data_limite_pedido: Mapped[DataLimitePedido] = mapped_column(
        Enum(DataLimitePedido, name="data_limite_pedido"),
        default=DataLimitePedido.NENHUM,
    )
    cobertura_estoque_manual_habilitada: Mapped[bool] = mapped_column(
        Boolean, default=False
    )

    grupo_compras: Mapped[GrupoCompras | None] = relationship()


class Comprador(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "compradores"

    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True)


class Sku(UUIDPkMixin, TimestampMixin, Base):
    """Ficha completa de produto (roadmap seção 4.6) — núcleo de dados
    consumido pelos motores de Forecast e DRP."""

    __tablename__ = "skus"

    codigo: Mapped[str] = mapped_column(String(50), unique=True)
    descricao: Mapped[str] = mapped_column(String(300))
    unidade_medida: Mapped[str] = mapped_column(String(10), default="UN")
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    fornecedor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fornecedores.id")
    )
    departamento_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departamentos.id")
    )
    segmento_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("segmentos.id")
    )
    comprador_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("compradores.id")
    )
    sku_similar_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id")
    )

    # Classificações (roadmap seção 4.6)
    custo_aquisicao: Mapped[CustoAquisicao | None] = mapped_column(
        Enum(CustoAquisicao, name="custo_aquisicao")
    )
    criticidade_resultado: Mapped[CriticidadeResultado | None] = mapped_column(
        Enum(CriticidadeResultado, name="criticidade_resultado")
    )
    comprabilidade: Mapped[Comprabilidade | None] = mapped_column(
        Enum(Comprabilidade, name="comprabilidade")
    )
    frequencia_saida: Mapped[FrequenciaSaida | None] = mapped_column(
        Enum(FrequenciaSaida, name="frequencia_saida")
    )
    perfil_demanda: Mapped[str | None] = mapped_column(String(50))

    # Parâmetros de reposição (roadmap seção 4.6)
    lead_time_dias: Mapped[int | None] = mapped_column()
    estoque_seguranca: Mapped[float | None] = mapped_column(Numeric(14, 3))
    ponto_pedido: Mapped[float | None] = mapped_column(Numeric(14, 3))
    estoque_maximo: Mapped[float | None] = mapped_column(Numeric(14, 3))
    cobertura_estoque_manual_dias: Mapped[float | None] = mapped_column(
        Numeric(10, 2)
    )

    fornecedor: Mapped[Fornecedor | None] = relationship()
    departamento: Mapped[Departamento | None] = relationship()
    segmento: Mapped[Segmento | None] = relationship()
    comprador: Mapped[Comprador | None] = relationship()
    sku_similar: Mapped["Sku | None"] = relationship(remote_side="Sku.id")
