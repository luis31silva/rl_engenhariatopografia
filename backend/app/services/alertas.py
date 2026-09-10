"""Deteção de trabalhos em risco de prazo (por entregar)."""
from datetime import date
from enum import Enum


class NivelAlerta(str, Enum):
    EM_RISCO = "EM_RISCO"      # a aproximar-se do prazo limite
    ULTRAPASSADO = "ULTRAPASSADO"  # já passou o prazo limite


# Margem (em dias) antes do prazo limite a partir da qual um trabalho é "em risco".
MARGEM_RISCO_DIAS = 3


def avaliar_alerta(
    data_adjudicacao: date | None,
    data_entrega: date | None,
    prazo_ok: int | None,
    hoje: date,
    margem: int = MARGEM_RISCO_DIAS,
) -> tuple[NivelAlerta, int] | None:
    """Avalia se um trabalho por entregar está em risco de prazo.

    Devolve (nível, dias_restantes) ou None quando não aplicável.
    - Só considera trabalhos POR ENTREGAR (sem data_entrega).
    - Requer data_adjudicacao e prazo_ok (> 0) para haver critério.
    - dias_restantes = prazo_ok - dias_decorridos (negativo = em atraso).
    """
    # Já entregue: não há alerta.
    if data_entrega is not None:
        return None
    # Sem dados para avaliar.
    if data_adjudicacao is None or not prazo_ok:
        return None

    dias_decorridos = (hoje - data_adjudicacao).days
    dias_restantes = prazo_ok - dias_decorridos

    if dias_restantes < 0:
        return (NivelAlerta.ULTRAPASSADO, dias_restantes)
    if dias_restantes <= margem:
        return (NivelAlerta.EM_RISCO, dias_restantes)
    return None
