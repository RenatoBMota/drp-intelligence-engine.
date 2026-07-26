"""Endpoints do domínio Estoque — mínimos para permitir popular e consultar
saldo por elo, necessários para o Motor DRP (Fase 3) funcionar via API.
A Fase 1 modelou o domínio mas não expôs API; fica coberto aqui porque a
Fase 3 depende disso para ser operável (não só para teste)."""

from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.estoque import SaldoEstoque
from app.schemas.estoque import SaldoEstoqueRead, SaldoEstoqueSet

router = APIRouter(prefix="/saldos-estoque", tags=["estoque"])


@router.put("", response_model=SaldoEstoqueRead)
async def definir_saldo(payload: SaldoEstoqueSet, db: DbSession) -> SaldoEstoque:
    """Upsert: define o saldo de um SKU num elo. Evita múltiplas linhas
    para o mesmo (sku, elo), já que o saldo é sempre a foto mais recente."""
    stmt = select(SaldoEstoque).where(SaldoEstoque.sku_id == payload.sku_id)
    stmt = (
        stmt.where(SaldoEstoque.cd_id == payload.cd_id)
        if payload.cd_id
        else stmt.where(SaldoEstoque.filial_id == payload.filial_id)
    )
    result = await db.execute(stmt)
    saldo = result.scalar_one_or_none()

    if saldo is None:
        saldo = SaldoEstoque(**payload.model_dump())
        db.add(saldo)
    else:
        saldo.quantidade = payload.quantidade

    await db.commit()
    await db.refresh(saldo)
    return saldo


@router.get("", response_model=list[SaldoEstoqueRead])
async def listar_saldos(db: DbSession, sku_id: str | None = None) -> list[SaldoEstoque]:
    stmt = select(SaldoEstoque)
    if sku_id is not None:
        stmt = stmt.where(SaldoEstoque.sku_id == sku_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())
