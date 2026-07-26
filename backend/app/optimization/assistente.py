"""RBM TASK 2.0 — Agente de decisão assistida (roadmap seção 9, issue
#33): "organiza a agenda... prioriza tarefas com base no contexto do
dia... cobra responsáveis por tarefas atrasadas".

Implementação honesta do que dá pra entregar sem um LLM (nenhuma API de
modelo de linguagem está configurada neste projeto): um gerador de
prioridades **determinístico**, baseado em regras sobre os dados já
calculados pelo motor DRP (Fase 3) e pela Torre de Controle (Fase 5) — não
é um assistente conversacional. Produz uma lista ordenada de alertas em
português, pronta para virar notificação/e-mail/painel.
"""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.analytics.control_tower import resumo_executivo
from app.analytics.snapshots import ultimos_snapshots
from app.drp_engine.alertas import detectar_transferencias_atrasadas
from app.models.drp import StatusRuptura

_PRIORIDADE_STATUS = {
    StatusRuptura.RUPTURA: 0,
    StatusRuptura.RUPTURA_DRP: 1,
    StatusRuptura.ELEVADA_EXPOSICAO_RUPTURA: 2,
    StatusRuptura.BAIXA_EXPOSICAO_RUPTURA: 3,
}


@dataclass
class ItemPrioridade:
    severidade: str  # "CRITICA" | "ALTA" | "MEDIA"
    mensagem: str


async def gerar_resumo_priorizado(db: AsyncSession, top_n: int = 10) -> list[ItemPrioridade]:
    itens: list[ItemPrioridade] = []

    resumo = await resumo_executivo(db)
    contagem = resumo.contagem_por_status
    if contagem.get(StatusRuptura.RUPTURA.value):
        itens.append(ItemPrioridade("CRITICA", f"{contagem[StatusRuptura.RUPTURA.value]} elo(s) em Ruptura total — ação imediata."))
    if contagem.get(StatusRuptura.RUPTURA_DRP.value):
        itens.append(
            ItemPrioridade(
                "CRITICA",
                f"{contagem[StatusRuptura.RUPTURA_DRP.value]} elo(s) em Ruptura por DRP — saldo local ok, "
                "mas a rede não cobre a necessidade agregada.",
            )
        )
    if contagem.get(StatusRuptura.ELEVADA_EXPOSICAO_RUPTURA.value):
        itens.append(
            ItemPrioridade(
                "ALTA",
                f"{contagem[StatusRuptura.ELEVADA_EXPOSICAO_RUPTURA.value]} elo(s) em Elevada Exposição a Ruptura.",
            )
        )

    snapshots = [s for s in await ultimos_snapshots(db) if s.status in _PRIORIDADE_STATUS]
    snapshots.sort(key=lambda s: (_PRIORIDADE_STATUS[s.status], -float(s.necessidade_liquida)))
    for snapshot in snapshots[:top_n]:
        itens.append(
            ItemPrioridade(
                "ALTA" if snapshot.status in (StatusRuptura.RUPTURA, StatusRuptura.RUPTURA_DRP) else "MEDIA",
                f"SKU {snapshot.sku_id} — necessidade líquida de {float(snapshot.necessidade_liquida):.1f} un. "
                f"(status {snapshot.status.value}).",
            )
        )

    atrasadas = await detectar_transferencias_atrasadas(db)
    for ordem in atrasadas[:top_n]:
        itens.append(
            ItemPrioridade(
                "ALTA",
                f"Ordem de transferência {ordem.id} está atrasada (previsão era {ordem.data_chegada_estimada}) "
                "— cobrar responsável ou reabrir o cálculo de necessidade.",
            )
        )

    return itens
