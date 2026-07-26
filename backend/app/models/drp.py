"""Domínio DRP — o núcleo do produto (roadmap seção 6): Ordens de
Transferência, Ordens de Compra e o snapshot de status de ruptura por
elo/SKU que alimenta a Torre de Controle (Fase 5).
"""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, UUIDPkMixin

_ELO_CHECK = "({prefix}cd_id IS NOT NULL AND {prefix}filial_id IS NULL) OR ({prefix}cd_id IS NULL AND {prefix}filial_id IS NOT NULL)"


class StatusRuptura(str, enum.Enum):
    EXCESSO = "EXCESSO"
    ADEQUADO = "ADEQUADO"
    BAIXA_EXPOSICAO_RUPTURA = "BAIXA_EXPOSICAO_RUPTURA"
    ELEVADA_EXPOSICAO_RUPTURA = "ELEVADA_EXPOSICAO_RUPTURA"
    RUPTURA = "RUPTURA"
    RUPTURA_DRP = "RUPTURA_DRP"


class StatusOrdem(str, enum.Enum):
    SUGERIDA = "SUGERIDA"
    APROVADA = "APROVADA"
    EM_TRANSITO = "EM_TRANSITO"
    CONCLUIDA = "CONCLUIDA"
    CANCELADA = "CANCELADA"


class OrdemTransferencia(UUIDPkMixin, TimestampMixin, Base):
    """Ordem de Transferência entre dois elos da mesma rede (roadmap seção
    6.6) — gerada quando existe elo doador com excedente capaz de suprir a
    necessidade líquida dentro da janela de tempo viável (seção 6.4)."""

    __tablename__ = "ordens_transferencia"
    __table_args__ = (
        CheckConstraint(_ELO_CHECK.format(prefix="origem_"), name="ck_ordem_transf_origem"),
        CheckConstraint(_ELO_CHECK.format(prefix="destino_"), name="ck_ordem_transf_destino"),
    )

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False
    )
    origem_cd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )
    origem_filial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id")
    )
    destino_cd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )
    destino_filial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id")
    )
    quantidade: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    data_embarque_sugerida: Mapped[date] = mapped_column(Date, nullable=False)
    data_chegada_estimada: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[StatusOrdem] = mapped_column(
        Enum(StatusOrdem, name="status_ordem_transferencia"), default=StatusOrdem.SUGERIDA
    )
    score_criticidade: Mapped[float] = mapped_column(Numeric(10, 4))
    justificativa: Mapped[str] = mapped_column(String(1000))
    data_conclusao: Mapped[date | None] = mapped_column(Date)
    """Preenchida quando o status muda para CONCLUIDA — base para OTIF e
    Lead Time Efetivo vs. planejado (roadmap seção 10.4, Fase 5)."""

    sku: Mapped["Sku"] = relationship()  # noqa: F821


class OrdemCompra(UUIDPkMixin, TimestampMixin, Base):
    """Ordem de Compra a fornecedor (roadmap seção 6.6) — gerada apenas
    depois de esgotada a opção de redistribuição interna (seção 6.4)."""

    __tablename__ = "ordens_compra"

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False
    )
    fornecedor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fornecedores.id"), nullable=False
    )
    destino_cd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )
    destino_filial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id")
    )
    quantidade: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    data_solicitacao: Mapped[date] = mapped_column(Date, nullable=False)
    data_previsao: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[StatusOrdem] = mapped_column(
        Enum(StatusOrdem, name="status_ordem_compra"), default=StatusOrdem.SUGERIDA
    )
    score_criticidade: Mapped[float] = mapped_column(Numeric(10, 4))
    justificativa: Mapped[str] = mapped_column(String(1000))
    data_conclusao: Mapped[date | None] = mapped_column(Date)

    sku: Mapped["Sku"] = relationship()  # noqa: F821


class StatusEstoqueSnapshot(UUIDPkMixin, TimestampMixin, Base):
    """Fotografia do status de ruptura/necessidade líquida de um SKU num
    elo, no momento do recálculo (roadmap seção 6.3) — histórico consumido
    pela Torre de Controle (Fase 5) e base para detectar desvios."""

    __tablename__ = "status_estoque_snapshots"
    __table_args__ = (CheckConstraint(_ELO_CHECK.format(prefix=""), name="ck_status_snapshot_elo"),)

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False
    )
    cd_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("centros_distribuicao.id")
    )
    filial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id")
    )
    necessidade_liquida: Mapped[float] = mapped_column(Numeric(14, 3))
    status: Mapped[StatusRuptura] = mapped_column(Enum(StatusRuptura, name="status_ruptura"))
    calculado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    sku: Mapped["Sku"] = relationship()  # noqa: F821
