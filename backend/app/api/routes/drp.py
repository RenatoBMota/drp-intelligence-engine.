import uuid
from datetime import date

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.api.deps import DbSession
from app.drp_engine.alertas import detectar_transferencias_atrasadas
from app.drp_engine.service import recalcular_sku_elo
from app.models.auditoria import LogDecisao, MotivoSilenciamento
from app.models.drp import OrdemCompra, OrdemTransferencia, StatusEstoqueSnapshot, StatusOrdem
from app.schemas.drp import (
    AtualizarStatusOrdemRequest,
    LogDecisaoRead,
    MotivoSilenciamentoCreate,
    MotivoSilenciamentoRead,
    OrdemCompraRead,
    OrdemTransferenciaRead,
    RecalcularRequest,
    RecalcularResponse,
    StatusEstoqueRead,
)

router = APIRouter(prefix="/drp", tags=["drp"])


@router.post("/recalcular", response_model=RecalcularResponse)
async def recalcular(payload: RecalcularRequest, db: DbSession) -> RecalcularResponse:
    try:
        resultado = await recalcular_sku_elo(
            db,
            sku_id=payload.sku_id,
            cd_id=payload.cd_id,
            filial_id=payload.filial_id,
            pesos_priorizacao=payload.pesos_priorizacao,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RecalcularResponse(
        status_estoque=resultado.snapshot,
        ordem_transferencia=resultado.ordem if isinstance(resultado.ordem, OrdemTransferencia) else None,
        ordem_compra=resultado.ordem if isinstance(resultado.ordem, OrdemCompra) else None,
        silenciado_motivo=resultado.silenciado_motivo,
    )


@router.get("/status", response_model=list[StatusEstoqueRead])
async def listar_status(db: DbSession, sku_id: str | None = None) -> list[StatusEstoqueSnapshot]:
    stmt = select(StatusEstoqueSnapshot).order_by(StatusEstoqueSnapshot.calculado_em.desc())
    if sku_id is not None:
        stmt = stmt.where(StatusEstoqueSnapshot.sku_id == sku_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/ordens-transferencia", response_model=list[OrdemTransferenciaRead])
async def listar_ordens_transferencia(db: DbSession) -> list[OrdemTransferencia]:
    result = await db.execute(select(OrdemTransferencia).order_by(OrdemTransferencia.score_criticidade.desc()))
    return list(result.scalars().all())


@router.patch("/ordens-transferencia/{ordem_id}", response_model=OrdemTransferenciaRead)
async def atualizar_status_ordem_transferencia(
    ordem_id: uuid.UUID, payload: AtualizarStatusOrdemRequest, db: DbSession
) -> OrdemTransferencia:
    ordem = await db.get(OrdemTransferencia, ordem_id)
    if ordem is None:
        raise HTTPException(status_code=404, detail="Ordem de transferência não encontrada")
    ordem.status = payload.status
    if payload.status == StatusOrdem.CONCLUIDA:
        ordem.data_conclusao = payload.data_conclusao or date.today()
    await db.commit()
    await db.refresh(ordem)
    return ordem


@router.get("/ordens-compra", response_model=list[OrdemCompraRead])
async def listar_ordens_compra(db: DbSession) -> list[OrdemCompra]:
    result = await db.execute(select(OrdemCompra).order_by(OrdemCompra.score_criticidade.desc()))
    return list(result.scalars().all())


@router.patch("/ordens-compra/{ordem_id}", response_model=OrdemCompraRead)
async def atualizar_status_ordem_compra(
    ordem_id: uuid.UUID, payload: AtualizarStatusOrdemRequest, db: DbSession
) -> OrdemCompra:
    ordem = await db.get(OrdemCompra, ordem_id)
    if ordem is None:
        raise HTTPException(status_code=404, detail="Ordem de compra não encontrada")
    ordem.status = payload.status
    if payload.status == StatusOrdem.CONCLUIDA:
        ordem.data_conclusao = payload.data_conclusao or date.today()
    await db.commit()
    await db.refresh(ordem)
    return ordem


@router.get("/alertas-desvio", response_model=list[OrdemTransferenciaRead])
async def alertas_desvio(db: DbSession) -> list[OrdemTransferencia]:
    return await detectar_transferencias_atrasadas(db)


@router.post("/motivos-silenciamento", response_model=MotivoSilenciamentoRead, status_code=201)
async def criar_motivo_silenciamento(
    payload: MotivoSilenciamentoCreate, db: DbSession
) -> MotivoSilenciamento:
    motivo = MotivoSilenciamento(**payload.model_dump())
    db.add(motivo)
    await db.commit()
    await db.refresh(motivo)
    return motivo


@router.get("/motivos-silenciamento", response_model=list[MotivoSilenciamentoRead])
async def listar_motivos_silenciamento(db: DbSession) -> list[MotivoSilenciamento]:
    result = await db.execute(select(MotivoSilenciamento))
    return list(result.scalars().all())


@router.get("/logs-decisao", response_model=list[LogDecisaoRead])
async def listar_logs_decisao(db: DbSession, entidade_id: str | None = None) -> list[LogDecisao]:
    stmt = select(LogDecisao).order_by(LogDecisao.created_at.desc())
    if entidade_id is not None:
        stmt = stmt.where(LogDecisao.entidade_id == entidade_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())
