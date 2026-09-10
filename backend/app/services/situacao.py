"""Situação (ponto de situação / pagamento) de uma especialidade e do trabalho."""
from enum import Enum


class Situacao(str, Enum):
    EM_CURSO = "Em curso"
    FALTA_PAGAMENTO = "Falta pagamento"
    PAGO = "Pago"


# Ordem de gravidade: quanto MAIOR o número, mais "grave"/prioritário.
# Em curso é o pior, Pago é o melhor.
_GRAVIDADE = {
    Situacao.PAGO: 0,
    Situacao.FALTA_PAGAMENTO: 1,
    Situacao.EM_CURSO: 2,
}


def situacao_do_trabalho(situacoes: list[Situacao | None]) -> Situacao | None:
    """Devolve a situação "pior" (mais grave) entre as especialidades de um trabalho.

    Ignora especialidades sem situação. Se nenhuma tiver situação, devolve None.
    """
    definidas = [s for s in situacoes if s is not None]
    if not definidas:
        return None
    return max(definidas, key=lambda s: _GRAVIDADE[s])
