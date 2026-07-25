"""Classificação de itens — Curva ABC, Curva PQR e coeficiente de variação
(roadmap seção 7, issue #19).

Observação de escopo: a Fase 1 não modelou preço/custo unitário do SKU, só
os campos de classificação e reposição (roadmap seção 4.6). Por isso a
Curva ABC aqui é calculada por **quantidade vendida** (proxy de relevância),
não por valor financeiro — quando o modelo de dados ganhar um campo de
preço/custo, a classificação por valor pode substituir esta sem mudar a
interface das funções abaixo.
"""

import uuid

import numpy as np


def classificar_abc(valores_por_sku: dict[uuid.UUID, float]) -> dict[uuid.UUID, str]:
    """Classificação de Pareto: A = top itens que somam até 80% do total,
    B = até 95%, C = restante."""
    if not valores_por_sku:
        return {}

    total = sum(valores_por_sku.values())
    if total <= 0:
        return {sku_id: "C" for sku_id in valores_por_sku}

    ordenado = sorted(valores_por_sku.items(), key=lambda item: item[1], reverse=True)
    resultado: dict[uuid.UUID, str] = {}
    acumulado = 0.0
    for sku_id, valor in ordenado:
        # Classifica pelo % acumulado ANTES de somar este item — é o início
        # da faixa que ele ocupa na curva. Evita que um item sozinho
        # responsável por 100% do valor seja jogado para C só porque o
        # acumulado final bate em 100% (bug: cumulativo pós-item classifica
        # pelo fim da faixa, punindo o maior item de cada corte).
        pct_acumulado_antes = acumulado / total
        if pct_acumulado_antes < 0.80:
            resultado[sku_id] = "A"
        elif pct_acumulado_antes < 0.95:
            resultado[sku_id] = "B"
        else:
            resultado[sku_id] = "C"
        acumulado += valor
    return resultado


def classificar_pqr(frequencia_por_sku: dict[uuid.UUID, float]) -> dict[uuid.UUID, str]:
    """Classificação por frequência de saída (roadmap seção 4.6 —
    Popular/Intermediária/Rara). `frequencia_por_sku` é a fração de
    períodos observados em que houve venda (0 a 1):
    P (popular) >= 0.66, Q (intermediário) >= 0.33, R (raro) abaixo disso.
    """
    resultado: dict[uuid.UUID, str] = {}
    for sku_id, frequencia in frequencia_por_sku.items():
        if frequencia >= 0.66:
            resultado[sku_id] = "P"
        elif frequencia >= 0.33:
            resultado[sku_id] = "Q"
        else:
            resultado[sku_id] = "R"
    return resultado


def coeficiente_variacao(serie: list[float]) -> float | None:
    """Desvio padrão / média — quanto maior, menos previsível a demanda.
    Retorna None quando a média é zero (não há como calcular)."""
    if not serie:
        return None
    arr = np.asarray(serie, dtype=float)
    media = arr.mean()
    if media == 0:
        return None
    return float(arr.std(ddof=0) / media)
