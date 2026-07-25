"""Conector WMS (roadmap seção 9): saldo físico por CD, status de separação.

Assim como o ERP, o WMS alvo ainda não foi definido (roadmap seção 13).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SaldoFisicoCd:
    cd_codigo: str
    sku_codigo: str
    quantidade: float


class WmsConnector(ABC):
    """Contrato de integração com o WMS."""

    @abstractmethod
    async def obter_saldo_fisico(self, cd_codigo: str) -> list[SaldoFisicoCd]:
        """Retorna o saldo físico de todos os SKUs em um CD."""


class NullWmsConnector(WmsConnector):
    """Implementação nula, usada até que um WMS real seja integrado."""

    async def obter_saldo_fisico(self, cd_codigo: str) -> list[SaldoFisicoCd]:
        return []
