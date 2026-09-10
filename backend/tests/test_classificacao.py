"""Testes unitários da função de classificação TOP/OK/MAU."""
from datetime import date

from app.services.classificacao import Estado, classificar


def test_top_quando_entrega_dentro_do_prazo_top():
    # 5 dias, prazo_top=7 -> TOP
    r = classificar(date(2024, 1, 1), date(2024, 1, 6), prazo_top=7, prazo_ok=15)
    assert r == Estado.TOP


def test_ok_quando_entre_top_e_ok():
    # 10 dias, prazo_top=7, prazo_ok=15 -> OK
    r = classificar(date(2024, 1, 1), date(2024, 1, 11), prazo_top=7, prazo_ok=15)
    assert r == Estado.OK


def test_mau_quando_ultrapassa_prazo_ok():
    # 20 dias, prazo_ok=15 -> MAU
    r = classificar(date(2024, 1, 1), date(2024, 1, 21), prazo_top=7, prazo_ok=15)
    assert r == Estado.MAU


def test_pendente_sem_data_entrega():
    r = classificar(date(2024, 1, 1), None, prazo_top=7, prazo_ok=15)
    assert r == Estado.PENDENTE


def test_none_sem_data_adjudicacao():
    r = classificar(None, date(2024, 1, 10), prazo_top=7, prazo_ok=15)
    assert r is None


def test_none_sem_prazos_definidos():
    r = classificar(date(2024, 1, 1), date(2024, 1, 10), prazo_top=None, prazo_ok=None)
    assert r is None


def test_limite_exato_top_conta_como_ok():
    # dias == prazo_top não é "< prazo_top", logo cai em OK (como na planilha)
    r = classificar(date(2024, 1, 1), date(2024, 1, 8), prazo_top=7, prazo_ok=15)
    assert r == Estado.OK


def test_limite_exato_ok_conta_como_mau():
    # dias == prazo_ok não é "< prazo_ok", logo MAU
    r = classificar(date(2024, 1, 1), date(2024, 1, 16), prazo_top=7, prazo_ok=15)
    assert r == Estado.MAU


def test_entrega_no_mesmo_dia_e_top():
    r = classificar(date(2024, 1, 1), date(2024, 1, 1), prazo_top=7, prazo_ok=15)
    assert r == Estado.TOP
