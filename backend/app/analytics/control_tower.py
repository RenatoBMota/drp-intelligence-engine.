"""Control Tower — visão executiva (roadmap seção 10.1, issue #35), com os
indicadores de feedback loop da seção 10.4 (Taxa de Resolução por Rede,
Lead Time Efetivo) que originalmente estavam previstos na issue #34
(Fase 4) — trazidos para cá porque o roadmap já os descreve como
indicadores da Torre de Controle."""

from collections import Counter
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.snapshots import ultimos_snapshots
from app.models.drp import OrdemCompra, OrdemTransferencia, StatusOrdem


@dataclass
class TaxaResolucaoRede:
    quantidade_via_transferencia: float
    quantidade_via_compra: float
    taxa_resolucao_rede: float | None


async def taxa_resolucao_rede(db: AsyncSession) -> TaxaResolucaoRede:
    """% da necessidade líquida total resolvida via transferência interna
    vs. compra externa — mede a eficácia do motor DRP em evitar compras
    desnecessárias (roadmap seção 10.4)."""
    soma_transferencia = (await db.execute(select(OrdemTransferencia.quantidade))).scalars().all()
    soma_compra = (await db.execute(select(OrdemCompra.quantidade))).scalars().all()

    total_transferencia = float(sum(float(q) for q in soma_transferencia))
    total_compra = float(sum(float(q) for q in soma_compra))
    total = total_transferencia + total_compra

    return TaxaResolucaoRede(
        quantidade_via_transferencia=total_transferencia,
        quantidade_via_compra=total_compra,
        taxa_resolucao_rede=(total_transferencia / total) if total > 0 else None,
    )


@dataclass
class LeadTimeEfetivo:
    n_ordens_concluidas: int
    lead_time_planejado_medio_dias: float | None
    lead_time_efetivo_medio_dias: float | None


async def lead_time_efetivo_transferencia(db: AsyncSession) -> LeadTimeEfetivo:
    """Lead Time Efetivo de Transferência vs. planejado (roadmap seção
    10.4) — feedback loop para recalibrar o motor."""
    stmt = select(OrdemTransferencia).where(
        OrdemTransferencia.status == StatusOrdem.CONCLUIDA,
        OrdemTransferencia.data_conclusao.is_not(None),
    )
    result = await db.execute(stmt)
    ordens = result.scalars().all()

    if not ordens:
        return LeadTimeEfetivo(0, None, None)

    planejados = [(o.data_chegada_estimada - o.data_embarque_sugerida).days for o in ordens]
    efetivos = [(o.data_conclusao - o.data_embarque_sugerida).days for o in ordens]

    return LeadTimeEfetivo(
        n_ordens_concluidas=len(ordens),
        lead_time_planejado_medio_dias=sum(planejados) / len(planejados),
        lead_time_efetivo_medio_dias=sum(efetivos) / len(efetivos),
    )


@dataclass
class ResumoExecutivo:
    contagem_por_status: dict[str, int]
    necessidade_liquida_total_aberta: float
    ordens_transferencia_pendentes: int
    ordens_compra_pendentes: int
    taxa_resolucao_rede: TaxaResolucaoRede
    lead_time_efetivo: LeadTimeEfetivo


async def resumo_executivo(db: AsyncSession) -> ResumoExecutivo:
    snapshots = await ultimos_snapshots(db)
    contagem = Counter(s.status.value for s in snapshots)
    necessidade_aberta = sum(max(float(s.necessidade_liquida), 0.0) for s in snapshots)

    pendentes_transf = await db.execute(
        select(OrdemTransferencia).where(
            OrdemTransferencia.status.notin_([StatusOrdem.CONCLUIDA, StatusOrdem.CANCELADA])
        )
    )
    pendentes_compra = await db.execute(
        select(OrdemCompra).where(OrdemCompra.status.notin_([StatusOrdem.CONCLUIDA, StatusOrdem.CANCELADA]))
    )

    return ResumoExecutivo(
        contagem_por_status=dict(contagem),
        necessidade_liquida_total_aberta=necessidade_aberta,
        ordens_transferencia_pendentes=len(pendentes_transf.scalars().all()),
        ordens_compra_pendentes=len(pendentes_compra.scalars().all()),
        taxa_resolucao_rede=await taxa_resolucao_rede(db),
        lead_time_efetivo=await lead_time_efetivo_transferencia(db),
    )
