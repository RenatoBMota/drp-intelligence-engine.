"""Governança e Saneamento (roadmap seção 11, issue #40).

Não coberto aqui: **Padronização Descritiva de Materiais (PDM)** — o
roadmap cita como pré-requisito de qualidade de dado, mas não define regra
objetiva (ex.: limiar de similaridade textual entre descrições) para
implementar uma verificação automática. Avaliação por categoria reaproveita
`relatorios.curva_abc_pqr` — não há nada novo a construir para isso.
"""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drp import OrdemCompra, OrdemTransferencia, StatusOrdem

_STATUS_EM_ABERTO = [StatusOrdem.SUGERIDA, StatusOrdem.APROVADA, StatusOrdem.EM_TRANSITO]


async def pedidos_para_saneamento(db: AsyncSession, dias_atraso_critico: int = 30) -> dict[str, list]:
    """Pedidos em aberto sem previsão real de entrada (roadmap seção 4.11
    e 11): ordens ainda não concluídas cuja data prevista já passou por
    uma margem grande — candidatas a cancelamento/investigação manual, não
    apenas ao alerta de desvio de curto prazo (issue #28)."""
    limite = date.today() - timedelta(days=dias_atraso_critico)

    transferencias = (
        await db.execute(
            select(OrdemTransferencia).where(
                OrdemTransferencia.status.in_(_STATUS_EM_ABERTO),
                OrdemTransferencia.data_chegada_estimada < limite,
            )
        )
    ).scalars().all()
    compras = (
        await db.execute(
            select(OrdemCompra).where(
                OrdemCompra.status.in_(_STATUS_EM_ABERTO),
                OrdemCompra.data_previsao < limite,
            )
        )
    ).scalars().all()

    return {"transferencias": list(transferencias), "compras": list(compras)}
