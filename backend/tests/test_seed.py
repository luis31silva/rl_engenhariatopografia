"""Testa o script de seed do utilizador inicial."""
from sqlalchemy import select


def test_seed_cria_e_e_idempotente(client, capsys):
    # Usa credenciais próprias para não colidir com o utilizador de teste.
    from app.config import get_settings
    from app.database import SessionLocal
    from app.models.user import User
    from app.seed import seed_user

    settings = get_settings()
    settings.initial_username = "seed-user"
    settings.initial_password = "seed-pass"

    seed_user()
    db = SessionLocal()
    try:
        assert db.scalar(select(User).where(User.username == "seed-user")) is not None
    finally:
        db.close()

    # Segunda execução não deve criar duplicado nem falhar.
    seed_user()
    db = SessionLocal()
    try:
        users = db.scalars(select(User).where(User.username == "seed-user")).all()
        assert len(users) == 1
    finally:
        db.close()
