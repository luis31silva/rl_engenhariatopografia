"""Testes unitários da lógica de alertas de prazo."""
from datetime import date

from app.services.alertas import NivelAlerta, avaliar_alerta

HOJE = date(2024, 6, 15)


def test_ultrapassado_quando_dias_excedem_prazo():
    # Adjudicado há 20 dias, prazo_ok=15 -> ultrapassado
    r = avaliar_alerta(date(2024, 5, 26), None, prazo_ok=15, hoje=HOJE)
    assert r is not None
    assert r[0] == NivelAlerta.ULTRAPASSADO
    assert r[1] < 0


def test_em_risco_quando_perto_do_prazo():
    # Adjudicado há 13 dias, prazo_ok=15 -> restam 2 dias -> em risco (margem 3)
    r = avaliar_alerta(date(2024, 6, 2), None, prazo_ok=15, hoje=HOJE)
    assert r is not None
    assert r[0] == NivelAlerta.EM_RISCO
    assert r[1] == 2


def test_sem_alerta_quando_ha_folga():
    # Adjudicado há 2 dias, prazo_ok=15 -> restam 13 dias -> sem alerta
    r = avaliar_alerta(date(2024, 6, 13), None, prazo_ok=15, hoje=HOJE)
    assert r is None


def test_sem_alerta_quando_ja_entregue():
    r = avaliar_alerta(date(2024, 5, 1), date(2024, 5, 10), prazo_ok=15, hoje=HOJE)
    assert r is None


def test_sem_alerta_sem_adjudicacao():
    assert avaliar_alerta(None, None, prazo_ok=15, hoje=HOJE) is None


def test_sem_alerta_sem_prazo():
    assert avaliar_alerta(date(2024, 5, 1), None, prazo_ok=None, hoje=HOJE) is None
    assert avaliar_alerta(date(2024, 5, 1), None, prazo_ok=0, hoje=HOJE) is None


def test_limite_exato_do_prazo_e_em_risco():
    # Adjudicado há exatamente 15 dias, prazo_ok=15 -> restam 0 -> em risco (0 <= margem)
    r = avaliar_alerta(date(2024, 5, 31), None, prazo_ok=15, hoje=HOJE)
    assert r is not None
    assert r[0] == NivelAlerta.EM_RISCO
    assert r[1] == 0
