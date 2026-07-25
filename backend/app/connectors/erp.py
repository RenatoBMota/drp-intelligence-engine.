"""Conector ERP (roadmap seção 9): cadastro de itens, custos, entrada de NF.

Nenhum ERP alvo foi definido ainda no roadmap (seção 13). Esta interface
define o contrato que qualquer implementação concreta (SAP, TOTVS, Oracle
etc.) deve cumprir; a implementação real entra quando o sistema for
escolhido.
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
