"""Configuração da ligação à base de dados via SQLAlchemy."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# Argumentos de ligação específicos por tipo de base de dados.
connect_args: dict = {}
if settings.database_url.startswith("sqlite"):
    # SQLite precisa disto para uso em múltiplas threads (testes/dev local).
    connect_args = {"check_same_thread": False}
elif settings.database_url.startswith("mysql") and settings.db_ssl:
    # O Aiven (MySQL) exige TLS. Passar um dict `ssl` não vazio ativa a ligação
    # segura no PyMySQL sem necessitar de um ficheiro de CA local.
    connect_args = {"ssl": {"ssl": True}}

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
