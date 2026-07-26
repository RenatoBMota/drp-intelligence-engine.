"""Otimização de rede via Programação Linear (roadmap seção 6.5/7, issue
#30): problema de transporte clássico — aloca o excedente de cada elo
doador aos elos com necessidade, minimizando o custo total de transporte,
respeitando a capacidade de cada rota.

"Multiobjetivo" (citado no roadmap): o segundo objetivo — minimizar
compra externa — entra como uma rota fictícia "EXTERNO→destino" com custo
alto e capacidade ilimitada. Isso garante que o problema sempre tem
solução viável (nem toda demanda precisa ter rota real) e faz o otimizador
preferir transferência a compra sempre que o custo de transporte for menor
que a penalidade — generalizando para N elos/rotas simultâneas a decisão
binária que o Motor DRP (Fase 3) toma elo a elo.
"""

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linprog

EXTERNO = "EXTERNO"
CUSTO_COMPRA_EXTERNA_PADRAO = 1000.0


@dataclass
class RotaDisponivel:
    origem: str
    destino: str
    capacidade: float
    custo_unitario: float
    id: str | None = None


@dataclass
class FluxoAlocado:
    origem: str
    destino: str
    quantidade: float
    custo_unitario: float


@dataclass
class ResultadoOtimizacao:
    sucesso: bool
    fluxos: list[FluxoAlocado] = field(default_factory=list)
    custo_total: float = 0.0
    quantidade_via_rede: float = 0.0
    quantidade_via_compra_externa: float = 0.0
    mensagem: str = ""


def otimizar_transferencias(
    ofertas: dict[str, float],
    demandas: dict[str, float],
    rotas: list[RotaDisponivel],
    custo_compra_externa: float = CUSTO_COMPRA_EXTERNA_PADRAO,
) -> ResultadoOtimizacao:
    demandas = {elo: qtd for elo, qtd in demandas.items() if qtd > 0}
    ofertas = {elo: qtd for elo, qtd in ofertas.items() if qtd > 0}

    if not demandas:
        return ResultadoOtimizacao(sucesso=True, mensagem="Nenhuma necessidade a resolver.")

    rotas_validas = [r for r in rotas if r.origem in ofertas and r.destino in demandas]
    variaveis: list[tuple[str, str, float, float]] = [
        (r.origem, r.destino, r.capacidade, r.custo_unitario) for r in rotas_validas
    ]
    # Uma variável "compra externa" por destino, capacidade ilimitada.
    idx_externo_por_destino: dict[str, int] = {}
    for destino in demandas:
        idx_externo_por_destino[destino] = len(variaveis)
        variaveis.append((EXTERNO, destino, float("inf"), custo_compra_externa))

    n = len(variaveis)
    custo = np.array([v[3] for v in variaveis])

    # Restrição de oferta: para cada elo doador, soma das saídas <= excedente.
    origens = list(ofertas.keys())
    A_ub = np.zeros((len(origens), n))
    b_ub = np.array([ofertas[o] for o in origens])
    for linha, origem in enumerate(origens):
        for col, (var_origem, _destino, _cap, _custo) in enumerate(variaveis):
            if var_origem == origem:
                A_ub[linha, col] = 1

    # Restrição de demanda: para cada destino, soma das entradas == necessidade.
    destinos = list(demandas.keys())
    A_eq = np.zeros((len(destinos), n))
    b_eq = np.array([demandas[d] for d in destinos])
    for linha, destino in enumerate(destinos):
        for col, (_origem, var_destino, _cap, _custo) in enumerate(variaveis):
            if var_destino == destino:
                A_eq[linha, col] = 1

    bounds = [(0, None if cap == float("inf") else cap) for _o, _d, cap, _c in variaveis]

    resultado = linprog(custo, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method="highs")

    if not resultado.success:
        return ResultadoOtimizacao(sucesso=False, mensagem=resultado.message)

    fluxos = []
    via_rede = 0.0
    via_externo = 0.0
    for (origem, destino, _cap, custo_unit), quantidade in zip(variaveis, resultado.x):
        if quantidade < 1e-6:
            continue
        fluxos.append(FluxoAlocado(origem=origem, destino=destino, quantidade=float(quantidade), custo_unitario=custo_unit))
        if origem == EXTERNO:
            via_externo += quantidade
        else:
            via_rede += quantidade

    return ResultadoOtimizacao(
        sucesso=True,
        fluxos=fluxos,
        custo_total=float(resultado.fun),
        quantidade_via_rede=via_rede,
        quantidade_via_compra_externa=via_externo,
        mensagem="ok",
    )
