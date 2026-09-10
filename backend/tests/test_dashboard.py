"""Testes de integração do dashboard financeiro (nova estrutura por itens)."""


def _ano_resumo(resumo, ano):
    return next((r for r in resumo if r["ano"] == ano), None)


def test_dashboard_agrega_brutos_e_custos(client):
    # Itens em 2035 (ano improvável de colidir com outros testes).
    client.post(
        "/trabalhos",
        json={
            "cliente": "Dash A",
            "itens": [
                {
                    "valor": "1000.00",
                    "valor_externo": "200.00",
                    "data_adjudicacao": "2035-03-01",
                    "data_entrega": "2035-04-01",
                }
            ],
        },
    )
    client.post(
        "/trabalhos",
        json={"cliente": "Dash B", "itens": [{"valor": "500.00", "data_adjudicacao": "2035-06-01"}]},
    )
    client.post("/dashboard/custos", json={"ano": 2035, "valor": "300.00", "descricao": "Seguros"})

    resp = client.get("/dashboard")
    assert resp.status_code == 200
    resumo = resp.json()["resumo_anual"]
    ano = _ano_resumo(resumo, 2035)
    assert ano is not None
    assert float(ano["brutos"]) == 1500.0
    # Custos = 200 (externo) + 300 (fixo) = 500
    assert float(ano["custos"]) == 500.0
    assert float(ano["liquidos"]) == 1000.0


def test_valor_externo_conta_no_ano_de_entrega(client):
    # Adjudicado em 2080 mas entregue em 2081: o valor externo deve contar em 2081.
    client.post(
        "/trabalhos",
        json={
            "cliente": "Externo Entrega",
            "itens": [
                {
                    "valor_externo": "150.00",
                    "data_adjudicacao": "2080-11-01",
                    "data_entrega": "2081-02-01",
                }
            ],
        },
    )
    resumo = client.get("/dashboard").json()["resumo_anual"]
    ano_adj = _ano_resumo(resumo, 2080)
    ano_ent = _ano_resumo(resumo, 2081)
    # Em 2080 (adjudicação) não há custo de externo por causa deste item.
    assert ano_adj is None or float(ano_adj["custos"]) == 0.0
    # Em 2081 (entrega) o custo do externo aparece.
    assert ano_ent is not None
    assert float(ano_ent["custos"]) == 150.0


def test_valor_aquisicao_equipamento_entra_nos_custos_do_ano(client):
    # Um item em 2088 com valor 1000 (brutos) e um equipamento comprado em 2088 por 700.
    client.post(
        "/trabalhos",
        json={"cliente": "Eq Custo", "itens": [{"valor": "1000.00", "data_adjudicacao": "2088-01-01"}]},
    )
    client.post(
        "/dashboard/equipamentos",
        json={"nome": "Aparelho 2088", "percentagem": "0.2", "ano_aquisicao": 2088, "valor": "700.00"},
    )

    resumo = client.get("/dashboard").json()["resumo_anual"]
    ano = _ano_resumo(resumo, 2088)
    assert ano is not None
    assert float(ano["brutos"]) == 1000.0
    # Custos do ano de aquisição = valor de aquisição do equipamento (700), NÃO a depreciação (140).
    assert float(ano["custos"]) == 700.0
    assert float(ano["liquidos"]) == 300.0


def test_dashboard_depreciacao_equipamento(client):
    client.post(
        "/dashboard/equipamentos",
        json={"nome": "Estação Teste", "percentagem": "0.1666", "ano_aquisicao": 2021, "valor": "23000.00"},
    )
    resp = client.get("/dashboard")
    dep = resp.json()["depreciacao"]
    eq = next((d for d in dep if d["nome"] == "Estação Teste"), None)
    assert eq is not None
    primeira = eq["linhas"][0]
    assert primeira["ano"] == 2021
    assert float(primeira["depreciacao"]) == 3831.8


def test_crud_custos(client):
    criado = client.post("/dashboard/custos", json={"ano": 2098, "valor": "100.00"}).json()
    assert criado["ano"] == 2098
    upd = client.put(f"/dashboard/custos/{criado['id']}", json={"valor": "150.00"})
    assert float(upd.json()["valor"]) == 150.0
    assert client.delete(f"/dashboard/custos/{criado['id']}").status_code == 204


def test_crud_equipamentos(client):
    criado = client.post(
        "/dashboard/equipamentos",
        json={"nome": "GPS Teste", "percentagem": "0.25", "ano_aquisicao": 2020, "valor": "5000.00"},
    ).json()
    upd = client.put(f"/dashboard/equipamentos/{criado['id']}", json={"valor": "4000.00"})
    assert float(upd.json()["valor"]) == 4000.0
    assert client.delete(f"/dashboard/equipamentos/{criado['id']}").status_code == 204


def test_dashboard_requer_autenticacao(anon_client):
    assert anon_client.get("/dashboard").status_code == 401
