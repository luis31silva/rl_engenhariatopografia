"""Testes da geração de fatura/recibo em PDF (nova estrutura com itens)."""


def test_fatura_devolve_pdf_valido(client):
    criado = client.post(
        "/trabalhos",
        json={
            "cliente": "Cliente Fatura",
            "referencia": "FAT-001",
            "itens": [{"valor": "250.00"}],
        },
    ).json()

    resp = client.get(f"/trabalhos/{criado['id']}/fatura")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"
    assert len(resp.content) > 500


def test_fatura_trabalho_inexistente_404(client):
    assert client.get("/trabalhos/999999/fatura").status_code == 404


def test_fatura_requer_autenticacao(anon_client):
    assert anon_client.get("/trabalhos/1/fatura").status_code == 401
