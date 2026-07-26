"""Classificação de status de ruptura (roadmap seção 6.3, issue #21)."""

from app.models.drp import StatusRuptura


def classificar_status_local(
    saldo: float, estoque_maximo: float, ponto_pedido: float, cobertura_dias: float, lead_time_dias: float
) -> StatusRuptura:
    """Classificação local (por elo), conforme a tabela da seção 6.3:

    | Status | Regra |
    |---|---|
    | Ruptura | Saldo = 0 |
    | Excesso | Saldo > Estoque Máximo |
    | Nível Adequado | Ponto de Pedido < Saldo <= Estoque Máximo |
    | Baixa Exposição a Ruptura | Saldo <= Ponto de Pedido e Cobertura >= Lead Time |
    | Elevada Exposição a Ruptura | Saldo <= Ponto de Pedido e Cobertura < Lead Time |
    """
    if saldo <= 0:
        return StatusRuptura.RUPTURA
    if saldo > estoque_maximo:
        return StatusRuptura.EXCESSO
    if saldo > ponto_pedido:
        return StatusRuptura.ADEQUADO
    if cobertura_dias >= lead_time_dias:
        return StatusRuptura.BAIXA_EXPOSICAO_RUPTURA
    return StatusRuptura.ELEVADA_EXPOSICAO_RUPTURA


def avaliar_ruptura_rede(necessidade_liquida_agregada_cd: float, saldo_disponivel_cd: float) -> bool:
    """Ruptura por DRP (roadmap seção 3.1): mesmo com o elo local em status
    adequado/baixa exposição, a rede aponta ruptura quando o CD supridor
    não tem saldo suficiente para cobrir a necessidade líquida agregada de
    todas as filiais que atende, dentro do lead time de transferência.

    Só faz sentido chamar esta função quando o status local já não é
    RUPTURA/EXCESSO/ELEVADA_EXPOSICAO_RUPTURA — o resultado, se True, deve
    *sobrescrever* o status local para RUPTURA_DRP.
    """
    return saldo_disponivel_cd < necessidade_liquida_agregada_cd
