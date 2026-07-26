import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.transporte import Rota
from app.optimization import service as otimizacao_service
from app.optimization.assistente import gerar_resumo_priorizado
from app.optimization.grafo import caminho_mais_barato, construir_grafo, fluxo_maximo
from app.optimization.simulacao import CenarioHipotetico, simular_cenario
from app.schemas.otimizacao import (
    ItemPrioridadeRead,
    OtimizarSkuRequest,
    ResultadoOtimizacaoRead,
    SimularCenarioRequest,
)
from app.schemas.transporte import RotaCreate, RotaRead

router = APIRouter(tags=["otimizacao"])


@router.post("/rotas", response_model=RotaRead, status_code=201)
async def criar_rota(payload: RotaCreate, db: DbSession) -> Rota:
    rota = Rota(**payload.model_dump())
    db.add(rota)
    await db.commit()
    await db.refresh(rota)
    return rota


@router.get("/rotas", response_model=list[RotaRead])
async def listar_rotas(db: DbSession) -> list[Rota]:
    result = await db.execute(select(Rota))
    return list(result.scalars().all())


@router.get("/otimizacao/grafo/caminho-mais-barato")
async def rota_caminho_mais_barato(origem: str, destino: str, db: DbSession) -> dict:
    grafo = await construir_grafo(db)
    resultado = caminho_mais_barato(grafo, origem, destino)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Sem caminho entre os elos informados")
    return resultado


@router.get("/otimizacao/grafo/fluxo-maximo")
async def rota_fluxo_maximo(origem: str, destino: str, db: DbSession) -> dict:
    grafo = await construir_grafo(db)
    resultado = fluxo_maximo(grafo, origem, destino)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Elo(s) não encontrado(s) no grafo")
    return {"fluxo_maximo": resultado["fluxo_maximo"]}


@router.post("/otimizacao/sku/{sku_id}", response_model=ResultadoOtimizacaoRead)
async def otimizar_sku(sku_id: uuid.UUID, payload: OtimizarSkuRequest, db: DbSession):
    try:
        return await otimizacao_service.otimizar_sku(db, sku_id, custo_compra_externa=payload.custo_compra_externa)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/otimizacao/sku/{sku_id}/simular", response_model=ResultadoOtimizacaoRead)
async def simular_cenario_sku(sku_id: uuid.UUID, payload: SimularCenarioRequest, db: DbSession):
    cenario = CenarioHipotetico(**payload.model_dump())
    try:
        return await simular_cenario(db, sku_id, cenario)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/assistente/resumo", response_model=list[ItemPrioridadeRead])
async def assistente_resumo(db: DbSession, top_n: int = 10):
    return await gerar_resumo_priorizado(db, top_n=top_n)
