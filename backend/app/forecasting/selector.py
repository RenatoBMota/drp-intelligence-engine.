"""Seleção automática de modelo por perfil de demanda (roadmap seção 7,
issue #15)."""

from app.forecasting.strategies import (
    ForecastStrategy,
    HoltWintersStrategy,
    MediaMovelStrategy,
)

_MIN_PONTOS_HOLT_WINTERS = 14
_PERFIS_SAZONAIS = {"SAZONAL", "REPETITIVO"}


def selecionar_estrategia(
    perfil_demanda: str | None, historico_diario: list[float]
) -> ForecastStrategy:
    """Escolhe a estratégia de forecast conforme o perfil de demanda do SKU
    e o volume de histórico disponível.

    - Menos de 14 pontos: Média Móvel (Holt-Winters não converge bem com
      pouco histórico).
    - Perfil repetitivo/sazonal com histórico suficiente: Holt-Winters.
    - Demais casos (ex.: esporádico): Média Móvel.
    """
    if len(historico_diario) < _MIN_PONTOS_HOLT_WINTERS:
        return MediaMovelStrategy()

    perfil = (perfil_demanda or "").strip().upper()
    if perfil in _PERFIS_SAZONAIS:
        return HoltWintersStrategy()

    return MediaMovelStrategy()
