"""Schemas Pydantic para as tabelas de apoio."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---- Especialidade ----
class EspecialidadeBase(BaseModel):
    codigo: str = Field(min_length=1, max_length=50)
    descricao: str | None = Field(default=None, max_length=255)
    prazo_top: int = Field(default=0, ge=0)
    prazo_ok: int = Field(default=0, ge=0)


class EspecialidadeCreate(EspecialidadeBase):
    pass


class EspecialidadeUpdate(BaseModel):
    codigo: str | None = Field(default=None, min_length=1, max_length=50)
    descricao: str | None = Field(default=None, max_length=255)
    prazo_top: int | None = Field(default=None, ge=0)
    prazo_ok: int | None = Field(default=None, ge=0)


class EspecialidadeRead(EspecialidadeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---- Intermediário ----
class IntermediarioBase(BaseModel):
    nome: str = Field(min_length=1, max_length=255)
    valor: Decimal | None = Field(default=None, ge=0)


class IntermediarioCreate(IntermediarioBase):
    pass


class IntermediarioUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    valor: Decimal | None = Field(default=None, ge=0)


class IntermediarioRead(IntermediarioBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    # Estatísticas calculadas (preenchidas na listagem).
    num_trabalhos: int = 0
    valor_total: Decimal = Decimal("0")
    valor_medio: Decimal = Decimal("0")
    # Do ano atual (itens adjudicados no ano corrente).
    num_trabalhos_ano: int = 0
    valor_ano: Decimal = Decimal("0")


# ---- Externo ----
class ExternoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=255)


class ExternoCreate(ExternoBase):
    pass


class ExternoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)


class ExternoRead(ExternoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    # Estatísticas calculadas (preenchidas na listagem).
    total_ganho: Decimal = Decimal("0")
    num_trabalhos: int = 0
