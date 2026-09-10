"""Testes de autenticação."""
from tests.conftest import TEST_PASSWORD, TEST_USERNAME


def test_login_com_credenciais_validas(anon_client):
    resp = anon_client.post(
        "/auth/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_com_password_errada(anon_client):
    resp = anon_client.post(
        "/auth/login",
        data={"username": TEST_USERNAME, "password": "errada"},
    )
    assert resp.status_code == 401


def test_login_utilizador_inexistente(anon_client):
    resp = anon_client.post(
        "/auth/login",
        data={"username": "nao-existe", "password": "x"},
    )
    assert resp.status_code == 401


def test_endpoint_protegido_sem_token_rejeita(anon_client):
    resp = anon_client.get("/trabalhos")
    assert resp.status_code == 401


def test_endpoint_protegido_com_token_aceita(client):
    resp = client.get("/trabalhos")
    assert resp.status_code == 200


def test_me_devolve_utilizador_atual(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["username"] == TEST_USERNAME


def test_token_invalido_rejeitado(anon_client):
    anon_client.headers.update({"Authorization": "Bearer token-falso"})
    resp = anon_client.get("/trabalhos")
    assert resp.status_code == 401
