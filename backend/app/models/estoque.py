"""Domínio Estoque (roadmap seção 8): saldo por elo, estoque em trânsito,
estoque bloqueado/reservado/avaria.

Um "elo" da rede é um CD ou uma Filial (roadmap seção 3). Cada tabela deste
domínio referencia o elo por duas FKs nulláveis (cd_id / filial_id), das
quais exatamente uma deve estar preenchida.
"""

import enum
import uuid
from datetime import date

from sqlalchemy import CheckConstraint, Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, UUIDPkMixin

_ELO_CHECK = (
    "(cd_id IS NOT NULL AND filial_id IS NULL) OR "
    "(cd_id IS NULL AND filial_id IS NOT NULL)"
)


class TipoBloqueio(str, enum.Enum):
    BLOQUEADO = "BLOQUEADO"
    RESERVADO = "RESERVADO"
    AVARIA = "AVARIA"


class SaldoEstoque(UUIDPkMixin, TimestampMixin, Base):
    """Saldo de estoque disponível de um SKU em um elo (CD ou Filial)."""

    __tablename__ = "saldos_estoque"
    __table_args__ = (
        CheckConstraint(_ELO_CHECK, name="ck_saldo_estoque_elo"),
    )

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False
    )
    cd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )
    filial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id")
    )
    quantidade: Mapped[float] = mapped_column(Numeric(14, 3), default=0)

    sku: Mapped["Sku"] = relationship()  # noqa: F821


class EstoqueTransito(UUIDPkMixin, TimestampMixin, Base):
    """Estoque em trânsito: pedidos a fornecedor ou transferências internas
    já emitidas, ainda não recebidos no elo de destino."""

    __tablename__ = "estoques_transito"

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False
    )
    origem_fornecedor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fornecedores.id")
    )
    origem_cd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )
    destino_cd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )
    destino_filial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id")
    )
    quantidade_solicitada: Mapped[float] = mapped_column(Numeric(14, 3))
    quantidade_recebida: Mapped[float] = mapped_column(Numeric(14, 3), default=0)
    data_previsao_chegada: Mapped[date | None] = mapped_column(Date)

    sku: Mapped["Sku"] = relationship()  # noqa: F821


class EstoqueBloqueado(UUIDPkMixin, TimestampMixin, Base):
    """Estoque bloqueado, reservado ou avariado — não disponível para venda
    nem para cálculo de necessidade líquida."""

    __tablename__ = "estoques_bloqueados"
    __table_args__ = (
        CheckConstraint(_ELO_CHECK, name="ck_estoque_bloqueado_elo"),
    )

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False
    )
    cd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )
    filial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id")
    )
    tipo: Mapped[TipoBloqueio] = mapped_column(Enum(TipoBloqueio, name="tipo_bloqueio"))
    quantidade: Mapped[float] = mapped_column(Numeric(14, 3))
    motivo: Mapped[str | None] = mapped_column(String(300))

    sku: Mapped["Sku"] = relationship()  # noqa: F821
