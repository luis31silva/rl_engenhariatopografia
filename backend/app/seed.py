"""Cria o utilizador inicial se ainda não existir.

Uso:
    python -m app.seed

As credenciais vêm das variáveis INITIAL_USERNAME e INITIAL_PASSWORD
(ver config). Em produção, definir uma password forte antes de correr.
"""
from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal
from app.models.user import User
from app.security import hash_password


def seed_user() -> None:
    settings = get_settings()
    db = SessionLocal()
    try:
        existente = db.scalar(select(User).where(User.username == settings.initial_username))
        if existente:
            print(f"Utilizador '{settings.initial_username}' já existe. Nada a fazer.")
            return
        user = User(
            username=settings.initial_username,
            hashed_password=hash_password(settings.initial_password),
        )
        db.add(user)
        db.commit()
        print(f"Utilizador '{settings.initial_username}' criado.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_user()
