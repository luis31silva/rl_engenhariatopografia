"""Classificação de desempenho de um trabalho (TOP / OK / MAU).

Replica a lógica original da folha de cálculo:

    IF((entrega - adjudicacao) < prazo_top, "TOP",
       IF((entrega - adjudicacao) < prazo_ok, "OK", "MAU"))

Extensões:
- Sem data de entrega -> "PENDENTE" (o trabalho ainda não foi concluído).
- Sem datas suficientes ou sem especialidade -> None (não classificável).
"""
from datetime import date
from enum import Enum


class Estado(str, Enum):
    TOP = "TOP"
    OK = "OK"
    MAU = "MAU"
    PENDENTE = "PENDENTE"


def classificar(
    data_adjudicacao: date | None,
    data_entrega: date | None,
    prazo_top: int | None,
    prazo_ok: int | None,
) -> Estado | None:
    """Devolve o estado de desempenho de um trabalho.

    - Se não houver data de adjudicação, não é possível medir -> None.
    - Se não houver data de entrega -> PENDENTE.
    - Caso contrário, compara os dias decorridos com os prazos da especialidade.
    """
    if data_adjudicacao is None:
        return None

    if data_entrega is None:
        return Estado.PENDENTE

    dias = (data_entrega - data_adjudicacao).days

    # Sem prazos definidos na especialidade, não há critério de comparação.
    if prazo_top is None and prazo_ok is None:
        return None

    top = prazo_top if prazo_top is not None else 0
    ok = prazo_ok if prazo_ok is not None else top

    if dias < top:
        return Estado.TOP
    if dias < ok:
        return Estado.OK
    return Estado.MAU


# Classificação do PRAZO MÉDIO de uma especialidade (nomes orientados ao
# desempenho, pedidos pelo utilizador). Mesma lógica de intervalos que `classificar`.
EXCELENTE = "Excelente"
BOM = "Bom"
MAU = "Mau"


def classificar_media(
    prazo_medio: float | None,
    prazo_top: int | None,
    prazo_ok: int | None,
) -> str | None:
    """Classifica o prazo médio de uma especialidade em Excelente / Bom / Mau.

    - prazo_medio < prazo_top -> Excelente
    - prazo_medio < prazo_ok  -> Bom
    - caso contrário          -> Mau
    Devolve None se não houver média ou se não houver prazos definidos.
    """
    if prazo_medio is None:
        return None
    if prazo_top is None and prazo_ok is None:
        return None

    top = prazo_top if prazo_top is not None else 0
    ok = prazo_ok if prazo_ok is not None else top

    if prazo_medio < top:
        return EXCELENTE
    if prazo_medio < ok:
        return BOM
    return MAU
