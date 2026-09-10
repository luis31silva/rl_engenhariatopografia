"""Modelos do Trabalho e dos seus itens (especialidades)."""
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.apoio import Especialidade, Externo, Intermediario


class Trabalho(Base):
    """Um trabalho identifica-se por uma referência e um cliente.

    Os dados que variam por especialidade (valor, datas, externo, avaliação)
    ficam nos itens (TrabalhoItem). Um trabalho tem um ou mais itens.
    """

    __tablename__ = "trabalhos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Referência no formato "num.ano" (ex.: "334.22").
    referencia: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)

    cliente: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    contacto: Mapped[str | None] = mapped_column(String(100), nullable=True)
    localidade: Mapped[str | None] = mapped_column(String(255), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)

    intermediario_id: Mapped[int | None] = mapped_column(
        ForeignKey("intermediarios.id", ondelete="SET NULL"), nullable=True
    )

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    intermediario: Mapped[Intermediario | None] = relationship(lazy="joined")
    itens: Mapped[list["TrabalhoItem"]] = relationship(
        back_populates="trabalho",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="TrabalhoItem.id",
    )


class TrabalhoItem(Base):
    """Uma especialidade dentro de um trabalho, com o seu valor, datas e externo."""

    __tablename__ = "trabalho_itens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trabalho_id: Mapped[int] = mapped_column(
        ForeignKey("trabalhos.id", ondelete="CASCADE"), index=True
    )

    especialidade_id: Mapped[int | None] = mapped_column(
        ForeignKey("especialidades.id", ondelete="SET NULL"), nullable=True
    )
    externo_id: Mapped[int | None] = mapped_column(
        ForeignKey("externos.id", ondelete="SET NULL"), nullable=True
    )

    # Valor cobrado ao cliente por esta especialidade (nem sempre preenchido).
    valor: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    # Valor pago ao colaborador externo por esta especialidade.
    valor_externo: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    data_adjudicacao: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)
    data_entrega: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Ponto de situação / pagamento: "Em curso" | "Falta pagamento" | "Pago".
    situacao: Mapped[str | None] = mapped_column(String(30), nullable=True)

    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)

    trabalho: Mapped[Trabalho] = relationship(back_populates="itens")
    especialidade: Mapped[Especialidade | None] = relationship(lazy="joined")
    externo: Mapped[Externo | None] = relationship(lazy="joined")
