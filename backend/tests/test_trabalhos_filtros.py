"""Testes de filtros, pesquisa, ordenação e paginação de trabalhos (nova estrutura)."""
import pytest


@pytest.fixture()
def especialidade_id(client):
    codigo = "FILT-ESP"
    resp = client.post("/especialidades", json={"codigo": codigo, "prazo_top": 7, "prazo_ok": 15})
    if resp.status_code == 201:
        return resp.json()["id"]
    existentes = client.get("/especialidades").json()
    return next(e["id"] for e in existentes if e["codigo"] == codigo)


def test_pesquisa_por_cliente(client):
    client.post("/trabalhos", json={"cliente": "ZZ Cliente Único Alpha", "referencia": "F-100", "itens": []})
    resp = client.get("/trabalhos", params={"q": "Único Alpha"})
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 1
    assert all("Único Alpha" in (t["cliente"] or "") for t in items)


def test_pesquisa_por_referencia(client):
    client.post("/trabalhos", json={"cliente": "Beta", "referencia": "REF-XYZ-999", "itens": []})
    resp = client.get("/trabalhos", params={"q": "XYZ-999"})
    items = resp.json()["items"]
    assert any(t["referencia"] == "REF-XYZ-999" for t in items)


def test_filtro_por_especialidade(client, especialidade_id):
    client.post(
        "/trabalhos",
        json={"cliente": "Com Esp", "itens": [{"especialidade_id": especialidade_id}]},
    )
    resp = client.get("/trabalhos", params={"especialidade_id": especialidade_id})
    items = resp.json()["items"]
    assert len(items) >= 1
    # O trabalho deve ter pelo menos um item com essa especialidade.
    for t in items:
        assert any(i["especialidade_id"] == especialidade_id for i in t["itens"])


def test_filtro_por_ano(client, especialidade_id):
    client.post(
        "/trabalhos",
        json={"cliente": "Ano 2015", "itens": [{"especialidade_id": especialidade_id, "data_adjudicacao": "2015-06-01"}]},
    )
    client.post(
        "/trabalhos",
        json={"cliente": "Ano 2099", "itens": [{"especialidade_id": especialidade_id, "data_adjudicacao": "2099-06-01"}]},
    )
    resp = client.get("/trabalhos", params={"ano": 2015})
    items = resp.json()["items"]
    assert len(items) >= 1
    for t in items:
        assert any((i["data_adjudicacao"] or "").startswith("2015") for i in t["itens"])


def test_filtro_por_estado_pendente(client, especialidade_id):
    client.post(
        "/trabalhos",
        json={
            "cliente": "Pendente Filtro",
            "itens": [{"especialidade_id": especialidade_id, "data_adjudicacao": "2022-01-01"}],
        },
    )
    resp = client.get("/trabalhos", params={"estado": "PENDENTE"})
    items = resp.json()["items"]
    assert len(items) >= 1
    # Cada trabalho devolvido tem algum item PENDENTE.
    for t in items:
        assert any(i["estado"] == "PENDENTE" for i in t["itens"])


def test_paginacao(client):
    for i in range(5):
        client.post("/trabalhos", json={"cliente": f"Pag Marker {i}", "referencia": f"PAG-{i}", "itens": []})
    resp = client.get("/trabalhos", params={"q": "Pag Marker", "page": 1, "page_size": 2})
    body = resp.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert len(body["items"]) == 2
    assert body["total"] >= 5

    resp2 = client.get("/trabalhos", params={"q": "Pag Marker", "page": 2, "page_size": 2})
    ids_p1 = {t["id"] for t in body["items"]}
    ids_p2 = {t["id"] for t in resp2.json()["items"]}
    assert ids_p1.isdisjoint(ids_p2)


def test_ordenacao_por_cliente_asc(client):
    client.post("/trabalhos", json={"cliente": "OrdTest BBB", "itens": []})
    client.post("/trabalhos", json={"cliente": "OrdTest AAA", "itens": []})
    resp = client.get(
        "/trabalhos",
        params={"q": "OrdTest", "order_by": "cliente", "order_dir": "asc"},
    )
    assert resp.status_code == 200
    clientes = [t["cliente"] for t in resp.json()["items"]]
    assert clientes == sorted(clientes)
