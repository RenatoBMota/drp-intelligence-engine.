from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import DbSession
from app.forecasting.classification_service import recalcular_classificacoes
from app.forecasting.safety_stock import (
    estoque_seguranca_estatistico,
    estoque_seguranca_monte_carlo,
)
from app.forecasting.service import gerar_projecao
from app.models.forecast import AjusteProjecao, ClassificacaoItem, HistoricoVendas, Projecao
from app.schemas.forecast import (
    AjusteProjecaoCreate,
    AjusteProjecaoRead,
    ClassificacaoItemRead,
    EstoqueSegurancaEstatisticoRequest,
    EstoqueSegurancaMonteCarloRequest,
    EstoqueSegurancaResponse,
    HistoricoVendasCreate,
    HistoricoVendasRead,
    ProjecaoGerarRequest,
    ProjecaoRead,
)

router = APIRouter(tags=["forecast"])


@router.post("/historico-vendas", response_model=HistoricoVendasRead, status_code=201)
async def registrar_venda(payload: HistoricoVendasCreate, db: DbSession) -> HistoricoVendas:
    registro = HistoricoVendas(**payload.model_dump())
    db.add(registro)
    await db.commit()
    await db.refresh(registro)
    return registro


@router.get("/historico-vendas", response_model=list[HistoricoVendasRead])
async def listar_vendas(db: DbSession, sku_id: str | None = None) -> list[HistoricoVendas]:
    stmt = select(HistoricoVendas).order_by(HistoricoVendas.data)
    if sku_id is not None:
        stmt = stmt.where(HistoricoVendas.sku_id == sku_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/projecoes/gerar", response_model=ProjecaoRead, status_code=201)
async def gerar_projecao_endpoint(payload: ProjecaoGerarRequest, db: DbSession) -> Projecao:
    try:
        return await gerar_projecao(
            db,
            sku_id=payload.sku_id,
            horizonte_dias=payload.horizonte_dias,
            cd_id=payload.cd_id,
            filial_id=payload.filial_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/projecoes", response_model=list[ProjecaoRead])
async def listar_projecoes(db: DbSession, sku_id: str | None = None) -> list[Projecao]:
    stmt = select(Projecao).order_by(Projecao.gerado_em.desc())
    if sku_id is not None:
        stmt = stmt.where(Projecao.sku_id == sku_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/ajustes-projecao", response_model=AjusteProjecaoRead, status_code=201)
async def criar_ajuste_projecao(
    payload: AjusteProjecaoCreate, db: DbSession
) -> AjusteProjecao:
    ajuste = AjusteProjecao(**payload.model_dump())
    db.add(ajuste)
    await db.commit()
    await db.refresh(ajuste)
    return ajuste


@router.get("/ajustes-projecao", response_model=list[AjusteProjecaoRead])
async def listar_ajustes_projecao(db: DbSession) -> list[AjusteProjecao]:
    result = await db.execute(select(AjusteProjecao))
    return list(result.scalars().all())


@router.post("/classificacoes/recalcular", response_model=list[ClassificacaoItemRead])
async def recalcular_classificacoes_endpoint(db: DbSession) -> list[ClassificacaoItem]:
    return await recalcular_classificacoes(db)


@router.get("/classificacoes", response_model=list[ClassificacaoItemRead])
async def listar_classificacoes(db: DbSession, sku_id: str | None = None) -> list[ClassificacaoItem]:
    stmt = select(ClassificacaoItem).order_by(ClassificacaoItem.calculado_em.desc())
    if sku_id is not None:
        stmt = stmt.where(ClassificacaoItem.sku_id == sku_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post("/estoque-seguranca/estatistico", response_model=EstoqueSegurancaResponse)
async def calcular_estoque_seguranca_estatistico(
    payload: EstoqueSegurancaEstatisticoRequest,
) -> EstoqueSegurancaResponse:
    valor = estoque_seguranca_estatistico(
        nivel_servico=payload.nivel_servico,
        desvio_padrao_demanda=payload.desvio_padrao_demanda,
        lead_time_dias=payload.lead_time_dias,
    )
    return EstoqueSegurancaResponse(estoque_seguranca=valor)


@router.post("/estoque-seguranca/monte-carlo", response_model=EstoqueSegurancaResponse)
async def calcular_estoque_seguranca_monte_carlo(
    payload: EstoqueSegurancaMonteCarloRequest, db: DbSession
) -> EstoqueSegurancaResponse:
    stmt = select(HistoricoVendas.quantidade).where(HistoricoVendas.sku_id == payload.sku_id)
    if payload.cd_id is not None:
        stmt = stmt.where(HistoricoVendas.cd_id == payload.cd_id)
    else:
        stmt = stmt.where(HistoricoVendas.filial_id == payload.filial_id)
    result = await db.execute(stmt)
    historico = [float(q) for q in result.scalars().all()]

    valor = estoque_seguranca_monte_carlo(
        demandas_historicas_diarias=historico,
        lead_time_dias=payload.lead_time_dias,
        nivel_servico=payload.nivel_servico,
        n_simulacoes=payload.n_simulacoes,
    )
    return EstoqueSegurancaResponse(estoque_seguranca=valor, n_pontos_historico=len(historico))
