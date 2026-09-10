"""Fixtures partilhadas pelos testes.

Usa uma base de dados SQLite em ficheiro temporário, isolada por sessão de teste,
para não depender de um MySQL a correr.
"""
import os
import tempfile

import pytest

# Configura o ambiente ANTES de importar a app (as settings são lidas no import).
_tmp_db_fd, _tmp_db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db_path}"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    """Cria todas as tabelas na BD de teste a partir dos modelos."""
    from app.database import Base, engine
    import app.models  # noqa: F401  (regista os modelos em Base.metadata)

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    try:
        os.close(_tmp_db_fd)
        os.unlink(_tmp_db_path)
    except OSError:
        pass


TEST_USERNAME = "tester"
TEST_PASSWORD = "test-pass-123"


@pytest.fixture(scope="session", autouse=True)
def _seed_test_user(_create_schema):
    """Cria um utilizador de teste para autenticar os pedidos."""
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User
    from app.security import hash_password

    db = SessionLocal()
    try:
        if not db.scalar(select(User).where(User.username == TEST_USERNAME)):
            db.add(User(username=TEST_USERNAME, hashed_password=hash_password(TEST_PASSWORD)))
            db.commit()
    finally:
        db.close()


@pytest.fixture()
def anon_client():
    """Cliente sem autenticação."""
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def client(anon_client):
    """Cliente autenticado (com token Bearer válido) — usado pela maioria dos testes."""
    resp = anon_client.post(
        "/auth/login",
        data={"username": TEST_USERNAME, "password": TEST_PASSWORD},
    )
    token = resp.json()["access_token"]
    anon_client.headers.update({"Authorization": f"Bearer {token}"})
    return anon_client
