"""Testes de integração do endpoint de alertas de prazo (nova estrutura)."""
from datetime import date, timedelta

import pytest


@pytest.fixture()
def especialidade_curta(client):
    """Especialidade com prazo_ok curto (5 dias)."""
    codigo = "ALERTA-ESP"
    resp = client.post("/especialidades", json={"codigo": codigo, "prazo_top": 2, "prazo_ok": 5})
    if resp.status_code == 201:
        return resp.json()["id"]
    existentes = client.get("/especialidades").json()
    return next(e["id"] for e in existentes if e["codigo"] == codigo)


def _iso(d: date) -> str:
    return d.isoformat()


def test_alerta_ultrapassado(client, especialidade_curta):
    hoje = date.today()
    client.post(
        "/trabalhos",
        json={
            "cliente": "Alerta Atrasado",
            "referencia": "ALERTA-ATR",
            "itens": [
                {"especialidade_id": especialidade_curta, "data_adjudicacao": _iso(hoje - timedelta(days=10))}
            ],
        },
    )
    resp = client.get("/trabalhos/alertas")
    assert resp.status_code == 200
    alerta = next((a for a in resp.json() if a["referencia"] == "ALERTA-ATR"), None)
    assert alerta is not None
    assert alerta["nivel"] == "ULTRAPASSADO"
    assert alerta["dias_restantes"] < 0
    assert "item_id" in alerta and "trabalho_id" in alerta


def test_alerta_em_risco(client, especialidade_curta):
    hoje = date.today()
    client.post(
        "/trabalhos",
        json={
            "cliente": "Alerta Risco",
            "referencia": "ALERTA-RSC",
            "itens": [
                {"especialidade_id": especialidade_curta, "data_adjudicacao": _iso(hoje - timedelta(days=4))}
            ],
        },
    )
    resp = client.get("/trabalhos/alertas")
    alerta = next((a for a in resp.json() if a["referencia"] == "ALERTA-RSC"), None)
    assert alerta is not None
    assert alerta["nivel"] == "EM_RISCO"


def test_item_entregue_nao_gera_alerta(client, especialidade_curta):
    hoje = date.today()
    client.post(
        "/trabalhos",
        json={
            "cliente": "Alerta Entregue",
            "referencia": "ALERTA-ENT",
            "itens": [
                {
                    "especialidade_id": especialidade_curta,
                    "data_adjudicacao": _iso(hoje - timedelta(days=10)),
                    "data_entrega": _iso(hoje - timedelta(days=8)),
                }
            ],
        },
    )
    resp = client.get("/trabalhos/alertas")
    assert all(a["referencia"] != "ALERTA-ENT" for a in resp.json())


def test_item_com_folga_nao_gera_alerta(client, especialidade_curta):
    hoje = date.today()
    client.post(
        "/trabalhos",
        json={
            "cliente": "Alerta Folga",
            "referencia": "ALERTA-FLG",
            "itens": [{"especialidade_id": especialidade_curta, "data_adjudicacao": _iso(hoje)}],
        },
    )
    resp = client.get("/trabalhos/alertas")
    assert all(a["referencia"] != "ALERTA-FLG" for a in resp.json())


def test_alertas_requer_autenticacao(anon_client):
    assert anon_client.get("/trabalhos/alertas").status_code == 401
