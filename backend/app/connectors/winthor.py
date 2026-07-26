"""Conector WinThor (TOTVS) — ERP e WMS (roadmap seção 9, issue #11).

Decisão registrada: o sistema legado do cliente para cadastro de itens,
custos, entrada de NF e saldo físico por CD é o WinThor. WinThor cobre os
dois papéis (ERP e WMS) num único banco — por isso `WinthorErpConnector`
e `WinthorWmsConnector` moram no mesmo módulo, mas continuam implementando
os contratos separados `ErpConnector`/`WmsConnector` (app/connectors/erp.py,
wms.py), sem alterar quem os consome.

As consultas abaixo usam os nomes de tabela/coluna do dicionário de dados
padrão do WinThor (PCPRODUT, PCFORNEC, PCNFENT/PCNFENTI, PCEST). Não há uma
instância WinThor disponível neste ambiente — não foram validadas contra um
banco real. Antes de usar em produção: confirmar com o DBA do cliente se a
versão instalada segue esse dicionário padrão (customizações de campo são
comuns em instalações antigas) e apontar `settings.winthor_database_url`
para o dialeto correto (Oracle, a maioria das instalações, ou SQL Server em
instalações mais novas).

TMS e YMS (issue #39) ficam de fora — WinThor não cobre rastreamento de
transporte nem gestão de pátio/doca, então esses dois seguem sem sistema
alvo definido.
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.connectors.erp import EntradaNotaFiscal, ErpConnector, ItemErp
from app.connectors.wms import SaldoFisicoCd, WmsConnector

_SQL_ITENS_ATUALIZADOS = text(
    """
    SELECT p.CODPROD, p.DESCRICAO, p.PVENDA, f.CGC
    FROM PCPRODUT p
    LEFT JOIN PCFORNEC f ON f.CODFORNEC = p.CODFORNEC
    WHERE p.DTALTER >= :desde
    """
)

_SQL_NF_CABECALHO = text(
    """
    SELECT n.NUMNOTA, n.DATAEMISSAO, f.CGC
    FROM PCNFENT n
    LEFT JOIN PCFORNEC f ON f.CODFORNEC = n.CODFORNEC
    WHERE n.DATAEMISSAO >= :desde
    """
)

_SQL_NF_ITENS = text("SELECT CODPROD, QT FROM PCNFENTI WHERE NUMNOTA = :numnota")

_SQL_SALDO_FISICO = text("SELECT CODPROD, QTESTGER FROM PCEST WHERE CODFILIAL = :codfilial")


class WinthorErpConnector(ErpConnector):
    """ERP via WinThor: produtos (PCPRODUT), fornecedores (PCFORNEC) e
    entrada de notas fiscais (PCNFENT/PCNFENTI)."""

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def listar_itens_atualizados(self, desde: date) -> list[ItemErp]:
        async with self._engine.connect() as conn:
            linhas = (await conn.execute(_SQL_ITENS_ATUALIZADOS, {"desde": desde})).mappings().all()
        return [
            ItemErp(
                codigo=str(linha["CODPROD"]),
                descricao=linha["DESCRICAO"],
                custo_unitario=float(linha["PVENDA"] or 0),
                fornecedor_cnpj=linha["CGC"] or "",
            )
            for linha in linhas
        ]

    async def listar_entradas_nf(self, desde: date) -> list[EntradaNotaFiscal]:
        async with self._engine.connect() as conn:
            cabecalhos = (await conn.execute(_SQL_NF_CABECALHO, {"desde": desde})).mappings().all()
            entradas = []
            for cab in cabecalhos:
                itens = (await conn.execute(_SQL_NF_ITENS, {"numnota": cab["NUMNOTA"]})).mappings().all()
                entradas.append(
                    EntradaNotaFiscal(
                        numero_nf=str(cab["NUMNOTA"]),
                        fornecedor_cnpj=cab["CGC"] or "",
                        data_emissao=cab["DATAEMISSAO"],
                        itens=[(str(item["CODPROD"]), float(item["QT"])) for item in itens],
                    )
                )
        return entradas


class WinthorWmsConnector(WmsConnector):
    """Saldo físico via WinThor: tabela PCEST (estoque por filial/produto).

    WinThor não distingue CD de Filial operacionalmente — ambos são um
    `CODFILIAL` na mesma tabela `PCFILIAL`. O `cd_codigo` recebido aqui é
    repassado direto como `PCEST.CODFILIAL`.
    """

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def obter_saldo_fisico(self, cd_codigo: str) -> list[SaldoFisicoCd]:
        async with self._engine.connect() as conn:
            linhas = (await conn.execute(_SQL_SALDO_FISICO, {"codfilial": cd_codigo})).mappings().all()
        return [
            SaldoFisicoCd(
                cd_codigo=cd_codigo,
                sku_codigo=str(linha["CODPROD"]),
                quantidade=float(linha["QTESTGER"] or 0),
            )
            for linha in linhas
        ]
