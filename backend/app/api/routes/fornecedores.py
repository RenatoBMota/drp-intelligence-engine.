from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.cadastro import Fornecedor
from app.schemas.cadastro import FornecedorCreate, FornecedorRead

router = APIRouter(prefix="/fornecedores", tags=["cadastro"])


@router.post("", response_model=FornecedorRead, status_code=201)
async def criar_fornecedor(payload: FornecedorCreate, db: DbSession) -> Fornecedor:
    fornecedor = Fornecedor(**payload.model_dump())
    db.add(fornecedor)
    await db.commit()
    await db.refresh(fornecedor)
    return fornecedor


@router.get("", response_model=list[FornecedorRead])
async def listar_fornecedores(db: DbSession) -> list[Fornecedor]:
    result = await db.execute(select(Fornecedor).order_by(Fornecedor.razao_social))
    return list(result.scalars().all())
