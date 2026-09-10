"""Configuração da ligação à base de dados via SQLAlchemy."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# SQLite precisa de um argumento especial para ser usado em múltiplas threads
# (relevante para os testes e para o dev local). MySQL não precisa.
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM."""


def get_db() -> Generator[Session, None, None]:
    """Dependência do FastAPI que fornece uma sessão de BD por pedido."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
