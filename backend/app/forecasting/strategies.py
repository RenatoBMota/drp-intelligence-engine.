"""Estratégias de forecast (roadmap seção 7).

Cada estratégia recebe a série histórica diária (mais recente por último) e
devolve a demanda projetada total para o horizonte pedido.

Implementadas: Média Móvel (fallback universal, funciona com pouquíssimo
histórico) e Holt-Winters (suavização exponencial, captura tendência e
sazonalidade). ARIMA, Prophet, XGBoost e LSTM — citados no roadmap como
opções adicionais — não estão implementados ainda; a interface
`ForecastStrategy` foi desenhada para que novas estratégias sejam
adicionadas sem alterar o seletor nem o serviço de geração de projeção.
"""

from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


class ForecastStrategy(ABC):
    nome: str

    @abstractmethod
    def prever(self, historico_diario: list[float], horizonte_dias: int) -> float:
        """Retorna a demanda total projetada para os próximos `horizonte_dias`."""


class MediaMovelStrategy(ForecastStrategy):
    """Projeta a demanda futura como a média diária histórica × horizonte.
    Funciona mesmo com histórico mínimo (inclusive 1 ponto) — usada como
    fallback para itens esporádicos ou com pouco histórico."""

    nome = "MEDIA_MOVEL"

    def prever(self, historico_diario: list[float], horizonte_dias: int) -> float:
        if not historico_diario:
            return 0.0
        media_diaria = float(np.mean(historico_diario))
        return max(media_diaria * horizonte_dias, 0.0)


class HoltWintersStrategy(ForecastStrategy):
    """Suavização exponencial de Holt-Winters — captura tendência e, com
    histórico suficiente (>= 2 ciclos semanais), sazonalidade semanal.
    Indicada para perfis de demanda repetitivos/sazonais."""

    nome = "HOLT_WINTERS"

    def prever(self, historico_diario: list[float], horizonte_dias: int) -> float:
        serie = pd.Series(historico_diario)
        usar_sazonalidade = len(serie) >= 14

        try:
            modelo = ExponentialSmoothing(
                serie,
                trend="add",
                seasonal="add" if usar_sazonalidade else None,
                seasonal_periods=7 if usar_sazonalidade else None,
                initialization_method="estimated",
            ).fit()
            previsao = modelo.forecast(horizonte_dias)
            return float(max(previsao.sum(), 0.0))
        except (ValueError, np.linalg.LinAlgError):
            # Séries degeneradas (ex.: todos os valores iguais/zero) podem
            # fazer o ajuste do Holt-Winters falhar — cai para média móvel.
            return MediaMovelStrategy().prever(historico_diario, horizonte_dias)
