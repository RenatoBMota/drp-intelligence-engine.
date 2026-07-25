"""Domínio Auditoria (roadmap seções 8 e 11): log de decisões do motor,
motivos de silenciamento, ajustes manuais — sempre com autor, data e motivo.
"""

import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import TimestampMixin, UUIDPkMixin


class TipoAutor(str, enum.Enum):
    SISTEMA = "SISTEMA"
    USUARIO = "USUARIO"


class LogDecisao(UUIDPkMixin, TimestampMixin, Base):
    """Trilha de auditoria de decisões automáticas do motor DRP (transferência,
    compra, silenciamento) e de ajustes manuais — autor, data e motivo
    (roadmap seção 11)."""

    __tablename__ = "logs_decisao"

    entidade: Mapped[str] = mapped_column(String(50))
    entidade_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    acao: Mapped[str] = mapped_column(String(100))
    motivo: Mapped[str | None] = mapped_column(String(500))
    tipo_autor: Mapped[TipoAutor] = mapped_column(Enum(TipoAutor, name="tipo_autor"))
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id")
    )


class MotivoSilenciamento(UUIDPkMixin, TimestampMixin, Base):
    """Motivo de silenciamento de um SKU (roadmap seção 4.8): suprime
    sugestão de compra/transferência por um período, com motivo obrigatório
    e escopo."""

    __tablename__ = "motivos_silenciamento"

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skus.id"), nullable=False
    )
    motivo: Mapped[str] = mapped_column(String(500))
    escopo: Mapped[str] = mapped_column(String(50))
    data_inicio: Mapped[date] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)
    usuario_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id")
    )
