"""Conector WMS (roadmap seção 9): saldo físico por CD, status de separação.

WMS alvo definido (issue #11): o próprio WinThor (TOTVS) cobre esse papel
também — ver `app/connectors/winthor.py` (`WinthorWmsConnector`).
`NullWmsConnector` segue disponível como default até o WinThor real ser
configurado (`settings.winthor_database_url`).
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
