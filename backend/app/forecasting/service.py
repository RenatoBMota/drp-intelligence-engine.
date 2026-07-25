"""Orquestração do motor de Forecast: busca histórico (com herança de
similar quando necessário — roadmap seção 4.6, issue #18), aplica ajustes
manuais ativos, seleciona a estratégia e persiste a projeção."""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.forecasting.selector import selecionar_estrategia
from app.models.cadastro import Sku
from app.models.forecast import AjusteProjecao, EscopoAjuste, HistoricoVendas, Projecao

_MIN_PONTOS_HISTORICO_PROPRIO = 5


async def _historico_diario(
    db: AsyncSession, sku_id: uuid.UUID, cd_id: uuid.UUID | None, filial_id: uuid.UUID | None
) -> list[float]:
    stmt = select(HistoricoVendas.quantidade).where(HistoricoVendas.sku_id == sku_id)
    if cd_id is not None:
        stmt = stmt.where(HistoricoVendas.cd_id == cd_id)
    else:
        stmt = stmt.where(HistoricoVendas.filial_id == filial_id)
    stmt = stmt.order_by(HistoricoVendas.data)
    result = await db.execute(stmt)
    return [float(q) for q in result.scalars().all()]


async def _ajuste_ativo(db: AsyncSession, sku: Sku) -> AjusteProjecao | None:
    hoje = date.today()
    stmt = select(AjusteProjecao).where(
        AjusteProjecao.ativo.is_(True), AjusteProjecao.data_limite >= hoje
    )
    result = await db.execute(stmt)
    ajustes = result.scalars().all()

    for ajuste in ajustes:
        if ajuste.escopo == EscopoAjuste.ITEM and ajuste.sku_id == sku.id:
            return ajuste
        if (
            ajuste.escopo == EscopoAjuste.FORNECEDOR
            and sku.fornecedor_id is not None
            and ajuste.fornecedor_id == sku.fornecedor_id
        ):
            return ajuste
    return None


async def gerar_projecao(
    db: AsyncSession,
    sku_id: uuid.UUID,
    horizonte_dias: int,
    cd_id: uuid.UUID | None = None,
    filial_id: uuid.UUID | None = None,
) -> Projecao:
    if (cd_id is None) == (filial_id is None):
        raise ValueError("Informe exatamente um elo: cd_id OU filial_id")

    sku = await db.get(Sku, sku_id)
    if sku is None:
        raise ValueError(f"SKU {sku_id} não encontrado")

    historico = await _historico_diario(db, sku_id, cd_id, filial_id)
    sku_similar_utilizado_id: uuid.UUID | None = None

    if len(historico) < _MIN_PONTOS_HISTORICO_PROPRIO and sku.sku_similar_id is not None:
        historico_similar = await _historico_diario(db, sku.sku_similar_id, cd_id, filial_id)
        if len(historico_similar) >= len(historico):
            historico = historico_similar
            sku_similar_utilizado_id = sku.sku_similar_id

    estrategia = selecionar_estrategia(sku.perfil_demanda, historico)
    quantidade_projetada = estrategia.prever(historico, horizonte_dias)

    ajuste = await _ajuste_ativo(db, sku)
    ajuste_pct = None
    if ajuste is not None:
        ajuste_pct = float(ajuste.percentual)
        quantidade_projetada *= 1 + (ajuste_pct / 100)

    projecao = Projecao(
        sku_id=sku_id,
        cd_id=cd_id,
        filial_id=filial_id,
        horizonte_dias=horizonte_dias,
        quantidade_projetada=max(quantidade_projetada, 0.0),
        modelo_utilizado=estrategia.nome,
        ajuste_aplicado_pct=ajuste_pct,
        sku_similar_utilizado_id=sku_similar_utilizado_id,
        gerado_em=datetime.now(timezone.utc),
    )
    db.add(projecao)
    await db.commit()
    await db.refresh(projecao)
    return projecao
