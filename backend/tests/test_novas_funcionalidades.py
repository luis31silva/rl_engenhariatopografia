"""Testes das novas funcionalidades:

- Resumo mensal do dashboard.
- Resumo por especialidade (anual/mensal).
- Externos com estatísticas do ano (valor_ano / num_trabalhos_ano).
- Desempenho das especialidades (prazo médio + classificação Excelente/Bom/Mau).
"""


def _criar_especialidade(client, codigo, prazo_top, prazo_ok):
    resp = client.post(
        "/especialidades",
        json={"codigo": codigo, "prazo_top": prazo_top, "prazo_ok": prazo_ok},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _criar_externo(client, nome):
    resp = client.post("/externos", json={"nome": nome})
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_resumo_mensal_dashboard(client):
    client.post(
        "/trabalhos",
        json={
            "cliente": "Mensal A",
            "itens": [
                {
                    "valor": "1000.00",
                    "valor_externo": "200.00",
                    "data_adjudicacao": "2091-03-10",
                    "data_entrega": "2091-03-20",
                },
                {
                    "valor": "500.00",
                    "data_adjudicacao": "2091-07-01",
                },
            ],
        },
    )
    mensal = client.get("/dashboard").json()["resumo_mensal"]
    marco = next((r for r in mensal if r["ano"] == 2091 and r["mes"] == 3), None)
    julho = next((r for r in mensal if r["ano"] == 2091 and r["mes"] == 7), None)
    assert marco is not None
    assert float(marco["brutos"]) == 1000.0
    assert float(marco["custos"]) == 200.0  # externo no mês de entrega (mesmo mês)
    assert float(marco["liquidos"]) == 800.0
    assert julho is not None
    assert float(julho["brutos"]) == 500.0


def test_custo_fixo_entra_em_dezembro_no_mensal(client):
    client.post("/dashboard/custos", json={"ano": 2092, "valor": "600.00", "descricao": "Software"})
    mensal = client.get("/dashboard").json()["resumo_mensal"]
    dez = next((r for r in mensal if r["ano"] == 2092 and r["mes"] == 12), None)
    assert dez is not None
    assert float(dez["custos"]) == 600.0


def test_especialidades_resumo_anual_e_mensal(client):
    esp_id = _criar_especialidade(client, "RESUMO93", 5, 10)
    client.post(
        "/trabalhos",
        json={
            "cliente": "Resumo Esp",
            "itens": [
                {"especialidade_id": esp_id, "valor": "300.00", "data_adjudicacao": "2093-02-01"},
                {"especialidade_id": esp_id, "valor": "700.00", "data_adjudicacao": "2093-02-15"},
            ],
        },
    )
    resumo = client.get("/dashboard/especialidades-resumo").json()
    esp = next((e for e in resumo if e["especialidade_id"] == esp_id), None)
    assert esp is not None
    ano = next((r for r in esp["resumo_anual"] if r["ano"] == 2093), None)
    assert ano is not None
    assert ano["num_itens"] == 2
    assert float(ano["valor"]) == 1000.0
    fev = next((r for r in esp["resumo_mensal"] if r["ano"] == 2093 and r["mes"] == 2), None)
    assert fev is not None
    assert fev["num_itens"] == 2
    assert float(fev["valor"]) == 1000.0


def test_externos_estatisticas_do_ano(client):
    ext_id = _criar_externo(client, "Externo Ano 94")
    client.post(
        "/trabalhos",
        json={
            "cliente": "Ext Ano",
            "itens": [
                {
                    "externo_id": ext_id,
                    "valor_externo": "100.00",
                    "data_adjudicacao": "2094-01-10",
                    "data_entrega": "2094-05-10",
                },
                {
                    "externo_id": ext_id,
                    "valor_externo": "250.00",
                    "data_adjudicacao": "2094-06-10",
                    "data_entrega": "2094-06-20",
                },
            ],
        },
    )
    # Ano com entregas: valor_ano = 350, num_trabalhos_ano = 2.
    externos_2094 = client.get("/externos", params={"ano": 2094}).json()
    e94 = next((x for x in externos_2094 if x["id"] == ext_id), None)
    assert e94 is not None
    assert float(e94["valor_ano"]) == 350.0
    assert e94["num_trabalhos_ano"] == 2
    assert float(e94["total_ganho"]) == 350.0

    # Ano sem entregas: valor_ano = 0.
    externos_2093 = client.get("/externos", params={"ano": 2093}).json()
    e93 = next((x for x in externos_2093 if x["id"] == ext_id), None)
    assert e93 is not None
    assert float(e93["valor_ano"]) == 0.0
    assert e93["num_trabalhos_ano"] == 0


def test_desempenho_classificacao(client):
    # Excelente: média < prazo_top.
    esp_exc = _criar_especialidade(client, "EXC95", 10, 20)
    client.post(
        "/trabalhos",
        json={
            "cliente": "Perf Exc",
            "itens": [
                {
                    "especialidade_id": esp_exc,
                    "data_adjudicacao": "2095-01-01",
                    "data_entrega": "2095-01-04",  # 3 dias
                },
                {
                    "especialidade_id": esp_exc,
                    "data_adjudicacao": "2095-02-01",
                    "data_entrega": "2095-02-06",  # 5 dias -> média 4
                },
            ],
        },
    )

    # Mau: média >= prazo_ok.
    esp_mau = _criar_especialidade(client, "MAU95", 5, 10)
    client.post(
        "/trabalhos",
        json={
            "cliente": "Perf Mau",
            "itens": [
                {
                    "especialidade_id": esp_mau,
                    "data_adjudicacao": "2095-03-01",
                    "data_entrega": "2095-03-21",  # 20 dias
                }
            ],
        },
    )

    desempenho = client.get("/especialidades/desempenho").json()
    d_exc = next((d for d in desempenho if d["especialidade_id"] == esp_exc), None)
    d_mau = next((d for d in desempenho if d["especialidade_id"] == esp_mau), None)
    assert d_exc is not None and d_exc["classificacao"] == "Excelente"
    assert d_exc["prazo_medio"] == 4.0
    assert d_exc["num_concluidos"] == 2
    assert d_mau is not None and d_mau["classificacao"] == "Mau"
    assert d_mau["prazo_medio"] == 20.0
