"""Modelos financeiros: custos anuais fixos e equipamento (depreciação)."""
from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CustoAnual(Base):
    """Custo fixo associado a um ano (ex.: os valores somados manualmente na planilha).

    Somados aos valores pagos a externos para obter os custos totais do ano.
    """

    __tablename__ = "custos_anuais"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ano: Mapped[int] = mapped_column(Integer, index=True)
    valor: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    descricao: Mapped[str | None] = mapped_column(String(255), nullable=True)


class Equipamento(Base):
    """Equipamento sujeito a depreciação (ex.: Estação Total, GPS, computador)."""

    __tablename__ = "equipamentos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255))
    # Taxa de depreciação anual (fração, ex.: 0.1666 para 16,66%).
    percentagem: Mapped[float] = mapped_column(Numeric(6, 4), default=0)
    ano_aquisicao: Mapped[int] = mapped_column(Integer)
    valor: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
