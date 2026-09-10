"""Schemas financeiros: custos anuais, equipamentos e dashboard."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---- Custo anual ----
class CustoAnualBase(BaseModel):
    ano: int = Field(ge=1900, le=2200)
    valor: Decimal = Field(default=Decimal("0"), ge=0)
    descricao: str | None = Field(default=None, max_length=255)


class CustoAnualCreate(CustoAnualBase):
    pass


class CustoAnualUpdate(BaseModel):
    ano: int | None = Field(default=None, ge=1900, le=2200)
    valor: Decimal | None = Field(default=None, ge=0)
    descricao: str | None = Field(default=None, max_length=255)


class CustoAnualRead(CustoAnualBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---- Equipamento ----
class EquipamentoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=255)
    percentagem: Decimal = Field(ge=0, le=1)
    ano_aquisicao: int = Field(ge=1900, le=2200)
    valor: Decimal = Field(ge=0)


class EquipamentoCreate(EquipamentoBase):
    pass


class EquipamentoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=255)
    percentagem: Decimal | None = Field(default=None, ge=0, le=1)
    ano_aquisicao: int | None = Field(default=None, ge=1900, le=2200)
    valor: Decimal | None = Field(default=None, ge=0)


class EquipamentoRead(EquipamentoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---- Dashboard ----
class ResumoAnoRead(BaseModel):
    ano: int
    brutos: Decimal
    custos: Decimal
    liquidos: Decimal
    liquidez_pct: float | None
    variacao_pct: float | None


class LinhaDepreciacaoRead(BaseModel):
    ano: int
    valor_inicial: Decimal
    depreciacao: Decimal
    valor_final: Decimal


class DepreciacaoEquipamentoRead(BaseModel):
    equipamento_id: int
    nome: str
    linhas: list[LinhaDepreciacaoRead]


class DashboardRead(BaseModel):
    resumo_anual: list[ResumoAnoRead]
    depreciacao: list[DepreciacaoEquipamentoRead]
    total_brutos: Decimal
    total_custos: Decimal
    total_liquidos: Decimal
