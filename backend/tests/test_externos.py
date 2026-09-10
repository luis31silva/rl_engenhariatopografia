"""Testes CRUD de Externos."""


def test_criar_e_listar_externo(client):
    resp = client.post("/externos", json={"nome": "Nicola"})
    assert resp.status_code == 201
    assert resp.json()["nome"] == "Nicola"

    nomes = [e["nome"] for e in client.get("/externos").json()]
    assert "Nicola" in nomes


def test_externo_total_ganho(client):
    # Cria um externo e dois itens de trabalho com valor_externo associado.
    ext = client.post("/externos", json={"nome": "Externo Totais"}).json()
    client.post(
        "/trabalhos",
        json={"cliente": "T1", "itens": [{"externo_id": ext["id"], "valor_externo": "100.00"}]},
    )
    client.post(
        "/trabalhos",
        json={"cliente": "T2", "itens": [{"externo_id": ext["id"], "valor_externo": "50.00"}]},
    )

    lista = client.get("/externos").json()
    alvo = next(e for e in lista if e["id"] == ext["id"])
    assert float(alvo["total_ganho"]) == 150.0
    # num_trabalhos aqui conta itens associados ao externo.
    assert alvo["num_trabalhos"] == 2


def test_nome_duplicado_devolve_409(client):
    client.post("/externos", json={"nome": "Jorge"})
    resp = client.post("/externos", json={"nome": "Jorge"})
    assert resp.status_code == 409


def test_atualizar_externo(client):
    criado = client.post("/externos", json={"nome": "Sergio"}).json()
    resp = client.put(f"/externos/{criado['id']}", json={"nome": "Sérgio"})
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Sérgio"


def test_apagar_externo(client):
    criado = client.post("/externos", json={"nome": "Mário"}).json()
    assert client.delete(f"/externos/{criado['id']}").status_code == 204
    assert client.get(f"/externos/{criado['id']}").status_code == 404
