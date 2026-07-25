"""Domínio Segurança (roadmap seção 8): perfis de acesso e permissões por
Grupo de Compras e Filial."""

import uuid

from sqlalchemy import Boolean, ForeignKey, String, Table, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin, UUIDPkMixin

perfil_permissao = Table(
    "perfis_permissoes",
    Base.metadata,
    Column("perfil_id", UUID(as_uuid=True), ForeignKey("perfis_acesso.id"), primary_key=True),
    Column("permissao_id", UUID(as_uuid=True), ForeignKey("permissoes.id"), primary_key=True),
)


class Permissao(UUIDPkMixin, TimestampMixin, Base):
    """Permissão granular (ex.: `sku:write`, `ordem_compra:aprovar`)."""

    __tablename__ = "permissoes"

    codigo: Mapped[str] = mapped_column(String(100), unique=True)
    descricao: Mapped[str | None] = mapped_column(String(300))


class PerfilAcesso(UUIDPkMixin, TimestampMixin, Base):
    """Perfil de acesso, escopado por Grupo de Compras e/ou Filial."""

    __tablename__ = "perfis_acesso"

    nome: Mapped[str] = mapped_column(String(100), unique=True)
    grupo_compras_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grupos_compras.id")
    )
    filial_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("filiais.id")
    )

    permissoes: Mapped[list[Permissao]] = relationship(secondary=perfil_permissao)


class Usuario(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "usuarios"

    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True)
    perfil_acesso_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("perfis_acesso.id")
    )

    perfil_acesso: Mapped[PerfilAcesso | None] = relationship()
