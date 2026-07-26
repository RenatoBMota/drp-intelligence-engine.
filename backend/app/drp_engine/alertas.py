"""Alertas de desvio de execução (roadmap seção 6.7, issue #28): quando a
execução real diverge da ordem sugerida (ex.: transferência atrasada).

Implementado como consulta derivada, não como tabela própria — o desvio é
sempre recalculável a partir do status/data das ordens, não há estado extra
para manter sincronizado."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drp import OrdemTransferencia, StatusOrdem


async def detectar_transferencias_atrasadas(db: AsyncSession) -> list[OrdemTransferencia]:
    """Ordens de transferência cuja data de chegada estimada já passou e
    que ainda não foram concluídas — a necessidade que as originou deve
    ser reaberta (recalculada) para o elo de destino."""
    hoje = date.today()
    stmt = select(OrdemTransferencia).where(
        OrdemTransferencia.data_chegada_estimada < hoje,
        OrdemTransferencia.status.in_([StatusOrdem.SUGERIDA, StatusOrdem.APROVADA, StatusOrdem.EM_TRANSITO]),
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
