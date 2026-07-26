"""Priorização por score de criticidade (roadmap seção 6.5, issue #23).

Score = w1·Criticidade de Resultado + w2·Custo de Aquisição
        + w3·(1 / Cobertura Atual) + w4·Frequência de Saída

Os pesos (w1..w4) são "configuráveis por vertical de cliente" no roadmap —
isso implica um sistema de configuração por tenant que só faz sentido a
partir da Fase 4 (multiempresa/SaaS). Por ora os pesos têm um default
único e podem ser passados explicitamente por chamada.
"""

from app.models.cadastro import CriticidadeResultado, CustoAquisicao, FrequenciaSaida

PESOS_PADRAO = {"w1": 0.4, "w2": 0.2, "w3": 0.3, "w4": 0.1}

_CRITICIDADE_PESO = {
    CriticidadeResultado.VITAL: 3.0,
    CriticidadeResultado.INTERMEDIARIO: 2.0,
    CriticidadeResultado.ORDINARIO: 1.0,
}
_CUSTO_PESO = {
    CustoAquisicao.ELEVADO: 3.0,
    CustoAquisicao.INTERMEDIARIO: 2.0,
    CustoAquisicao.BAIXO: 1.0,
}
_FREQUENCIA_PESO = {
    FrequenciaSaida.POPULAR: 3.0,
    FrequenciaSaida.INTERMEDIARIA: 2.0,
    FrequenciaSaida.RARO: 1.0,
}


def calcular_score(
    criticidade_resultado: CriticidadeResultado | None,
    custo_aquisicao: CustoAquisicao | None,
    cobertura_atual_dias: float,
    frequencia_saida: FrequenciaSaida | None,
    pesos: dict[str, float] | None = None,
) -> float:
    """Quanto maior o score, mais crítica/urgente a necessidade — usado
    para ordenar a fila de execução de ordens de transferência/compra.
    Campos de classificação ausentes contam com o menor peso (1.0), para
    não impedir o cálculo em SKUs ainda não totalmente classificados.
    """
    p = pesos or PESOS_PADRAO

    criticidade = _CRITICIDADE_PESO.get(criticidade_resultado, 1.0)
    custo = _CUSTO_PESO.get(custo_aquisicao, 1.0)
    inverso_cobertura = 1 / cobertura_atual_dias if cobertura_atual_dias > 0 else 1.0
    frequencia = _FREQUENCIA_PESO.get(frequencia_saida, 1.0)

    return (
        p["w1"] * criticidade
        + p["w2"] * custo
        + p["w3"] * inverso_cobertura
        + p["w4"] * frequencia
    )
