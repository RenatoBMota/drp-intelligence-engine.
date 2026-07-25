from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.cadastro import CentroDistribuicao, Filial
from app.schemas.cadastro import (
    CentroDistribuicaoCreate,
    CentroDistribuicaoRead,
    FilialCreate,
    FilialRead,
)

router = APIRouter(tags=["cadastro"])


@router.post("/centros-distribuicao", response_model=CentroDistribuicaoRead, status_code=201)
async def criar_cd(payload: CentroDistribuicaoCreate, db: DbSession) -> CentroDistribuicao:
    cd = CentroDistribuicao(**payload.model_dump())
    db.add(cd)
    await db.commit()
    await db.refresh(cd)
    return cd


@router.get("/centros-distribuicao", response_model=list[CentroDistribuicaoRead])
async def listar_cds(db: DbSession) -> list[CentroDistribuicao]:
    result = await db.execute(select(CentroDistribuicao).order_by(CentroDistribuicao.codigo))
    return list(result.scalars().all())


@router.post("/filiais", response_model=FilialRead, status_code=201)
async def criar_filial(payload: FilialCreate, db: DbSession) -> Filial:
    filial = Filial(**payload.model_dump())
    db.add(filial)
    await db.commit()
    await db.refresh(filial)
    return filial


@router.get("/filiais", response_model=list[FilialRead])
async def listar_filiais(db: DbSession) -> list[Filial]:
    result = await db.execute(select(Filial).order_by(Filial.codigo))
    return list(result.scalars().all())
