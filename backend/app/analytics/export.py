"""Exportação de relatórios em Excel (roadmap seção 10, issue #38).

Implementado como download direto (streaming), não via MinIO — a Fase 1
não colocou um serviço MinIO no docker-compose (só Postgres/Redis/
backend/frontend), então não há onde persistir o arquivo gerado ainda.
Gerar o arquivo e devolver por streaming resolve o caso de uso imediato
("consigo exportar o relatório?"); persistência em objeto storage fica
para quando o MinIO for adicionado à infra.
"""

import io
from collections.abc import Iterable, Mapping
from typing import Any

from openpyxl import Workbook


def gerar_excel(linhas: Iterable[Mapping[str, Any]], nome_planilha: str = "Relatório") -> bytes:
    """Recebe uma lista de dicts (mesma forma que os endpoints JSON já
    retornam) e devolve os bytes de um .xlsx com cabeçalho."""
    linhas = list(linhas)

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = nome_planilha[:31]  # limite do Excel para nome de aba

    if linhas:
        cabecalho = list(linhas[0].keys())
        sheet.append(cabecalho)
        for linha in linhas:
            sheet.append([_serializar(linha.get(coluna)) for coluna in cabecalho])
    else:
        sheet.append(["(sem dados)"])

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _serializar(valor: Any) -> Any:
    if valor is None or isinstance(valor, (str, int, float, bool)):
        return valor
    return str(valor)
