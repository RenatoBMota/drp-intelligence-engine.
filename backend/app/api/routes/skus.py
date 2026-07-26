import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.cadastro import Sku
from app.schemas.cadastro import AtualizarAtivoSkuRequest, SkuCreate, SkuRead

router = APIRouter(prefix="/skus", tags=["cadastro"])


@router.post("", response_model=SkuRead, status_code=201)
async def criar_sku(payload: SkuCreate, db: DbSession) -> Sku:
    sku = Sku(**payload.model_dump())
    db.add(sku)
    await db.commit()
    await db.refresh(sku)
    return sku


@router.get("", response_model=list[SkuRead])
async def listar_skus(db: DbSession) -> list[Sku]:
    result = await db.execute(select(Sku).order_by(Sku.codigo))
    return list(result.scalars().all())


@router.get("/{sku_id}", response_model=SkuRead)
async def obter_sku(sku_id: uuid.UUID, db: DbSession) -> Sku:
    sku = await db.get(Sku, sku_id)
    if sku is None:
        raise HTTPException(status_code=404, detail="SKU não encontrado")
    return sku


@router.patch("/{sku_id}/ativo", response_model=SkuRead)
async def atualizar_ativo_sku(sku_id: uuid.UUID, payload: AtualizarAtivoSkuRequest, db: DbSession) -> Sku:
    """Inativação de SKU sem giro/descontinuado (roadmap seção 4.11 e 11,
    issue #40) — não deleta o cadastro, só impede que o motor DRP gere
    novas sugestões de compra/transferência para o SKU a partir de agora
    (`recalcular_sku_elo` verifica `Sku.ativo` antes de decidir)."""
    sku = await db.get(Sku, sku_id)
    if sku is None:
        raise HTTPException(status_code=404, detail="SKU não encontrado")
    sku.ativo = payload.ativo
    await db.commit()
    await db.refresh(sku)
    return sku
