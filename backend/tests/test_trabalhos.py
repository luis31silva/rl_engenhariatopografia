"""Testes CRUD da entidade Trabalho (com itens/especialidades) e estado por item."""
import pytest


@pytest.fixture()
def especialidade_id(client):
    """Cria (ou reutiliza) uma especialidade com prazos e devolve o seu id."""
    codigo = "LEVTOP-T3"
    resp = client.post("/especialidades", json={"codigo": codigo, "prazo_top": 7, "prazo_ok": 15})
    if resp.status_code == 201:
        return resp.json()["id"]
    existentes = client.get("/especialidades").json()
    return next(e["id"] for e in existentes if e["codigo"] == codigo)


def test_criar_trabalho_sem_itens(client):
    resp = client.post("/trabalhos", json={"cliente": "Sr. Almerindo", "itens": []})
    assert resp.status_code == 201
    body = resp.json()
    assert body["cliente"] == "Sr. Almerindo"
    assert body["itens"] == []
    assert float(body["valor_total"]) == 0


def test_criar_trabalho_com_item_estado_top(client, especialidade_id):
    resp = client.post(
        "/trabalhos",
        json={
            "referencia": "001.24",
            "cliente": "D. Elisabete",
            "itens": [
                {
                    "especialidade_id": especialidade_id,
                    "valor": "380.00",
                    "data_adjudicacao": "2024-01-01",
                    "data_entrega": "2024-01-05",
                }
            ],
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["itens"]) == 1
    item = body["itens"][0]
    assert item["estado"] == "TOP"
    assert item["especialidade_codigo"] == "LEVTOP-T3"
    assert float(body["valor_total"]) == 380.0


def test_valor_total_soma_itens(client, especialidade_id):
    resp = client.post(
        "/trabalhos",
        json={
            "cliente": "Multi",
            "itens": [
                {"especialidade_id": especialidade_id, "valor": "200.00"},
                {"especialidade_id": especialidade_id, "valor": "50.00"},
            ],
        },
    )
    body = resp.json()
    assert len(body["itens"]) == 2
    assert float(body["valor_total"]) == 250.0


def test_item_estado_pendente_sem_entrega(client, especialidade_id):
    resp = client.post(
        "/trabalhos",
        json={
            "cliente": "Sr. Pena",
            "itens": [{"especialidade_id": especialidade_id, "data_adjudicacao": "2024-01-01"}],
        },
    )
    assert resp.json()["itens"][0]["estado"] == "PENDENTE"


def test_item_estado_mau_quando_atrasado(client, especialidade_id):
    resp = client.post(
        "/trabalhos",
        json={
            "cliente": "Sr. Sano",
            "itens": [
                {
                    "especialidade_id": especialidade_id,
                    "data_adjudicacao": "2024-01-01",
                    "data_entrega": "2024-02-01",
                }
            ],
        },
    )
    assert resp.json()["itens"][0]["estado"] == "MAU"


def test_data_entrega_antes_de_adjudicacao_rejeitada(client):
    resp = client.post(
        "/trabalhos",
        json={
            "cliente": "X",
            "itens": [{"data_adjudicacao": "2024-01-10", "data_entrega": "2024-01-01"}],
        },
    )
    assert resp.status_code == 422


def test_especialidade_inexistente_rejeitada(client):
    resp = client.post(
        "/trabalhos",
        json={"cliente": "Y", "itens": [{"especialidade_id": 999999}]},
    )
    assert resp.status_code == 422


def test_atualizar_trabalho_substitui_itens(client, especialidade_id):
    criado = client.post(
        "/trabalhos",
        json={
            "cliente": "Sr. Hélder",
            "itens": [{"especialidade_id": especialidade_id, "data_adjudicacao": "2024-01-01"}],
        },
    ).json()
    assert criado["itens"][0]["estado"] == "PENDENTE"

    resp = client.put(
        f"/trabalhos/{criado['id']}",
        json={
            "itens": [
                {
                    "especialidade_id": especialidade_id,
                    "data_adjudicacao": "2024-01-01",
                    "data_entrega": "2024-01-04",
                }
            ]
        },
    )
    assert resp.status_code == 200
    assert resp.json()["itens"][0]["estado"] == "TOP"


def test_atualizar_dados_comuns_mantem_itens(client, especialidade_id):
    criado = client.post(
        "/trabalhos",
        json={"cliente": "Antes", "itens": [{"especialidade_id": especialidade_id, "valor": "10"}]},
    ).json()
    resp = client.put(f"/trabalhos/{criado['id']}", json={"cliente": "Depois"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["cliente"] == "Depois"
    assert len(body["itens"]) == 1  # itens preservados


def test_obter_e_apagar_trabalho(client):
    criado = client.post("/trabalhos", json={"cliente": "Sr. Berto", "itens": []}).json()
    assert client.get(f"/trabalhos/{criado['id']}").status_code == 200
    assert client.delete(f"/trabalhos/{criado['id']}").status_code == 204
    assert client.get(f"/trabalhos/{criado['id']}").status_code == 404


def test_listar_trabalhos(client):
    client.post("/trabalhos", json={"cliente": "Cliente Lista", "itens": []})
    resp = client.get("/trabalhos")
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body and "total" in body
    assert any(t["cliente"] == "Cliente Lista" for t in body["items"])


def test_proxima_referencia(client):
    from datetime import date

    ano2 = date.today().strftime("%y")
    # Cria um trabalho com número alto no ano atual.
    client.post("/trabalhos", json={"referencia": f"500.{ano2}", "cliente": "Ref Base", "itens": []})
    resp = client.get("/trabalhos/proxima-referencia")
    assert resp.status_code == 200
    ref = resp.json()["referencia"]
    # Deve ser um número > 500 no formato NNN.AA do ano atual.
    assert ref.endswith(f".{ano2}")
    numero = int(ref.split(".")[0])
    assert numero >= 501


def test_situacao_por_item_e_do_trabalho(client, especialidade_id):
    # Trabalho com 2 especialidades: uma "Pago", outra "Em curso".
    resp = client.post(
        "/trabalhos",
        json={
            "cliente": "Sit Trabalho",
            "itens": [
                {"especialidade_id": especialidade_id, "situacao": "Pago"},
                {"especialidade_id": especialidade_id, "situacao": "Em curso"},
            ],
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    # A situação do trabalho é a "pior": Em curso.
    assert body["situacao_trabalho"] == "Em curso"
    assert {i["situacao"] for i in body["itens"]} == {"Pago", "Em curso"}


def test_situacao_todos_aplica_a_todas(client, especialidade_id):
    criado = client.post(
        "/trabalhos",
        json={
            "cliente": "Aplicar Todos",
            "itens": [
                {"especialidade_id": especialidade_id, "situacao": "Em curso"},
                {"especialidade_id": especialidade_id, "situacao": "Falta pagamento"},
            ],
        },
    ).json()

    resp = client.put(f"/trabalhos/{criado['id']}", json={"situacao_todos": "Pago"})
    assert resp.status_code == 200
    body = resp.json()
    assert all(i["situacao"] == "Pago" for i in body["itens"])
    assert body["situacao_trabalho"] == "Pago"


def test_editar_situacao_de_uma_especialidade_nao_afeta_outras(client, especialidade_id):
    criado = client.post(
        "/trabalhos",
        json={
            "cliente": "Uma Especialidade",
            "itens": [
                {"especialidade_id": especialidade_id, "situacao": "Em curso"},
                {"especialidade_id": especialidade_id, "situacao": "Em curso"},
            ],
        },
    ).json()

    # Substitui os itens: a primeira passa a Pago, a segunda mantém Em curso.
    resp = client.put(
        f"/trabalhos/{criado['id']}",
        json={
            "itens": [
                {"especialidade_id": especialidade_id, "situacao": "Pago"},
                {"especialidade_id": especialidade_id, "situacao": "Em curso"},
            ]
        },
    )
    body = resp.json()
    situacoes = [i["situacao"] for i in body["itens"]]
    assert "Pago" in situacoes and "Em curso" in situacoes
    # O trabalho continua "Em curso" (pior).
    assert body["situacao_trabalho"] == "Em curso"


def test_filtro_por_situacao(client, especialidade_id):
    client.post(
        "/trabalhos",
        json={
            "cliente": "Filtro Falta Pag",
            "referencia": "SIT-001",
            "itens": [{"especialidade_id": especialidade_id, "situacao": "Falta pagamento"}],
        },
    )
    resp = client.get("/trabalhos", params={"situacao": "Falta pagamento"})
    items = resp.json()["items"]
    assert len(items) >= 1
    for t in items:
        assert any(i["situacao"] == "Falta pagamento" for i in t["itens"])
