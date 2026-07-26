"""Conector ERP (roadmap seção 9): cadastro de itens, custos, entrada de NF.

ERP alvo definido (issue #11): WinThor (TOTVS) — ver
`app/connectors/winthor.py` para a implementação concreta
(`WinthorErpConnector`). Esta interface é o contrato que qualquer
implementação deve cumprir; `NullErpConnector` segue disponível como
default até o WinThor real ser configurado (`settings.winthor_database_url`).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date


@dataclass
class ItemErp:
    codigo: str
    descricao: str
    custo_unitario: float
    fornecedor_cnpj: str


@dataclass
class EntradaNotaFiscal:
    numero_nf: str
    fornecedor_cnpj: str
    data_emissao: date
    itens: list[tuple[str, float]]  # (codigo_item, quantidade)


class ErpConnector(ABC):
    """Contrato de integração com o ERP."""

    @abstractmethod
    async def listar_itens_atualizados(self, desde: date) -> list[ItemErp]:
        """Retorna itens (cadastro/custo) alterados desde a data informada."""

    @abstractmethod
    async def listar_entradas_nf(self, desde: date) -> list[EntradaNotaFiscal]:
        """Retorna notas fiscais de entrada emitidas desde a data informada."""


class NullErpConnector(ErpConnector):
    """Implementação nula, usada até que um ERP real seja integrado."""

    async def listar_itens_atualizados(self, desde: date) -> list[ItemErp]:
        return []

    async def listar_entradas_nf(self, desde: date) -> list[EntradaNotaFiscal]:
        return []
