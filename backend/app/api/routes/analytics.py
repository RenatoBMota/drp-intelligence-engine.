"""Endpoints da Torre de Controle (Fase 5): Control Tower, indicadores e
relatórios herdados do Systock, exportação e governança/saneamento."""

import io
import uuid
from dataclasses import asdict

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.analytics import control_tower, governanca, indicadores, relatorios
from app.analytics.export import gerar_excel
from app.api.deps import DbSession
from app.schemas.cadastro import SkuRead
from app.schemas.drp import OrdemCompraRead, OrdemTransferenciaRead, StatusEstoqueRead
from app.schemas.forecast import ClassificacaoItemRead

router = APIRouter(tags=["torre-de-controle"])


# ---------- Control Tower (issue #35, + indicadores da issue #34 trazidos para cá) ----------


@router.get("/control-tower/resumo")
async def resumo_executivo(db: DbSession) -> dict:
    resumo = await control_tower.resumo_executivo(db)
    return {
        "contagem_por_status": resumo.contagem_por_status,
        "necessidade_liquida_total_aberta": resumo.necessidade_liquida_total_aberta,
        "ordens_transferencia_pendentes": resumo.ordens_transferencia_pendentes,
        "ordens_compra_pendentes": resumo.ordens_compra_pendentes,
        "taxa_resolucao_rede": asdict(resumo.taxa_resolucao_rede),
        "lead_time_efetivo": asdict(resumo.lead_time_efetivo),
    }


# ---------- Indicadores herdados do Systock (issue #36) ----------


@router.get("/indicadores/status-mensal")
async def status_mensal(db: DbSession) -> list[dict]:
    return await indicadores.status_mensal(db)


@router.get("/indicadores/no-moving", response_model=list[SkuRead])
async def no_moving(db: DbSession, dias: int = 90):
    return await indicadores.no_moving(db, dias=dias)


@router.get("/indicadores/status-produto", response_model=list[StatusEstoqueRead])
async def status_produto(db: DbSession, sku_id: uuid.UUID | None = None):
    return await indicadores.status_produto(db, sku_id=sku_id)


@router.get("/indicadores/perda-venda-ruptura")
async def perda_venda_ruptura(db: DbSession) -> dict:
    return asdict(await indicadores.perda_venda_ruptura(db))


@router.get("/indicadores/analise-compradores")
async def analise_compradores(db: DbSession) -> dict:
    resultado = await indicadores.analise_compradores(db)
    return {comprador: dict(categorias) for comprador, categorias in resultado.items()}


# ---------- Relatórios herdados do Systock (issue #37) ----------


@router.get("/relatorios/ruptura-geral")
async def ruptura_geral(db: DbSession) -> dict:
    return await relatorios.ruptura_geral(db)


@router.get("/relatorios/excesso-estoque", response_model=list[StatusEstoqueRead])
async def excesso_estoque(db: DbSession):
    return await relatorios.excesso_estoque(db)


@router.get("/relatorios/movimentacao-produtos")
async def movimentacao_produtos(db: DbSession, dias: int = 90) -> list[dict]:
    return await relatorios.movimentacao_produtos(db, dias=dias)


@router.get("/relatorios/curva-abc-pqr", response_model=list[ClassificacaoItemRead])
async def curva_abc_pqr(db: DbSession):
    return await relatorios.curva_abc_pqr(db)


@router.get("/relatorios/sugestao-inativacao", response_model=list[SkuRead])
async def sugestao_inativacao(db: DbSession, dias: int = 90):
    return await relatorios.sugestao_inativacao(db, dias=dias)


@router.get("/relatorios/cobertura-estoque")
async def cobertura_estoque(db: DbSession) -> list[dict]:
    itens = await relatorios.cobertura_estoque(db)
    return [asdict(item) | {"sku_id": str(item.sku_id), "cd_id": str(item.cd_id) if item.cd_id else None,
                             "filial_id": str(item.filial_id) if item.filial_id else None}
            for item in itens]


@router.get("/relatorios/pedidos-pendentes")
async def pedidos_pendentes(db: DbSession) -> dict:
    resultado = await relatorios.pedidos_pendentes(db)
    return {
        "transferencias": [OrdemTransferenciaRead.model_validate(o).model_dump(mode="json") for o in resultado["transferencias"]],
        "compras": [OrdemCompraRead.model_validate(o).model_dump(mode="json") for o in resultado["compras"]],
    }


@router.get("/relatorios/otif")
async def indicador_otif(db: DbSession) -> dict:
    return asdict(await relatorios.indicador_otif(db))


@router.get("/relatorios/ruptura-geral/exportar")
async def exportar_ruptura_geral(db: DbSession) -> StreamingResponse:
    dados = await relatorios.ruptura_geral(db)
    linhas = [{"status": status, "quantidade": qtd} for status, qtd in dados.items()]
    conteudo = gerar_excel(linhas, "Ruptura Geral")
    return StreamingResponse(
        io.BytesIO(conteudo),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=ruptura_geral.xlsx"},
    )


@router.get("/relatorios/pedidos-pendentes/exportar")
async def exportar_pedidos_pendentes(db: DbSession) -> StreamingResponse:
    resultado = await relatorios.pedidos_pendentes(db)
    linhas = [
        {
            "tipo": "TRANSFERENCIA", "sku_id": str(o.sku_id), "quantidade": float(o.quantidade),
            "status": o.status.value, "data_prevista": o.data_chegada_estimada.isoformat(),
        }
        for o in resultado["transferencias"]
    ] + [
        {
            "tipo": "COMPRA", "sku_id": str(o.sku_id), "quantidade": float(o.quantidade),
            "status": o.status.value, "data_prevista": o.data_previsao.isoformat(),
        }
        for o in resultado["compras"]
    ]
    conteudo = gerar_excel(linhas, "Pedidos Pendentes")
    return StreamingResponse(
        io.BytesIO(conteudo),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=pedidos_pendentes.xlsx"},
    )


# ---------- Governança e Saneamento (issue #40) ----------


@router.get("/governanca/saneamento")
async def saneamento(db: DbSession, dias_atraso_critico: int = 30) -> dict:
    resultado = await governanca.pedidos_para_saneamento(db, dias_atraso_critico=dias_atraso_critico)
    return {
        "transferencias": [OrdemTransferenciaRead.model_validate(o).model_dump(mode="json") for o in resultado["transferencias"]],
        "compras": [OrdemCompraRead.model_validate(o).model_dump(mode="json") for o in resultado["compras"]],
    }
