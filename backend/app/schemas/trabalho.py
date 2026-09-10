"""Schemas Pydantic para o Trabalho e os seus itens (especialidades)."""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.services.classificacao import Estado, classificar
from app.services.situacao import Situacao, situacao_do_trabalho


# ---- Item de trabalho (uma especialidade) ----
class TrabalhoItemBase(BaseModel):
    especialidade_id: int | None = None
    externo_id: int | None = None
    valor: Decimal | None = Field(default=None, ge=0)
    valor_externo: Decimal | None = Field(default=None, ge=0)
    data_adjudicacao: date | None = None
    data_entrega: date | None = None
    situacao: Situacao | None = None
    observacoes: str | None = None


class TrabalhoItemCreate(TrabalhoItemBase):
    @model_validator(mode="after")
    def _validar_datas(self):
        # Validação só na criação/edição. Na leitura não se valida, pois há
        # dados históricos (importados) com entrega anterior à adjudicação.
        if (
            self.data_adjudicacao is not None
            and self.data_entrega is not None
            and self.data_entrega < self.data_adjudicacao
        ):
            raise ValueError("A data de entrega não pode ser anterior à adjudicação.")
        return self


class TrabalhoItemRead(TrabalhoItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    especialidade_codigo: str | None = None
    externo_nome: str | None = None
    estado: Estado | None = None

    @classmethod
    def from_model(cls, item) -> "TrabalhoItemRead":
        estado = classificar(
            item.data_adjudicacao,
            item.data_entrega,
            item.especialidade.prazo_top if item.especialidade else None,
            item.especialidade.prazo_ok if item.especialidade else None,
        )
        return cls(
            id=item.id,
            especialidade_id=item.especialidade_id,
            externo_id=item.externo_id,
            valor=item.valor,
            valor_externo=item.valor_externo,
            data_adjudicacao=item.data_adjudicacao,
            data_entrega=item.data_entrega,
            situacao=item.situacao,
            observacoes=item.observacoes,
            especialidade_codigo=item.especialidade.codigo if item.especialidade else None,
            externo_nome=item.externo.nome if item.externo else None,
            estado=estado,
        )


# ---- Trabalho ----
class TrabalhoBase(BaseModel):
    referencia: str | None = Field(default=None, max_length=50)
    cliente: str | None = Field(default=None, max_length=255)
    contacto: str | None = Field(default=None, max_length=100)
    localidade: str | None = Field(default=None, max_length=255)
    endereco: str | None = Field(default=None, max_length=255)
    intermediario_id: int | None = None
    observacoes: str | None = None


class TrabalhoCreate(TrabalhoBase):
    itens: list[TrabalhoItemCreate] = Field(default_factory=list)


class TrabalhoUpdate(BaseModel):
    referencia: str | None = Field(default=None, max_length=50)
    cliente: str | None = Field(default=None, max_length=255)
    contacto: str | None = Field(default=None, max_length=100)
    localidade: str | None = Field(default=None, max_length=255)
    endereco: str | None = Field(default=None, max_length=255)
    intermediario_id: int | None = None
    observacoes: str | None = None
    # Se `itens` for fornecido, substitui o conjunto de itens do trabalho.
    itens: list[TrabalhoItemCreate] | None = None
    # Se fornecido, aplica esta situação a TODAS as especialidades do trabalho.
    situacao_todos: Situacao | None = None


class TrabalhoRead(TrabalhoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    intermediario_nome: str | None = None
    itens: list[TrabalhoItemRead] = Field(default_factory=list)
    valor_total: Decimal = Decimal("0")
    valor_externo_total: Decimal = Decimal("0")
    # Situação global do trabalho = a "pior" das especialidades.
    situacao_trabalho: Situacao | None = None

    @classmethod
    def from_model(cls, t) -> "TrabalhoRead":
        itens = [TrabalhoItemRead.from_model(i) for i in t.itens]
        valor_total = sum((i.valor or Decimal("0") for i in itens), Decimal("0"))
        valor_ext_total = sum((i.valor_externo or Decimal("0") for i in itens), Decimal("0"))
        situacao_trab = situacao_do_trabalho([i.situacao for i in itens])
        return cls(
            id=t.id,
            referencia=t.referencia,
            cliente=t.cliente,
            contacto=t.contacto,
            localidade=t.localidade,
            endereco=t.endereco,
            intermediario_id=t.intermediario_id,
            observacoes=t.observacoes,
            intermediario_nome=t.intermediario.nome if t.intermediario else None,
            itens=itens,
            valor_total=valor_total,
            valor_externo_total=valor_ext_total,
            situacao_trabalho=situacao_trab,
        )


class TrabalhoPage(BaseModel):
    items: list[TrabalhoRead]
    total: int
    page: int
    page_size: int


class TrabalhoAlerta(BaseModel):
    """Um item (especialidade) por entregar em risco/atraso de prazo."""

    trabalho_id: int
    item_id: int
    referencia: str | None
    cliente: str | None
    especialidade_codigo: str | None
    data_adjudicacao: date | None
    prazo_ok: int | None
    dias_restantes: int
    nivel: str
