"""Cálculo de Estoque de Segurança (roadmap seção 7, issue #16): abordagem
estatística clássica e simulação de Monte Carlo."""

import numpy as np
from scipy.stats import norm


def estoque_seguranca_estatistico(
    nivel_servico: float, desvio_padrao_demanda: float, lead_time_dias: float
) -> float:
    """Estoque de segurança = Z(nível de serviço) × desvio padrão da
    demanda × raiz do lead time — fórmula clássica citada no roadmap."""
    if desvio_padrao_demanda <= 0 or lead_time_dias <= 0:
        return 0.0
    z = norm.ppf(nivel_servico)
    return max(float(z * desvio_padrao_demanda * (lead_time_dias**0.5)), 0.0)


def estoque_seguranca_monte_carlo(
    demandas_historicas_diarias: list[float],
    lead_time_dias: int,
    nivel_servico: float,
    n_simulacoes: int = 10_000,
    seed: int | None = None,
) -> float:
    """Simula `n_simulacoes` cenários de demanda ao longo do lead time,
    reamostrando (bootstrap) a demanda diária histórica, e retorna o
    estoque de segurança como o percentil `nivel_servico` da demanda
    simulada no lead time, acima da média — indicado para SKUs de alta
    variabilidade, onde a distribuição normal da fórmula clássica é uma
    aproximação pobre."""
    demandas = np.asarray(demandas_historicas_diarias, dtype=float)
    if demandas.size == 0 or lead_time_dias <= 0:
        return 0.0

    rng = np.random.default_rng(seed)
    amostras = rng.choice(demandas, size=(n_simulacoes, lead_time_dias), replace=True)
    demanda_no_lead_time = amostras.sum(axis=1)

    media = demanda_no_lead_time.mean()
    percentil = np.quantile(demanda_no_lead_time, nivel_servico)
    return max(float(percentil - media), 0.0)
