"""Cálculo de Necessidade Líquida (roadmap seção 6.2, issue #20)."""


def calcular_necessidade_liquida(
    demanda_projetada: float,
    estoque_seguranca: float,
    estoque_disponivel: float,
    estoque_transito: float,
) -> float:
    """Necessidade Líquida = Demanda Projetada + Estoque Segurança −
    Estoque Disponível − Estoque em Trânsito.

    Positivo → há necessidade de ressuprimento (transferência ou compra).
    """
    return demanda_projetada + estoque_seguranca - estoque_disponivel - estoque_transito
