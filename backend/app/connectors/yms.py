"""Conector YMS (roadmap seção 9): gestão de pátio/docas — relevante para
prever confirmação de janela de recebimento das transferências.

Mesmo padrão de `erp.py`/`wms.py` (Fase 1): nenhum YMS alvo foi definido.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class JanelaRecebimento:
    cd_codigo: str
    doca: str
    inicio: datetime
    fim: datetime
    confirmada: bool


class YmsConnector(ABC):
    @abstractmethod
    async def proxima_janela_disponivel(self, cd_codigo: str) -> JanelaRecebimento | None:
        """Próxima janela de doca livre num CD, para agendar o recebimento
        de uma Ordem de Transferência ou Ordem de Compra."""


class NullYmsConnector(YmsConnector):
    async def proxima_janela_disponivel(self, cd_codigo: str) -> JanelaRecebimento | None:
        return None
