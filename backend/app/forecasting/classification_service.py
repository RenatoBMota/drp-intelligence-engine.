"""Orquestra o recálculo de Curva ABC/PQR e coeficiente de variação para
todos os SKUs com histórico de vendas (issue #19)."""

import uuid
from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.forecasting.classification import (
    classificar_abc,
    classificar_pqr,
    coeficiente_variacao,
)
from app.models.forecast import ClassificacaoItem, HistoricoVendas


async def recalcular_classificacoes(db: AsyncSession) -> list[ClassificacaoItem]:
    stmt = select(
        HistoricoVendas.sku_id, HistoricoVendas.data, HistoricoVendas.quantidade
    )
    result = await db.execute(stmt)
    linhas = result.all()

    if not linhas:
        return []

    quantidades_por_sku: dict[uuid.UUID, list[float]] = defaultdict(list)
    dias_com_venda_por_sku: dict[uuid.UUID, set] = defaultdict(set)
    todas_as_datas: set = set()

    for sku_id, data_venda, quantidade in linhas:
        quantidades_por_sku[sku_id].append(float(quantidade))
        dias_com_venda_por_sku[sku_id].add(data_venda)
        todas_as_datas.add(data_venda)

    total_dias_observados = max((max(todas_as_datas) - min(todas_as_datas)).days + 1, 1)

    valores_totais = {
        sku_id: sum(quantidades) for sku_id, quantidades in quantidades_por_sku.items()
    }
    frequencias = {
        sku_id: len(dias) / total_dias_observados
        for sku_id, dias in dias_com_venda_por_sku.items()
    }

    classificacoes_abc = classificar_abc(valores_totais)
    classificacoes_pqr = classificar_pqr(frequencias)

    agora = datetime.now(timezone.utc)
    resultado: list[ClassificacaoItem] = []
    for sku_id in quantidades_por_sku:
        classificacao = ClassificacaoItem(
            sku_id=sku_id,
            curva_abc=classificacoes_abc[sku_id],
            curva_pqr=classificacoes_pqr[sku_id],
            coeficiente_variacao=coeficiente_variacao(quantidades_por_sku[sku_id]),
            calculado_em=agora,
        )
        db.add(classificacao)
        resultado.append(classificacao)

    await db.commit()
    for classificacao in resultado:
        await db.refresh(classificacao)
    return resultado
