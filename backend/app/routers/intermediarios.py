"""CRUD de Intermediários."""
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.apoio import Intermediario
from app.models.trabalho import Trabalho, TrabalhoItem
from app.schemas.apoio import (
    IntermediarioCreate,
    IntermediarioRead,
    IntermediarioUpdate,
)

router = APIRouter(
    prefix="/intermediarios",
    tags=["intermediarios"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[IntermediarioRead])
def listar(db: Session = Depends(get_db)):
    ano_atual = date.today().year

    # Expressão para o ano de adjudicação do item, conforme o dialeto da BD.
    if db.bind.dialect.name == "sqlite":
        ano_item = func.strftime("%Y", TrabalhoItem.data_adjudicacao)
        ano_valor = str(ano_atual)
    else:
        ano_item = func.year(TrabalhoItem.data_adjudicacao)
        ano_valor = ano_atual

    # Nº de trabalhos por intermediário (trabalhos distintos).
    contagem_rows = db.execute(
        select(Trabalho.intermediario_id, func.count(Trabalho.id))
        .where(Trabalho.intermediario_id.is_not(None))
        .group_by(Trabalho.intermediario_id)
    ).all()
    num_por_interm = {iid: n for iid, n in contagem_rows}

    # Valor total (soma dos valores dos itens dos trabalhos) por intermediário.
    valor_rows = db.execute(
        select(
            Trabalho.intermediario_id,
            func.coalesce(func.sum(TrabalhoItem.valor), 0),
        )
        .join(TrabalhoItem, TrabalhoItem.trabalho_id == Trabalho.id)
        .where(Trabalho.intermediario_id.is_not(None))
        .group_by(Trabalho.intermediario_id)
    ).all()
    valor_por_interm = {iid: Decimal(str(v)) for iid, v in valor_rows}

    # Valor do ANO ATUAL: soma dos valores dos itens adjudicados este ano.
    valor_ano_rows = db.execute(
        select(
            Trabalho.intermediario_id,
            func.coalesce(func.sum(TrabalhoItem.valor), 0),
        )
        .join(TrabalhoItem, TrabalhoItem.trabalho_id == Trabalho.id)
        .where(Trabalho.intermediario_id.is_not(None), ano_item == ano_valor)
        .group_by(Trabalho.intermediario_id)
    ).all()
    valor_ano_por_interm = {iid: Decimal(str(v)) for iid, v in valor_ano_rows}

    # Nº de trabalhos DISTINTOS do ano atual (com pelo menos um item adjudicado este ano).
    num_ano_rows = db.execute(
        select(
            Trabalho.intermediario_id,
            func.count(func.distinct(Trabalho.id)),
        )
        .join(TrabalhoItem, TrabalhoItem.trabalho_id == Trabalho.id)
        .where(Trabalho.intermediario_id.is_not(None), ano_item == ano_valor)
        .group_by(Trabalho.intermediario_id)
    ).all()
    num_ano_por_interm = {iid: n for iid, n in num_ano_rows}

    resultado = []
    for obj in db.scalars(select(Intermediario).order_by(Intermediario.nome)).all():
        num = num_por_interm.get(obj.id, 0)
        total = valor_por_interm.get(obj.id, Decimal("0"))
        item = IntermediarioRead.model_validate(obj)
        item.num_trabalhos = num
        item.valor_total = total
        item.valor_medio = (total / num) if num else Decimal("0")
        item.num_trabalhos_ano = num_ano_por_interm.get(obj.id, 0)
        item.valor_ano = valor_ano_por_interm.get(obj.id, Decimal("0"))
        resultado.append(item)
    return resultado


@router.post("", response_model=IntermediarioRead, status_code=status.HTTP_201_CREATED)
def criar(payload: IntermediarioCreate, db: Session = Depends(get_db)):
    existe = db.scalar(select(Intermediario).where(Intermediario.nome == payload.nome))
    if existe:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um intermediário com esse nome.")
    obj = Intermediario(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{item_id}", response_model=IntermediarioRead)
def obter(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Intermediario, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Intermediário não encontrado.")
    return obj


@router.put("/{item_id}", response_model=IntermediarioRead)
def atualizar(item_id: int, payload: IntermediarioUpdate, db: Session = Depends(get_db)):
    obj = db.get(Intermediario, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Intermediário não encontrado.")

    dados = payload.model_dump(exclude_unset=True)
    if "nome" in dados and dados["nome"] != obj.nome:
        duplicado = db.scalar(select(Intermediario).where(Intermediario.nome == dados["nome"]))
        if duplicado:
            raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um intermediário com esse nome.")

    for campo, valor in dados.items():
        setattr(obj, campo, valor)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Intermediario, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Intermediário não encontrado.")
    db.delete(obj)
    db.commit()
