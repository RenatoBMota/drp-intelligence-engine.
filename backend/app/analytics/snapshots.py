"""Helper compartilhado: o status "atual" de um SKU/elo é o snapshot mais
recente em StatusEstoqueSnapshot — a tabela guarda histórico (um registro
por recálculo), não um único estado por sku/elo."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.drp import StatusEstoqueSnapshot


async def ultimos_snapshots(db: AsyncSession) -> list[StatusEstoqueSnapshot]:
    stmt = select(StatusEstoqueSnapshot).order_by(StatusEstoqueSnapshot.calculado_em.desc())
    result = await db.execute(stmt)

    vistos: set[tuple[uuid.UUID, uuid.UUID | None, uuid.UUID | None]] = set()
    ultimos: list[StatusEstoqueSnapshot] = []
    for snapshot in result.scalars().all():
        chave = (snapshot.sku_id, snapshot.cd_id, snapshot.filial_id)
        if chave in vistos:
            continue
        vistos.add(chave)
        ultimos.append(snapshot)
    return ultimos
