"""Testes do endpoint de saúde da aplicação."""


def test_health_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_reports_ok_status(client):
    resp = client.get("/health")
    body = resp.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
