"""Testes CRUD de Especialidades."""


def test_criar_e_obter_especialidade(client):
    resp = client.post(
        "/especialidades",
        json={"codigo": "LEVTOP", "descricao": "Levantamento topográfico", "prazo_top": 7, "prazo_ok": 15},
    )
    assert resp.status_code == 201
    criado = resp.json()
    assert criado["codigo"] == "LEVTOP"
    assert criado["prazo_top"] == 7
    assert criado["prazo_ok"] == 15
    assert "id" in criado

    resp = client.get(f"/especialidades/{criado['id']}")
    assert resp.status_code == 200
    assert resp.json()["codigo"] == "LEVTOP"


def test_listar_especialidades(client):
    client.post("/especialidades", json={"codigo": "DEST", "prazo_top": 5, "prazo_ok": 10})
    resp = client.get("/especialidades")
    assert resp.status_code == 200
    codigos = [e["codigo"] for e in resp.json()]
    assert "DEST" in codigos


def test_codigo_duplicado_devolve_409(client):
    client.post("/especialidades", json={"codigo": "PIP", "prazo_top": 3, "prazo_ok": 6})
    resp = client.post("/especialidades", json={"codigo": "PIP", "prazo_top": 3, "prazo_ok": 6})
    assert resp.status_code == 409


def test_atualizar_especialidade(client):
    criado = client.post("/especialidades", json={"codigo": "EST", "prazo_top": 4, "prazo_ok": 8}).json()
    resp = client.put(f"/especialidades/{criado['id']}", json={"prazo_ok": 20})
    assert resp.status_code == 200
    assert resp.json()["prazo_ok"] == 20
    assert resp.json()["prazo_top"] == 4  # inalterado


def test_apagar_especialidade(client):
    criado = client.post("/especialidades", json={"codigo": "ELE", "prazo_top": 2, "prazo_ok": 5}).json()
    resp = client.delete(f"/especialidades/{criado['id']}")
    assert resp.status_code == 204
    assert client.get(f"/especialidades/{criado['id']}").status_code == 404


def test_obter_inexistente_devolve_404(client):
    assert client.get("/especialidades/999999").status_code == 404


def test_prazo_negativo_rejeitado(client):
    resp = client.post("/especialidades", json={"codigo": "XPTO", "prazo_top": -1, "prazo_ok": 5})
    assert resp.status_code == 422
