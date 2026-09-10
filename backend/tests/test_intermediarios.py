"""Testes CRUD de Intermediários."""


def test_criar_intermediario_com_valor(client):
    resp = client.post("/intermediarios", json={"nome": "Arqt. Gil", "valor": "150.00"})
    assert resp.status_code == 201
    criado = resp.json()
    assert criado["nome"] == "Arqt. Gil"
    assert str(criado["valor"]) in ("150.0", "150.00")


def test_criar_intermediario_sem_valor(client):
    resp = client.post("/intermediarios", json={"nome": "Eng. Vitor CMT"})
    assert resp.status_code == 201
    assert resp.json()["valor"] is None


def test_nome_duplicado_devolve_409(client):
    client.post("/intermediarios", json={"nome": "Requinte"})
    resp = client.post("/intermediarios", json={"nome": "Requinte"})
    assert resp.status_code == 409


def test_atualizar_intermediario(client):
    criado = client.post("/intermediarios", json={"nome": "Pedro Sol."}).json()
    resp = client.put(f"/intermediarios/{criado['id']}", json={"valor": "75.50"})
    assert resp.status_code == 200
    assert str(resp.json()["valor"]) in ("75.5", "75.50")


def test_apagar_intermediario(client):
    criado = client.post("/intermediarios", json={"nome": "Arqt. Eurico"}).json()
    assert client.delete(f"/intermediarios/{criado['id']}").status_code == 204
    assert client.get(f"/intermediarios/{criado['id']}").status_code == 404


def test_nome_vazio_rejeitado(client):
    resp = client.post("/intermediarios", json={"nome": ""})
    assert resp.status_code == 422


def test_intermediario_estatisticas(client):
    inter = client.post("/intermediarios", json={"nome": "Interm Stats"}).json()
    # Dois trabalhos deste intermediário: um de 300 (100+200), outro de 100.
    client.post(
        "/trabalhos",
        json={
            "cliente": "T1",
            "intermediario_id": inter["id"],
            "itens": [{"valor": "100.00"}, {"valor": "200.00"}],
        },
    )
    client.post(
        "/trabalhos",
        json={"cliente": "T2", "intermediario_id": inter["id"], "itens": [{"valor": "100.00"}]},
    )

    lista = client.get("/intermediarios").json()
    alvo = next(i for i in lista if i["id"] == inter["id"])
    assert alvo["num_trabalhos"] == 2
    assert float(alvo["valor_total"]) == 400.0
    # Média por trabalho = 400 / 2 = 200.
    assert float(alvo["valor_medio"]) == 200.0


def test_intermediario_estatisticas_ano_atual(client):
    from datetime import date

    ano = date.today().year
    inter = client.post("/intermediarios", json={"nome": "Interm Ano"}).json()
    # Trabalho com item deste ano (150) e item de um ano antigo (999).
    client.post(
        "/trabalhos",
        json={
            "cliente": "TA",
            "intermediario_id": inter["id"],
            "itens": [
                {"valor": "150.00", "data_adjudicacao": f"{ano}-03-01"},
                {"valor": "999.00", "data_adjudicacao": "2016-03-01"},
            ],
        },
    )

    alvo = next(i for i in client.get("/intermediarios").json() if i["id"] == inter["id"])
    # Só o item deste ano conta para valor_ano.
    assert float(alvo["valor_ano"]) == 150.0
    assert alvo["num_trabalhos_ano"] == 1
