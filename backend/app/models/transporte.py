"""Domínio Transporte (roadmap seção 8): rotas, lead time por rota,
capacidade — a Fase 3 usava uma constante fixa de lead time de
transferência porque este domínio ainda não existia; a Fase 4 (otimização
de rede) é o motivo real de modelá-lo agora."""

import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import TimestampMixin, UUIDPkMixin

_ELO_CHECK = "({prefix}cd_id IS NOT NULL AND {prefix}filial_id IS NULL) OR ({prefix}cd_id IS NULL AND {prefix}filial_id IS NOT NULL)"


class Rota(UUIDPkMixin, TimestampMixin, Base):
    """Rota de transporte entre dois elos da rede, com capacidade e custo
    — usada pela otimização de rede (issue #30) e pela modelagem em grafo
    (issue #31)."""

    __tablename__ = "rotas"
    __table_args__ = (
        CheckConstraint(_ELO_CHECK.format(prefix="origem_"), name="ck_rota_origem"),
        CheckConstraint(_ELO_CHECK.format(prefix="destino_"), name="ck_rota_destino"),
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
    capacidade_maxima: Mapped[float] = mapped_column(Numeric(14, 3), nullable=False)
    custo_unitario: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False)
    lead_time_dias: Mapped[int] = mapped_column(nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, default=True)
