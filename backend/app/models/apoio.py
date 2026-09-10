"""Modelos das tabelas de apoio: Especialidades, Intermediários, Externos."""
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Especialidade(Base):
    """Tipo de serviço (ex.: LEVTOP, DEST, PIP, EST...).

    prazo_top e prazo_ok definem, em dias, os limites usados para classificar
    o desempenho de um trabalho (TOP/OK/MAU) consoante o tempo de entrega.
    """

    __tablename__ = "especialidades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    descricao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Limite (em dias) para o trabalho ser considerado "TOP".
    prazo_top: Mapped[int] = mapped_column(Integer, default=0)
    # Limite (em dias) para o trabalho ser considerado "OK"; acima disto é "MAU".
    prazo_ok: Mapped[int] = mapped_column(Integer, default=0)


class Intermediario(Base):
    """Quem envia/angaria trabalho (arquitetos, engenheiros, agentes, etc.)."""

    __tablename__ = "intermediarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    # Valor associado ao intermediário (comissão/referência), opcional.
    valor: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)


class Externo(Base):
    """Colaborador externo que executa parte do trabalho."""

    __tablename__ = "externos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), unique=True, index=True)
