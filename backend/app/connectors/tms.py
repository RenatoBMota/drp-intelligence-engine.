"""Conector TMS (roadmap seção 9): lead time real de transporte,
rastreamento de transferências em trânsito.

Mesmo padrão de `erp.py`/`wms.py` (Fase 1): nenhum TMS alvo foi definido
no roadmap (seção 13), então isto é só o contrato, com implementação nula.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class RastreioTransporte:
    ordem_transferencia_id: str
    localizacao_atual: str
    previsao_chegada_atualizada: date | None


class TmsConnector(ABC):
    @abstractmethod
    async def rastrear(self, ordem_transferencia_id: str) -> RastreioTransporte | None:
        """Retorna o rastreio mais recente de uma transferência em trânsito."""

    @abstractmethod
    async def lead_time_real_rota(self, origem_codigo: str, destino_codigo: str) -> float | None:
        """Lead time real médio (dias) observado numa rota, para recalibrar
        o `LEAD_TIME_TRANSFERENCIA_PADRAO_DIAS` usado no motor DRP (Fase 3)."""


class NullTmsConnector(TmsConnector):
    async def rastrear(self, ordem_transferencia_id: str) -> RastreioTransporte | None:
        return None

    async def lead_time_real_rota(self, origem_codigo: str, destino_codigo: str) -> float | None:
        return None
