"""Domínio Forecast (roadmap seções 4.6, 7, 8): séries históricas,
projeções, ajustes manuais (Influenciar Projeção) e classificação de itens
(Curva ABC/PQR, coeficiente de variação).

Segue o mesmo padrão de "elo" do domínio Estoque: cd_id/filial_id nuláveis,
exatamente um preenchido.
"""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, UUIDPkMixin

_ELO_CHECK = (
    "(cd_id IS NOT NULL AND filial_id IS NULL) OR "
    "(cd_id IS NULL AND filial_id IS NOT NULL)"
)


class EscopoAjuste(str, enum.Enum):
    ITEM = "ITEM"
    FORNECEDOR = "FORNECEDOR"


class CurvaAbc(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class CurvaPqr(str, enum.Enum):
    P = "P"
    Q = "Q"
    R = "R"


class HistoricoVendas(UUIDPkMixin, TimestampMixin, Base):
    """Série histórica de vendas por SKU/elo — entrada dos modelos de
    forecast (roadmap seção 7)."""

    __tablename__ = "historico_vendas"
    __table_args__ = (CheckConstraint(_ELO_CHECK, name="ck_historico_vendas_elo"),)

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False
    )
    cd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )
    filial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id")
    )
    data: Mapped[date] = mapped_column(Date, nullable=False)
    quantidade: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)

    sku: Mapped["Sku"] = relationship()  # noqa: F821


class Projecao(UUIDPkMixin, TimestampMixin, Base):
    """Demanda projetada por SKU/elo, gerada pelo motor de Forecast
    (roadmap seção 6.1) — consumida diretamente pelo Motor DRP (Fase 3)."""

    __tablename__ = "projecoes"
    __table_args__ = (CheckConstraint(_ELO_CHECK, name="ck_projecoes_elo"),)

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False
    )
    cd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )
    filial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id")
    )
    horizonte_dias: Mapped[int] = mapped_column(nullable=False)
    quantidade_projetada: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    modelo_utilizado: Mapped[str] = mapped_column(String(50))
    ajuste_aplicado_pct: Mapped[float | None] = mapped_column(Numeric(6, 2))
    sku_similar_utilizado_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id")
    )
    gerado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    sku: Mapped["Sku"] = relationship(foreign_keys=[sku_id])  # noqa: F821


class AjusteProjecao(UUIDPkMixin, TimestampMixin, Base):
    """Ajuste manual de projeção — "Influenciar Projeção" (roadmap seção
    4.6): percentual aplicado por período, com data limite e escopo."""

    __tablename__ = "ajustes_projecao"

    sku_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id")
    )
    fornecedor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fornecedores.id")
    )
    escopo: Mapped[EscopoAjuste] = mapped_column(Enum(EscopoAjuste, name="escopo_ajuste"))
    percentual: Mapped[float] = mapped_column(Numeric(6, 2), nullable=False)
    data_limite: Mapped[date] = mapped_column(Date, nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True)
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id")
    )


class ClassificacaoItem(UUIDPkMixin, TimestampMixin, Base):
    """Classificação de item — Curva ABC (valor), Curva PQR (frequência de
    saída) e coeficiente de variação da demanda (roadmap seção 7)."""

    __tablename__ = "classificacoes_item"

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False
    )
    curva_abc: Mapped[CurvaAbc] = mapped_column(Enum(CurvaAbc, name="curva_abc"))
    curva_pqr: Mapped[CurvaPqr] = mapped_column(Enum(CurvaPqr, name="curva_pqr"))
    coeficiente_variacao: Mapped[float | None] = mapped_column(Numeric(8, 4))
    calculado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    sku: Mapped["Sku"] = relationship()  # noqa: F821
