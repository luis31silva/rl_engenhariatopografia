"""CRUD de Externos (colaboradores externos)."""
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.apoio import Externo
from app.models.trabalho import TrabalhoItem
from app.schemas.apoio import ExternoCreate, ExternoRead, ExternoUpdate

router = APIRouter(
    prefix="/externos",
    tags=["externos"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[ExternoRead])
def listar(ano: int | None = None, db: Session = Depends(get_db)):
    # As colunas "do ano" mostram os dados do `ano` pedido; por defeito, o ano atual.
    ano_alvo = ano if ano is not None else date.today().year

    # Ano em que o custo do externo se materializa: ano de ENTREGA do item.
    if db.bind.dialect.name == "sqlite":
        ano_item = func.strftime("%Y", TrabalhoItem.data_entrega)
        ano_valor = str(ano_alvo)
    else:
        ano_item = func.year(TrabalhoItem.data_entrega)
        ano_valor = ano_alvo

    # Agrega, por externo, o total pago e o número de trabalhos associados.
    rows = db.execute(
        select(
            Externo,
            func.coalesce(func.sum(TrabalhoItem.valor_externo), 0),
            func.count(TrabalhoItem.id),
        )
        .outerjoin(TrabalhoItem, TrabalhoItem.externo_id == Externo.id)
        .group_by(Externo.id)
        .order_by(Externo.nome)
    ).all()

    # Valor e nº de trabalhos do ANO ALVO (itens entregues nesse ano).
    ano_rows = db.execute(
        select(
            TrabalhoItem.externo_id,
            func.coalesce(func.sum(TrabalhoItem.valor_externo), 0),
            func.count(TrabalhoItem.id),
        )
        .where(TrabalhoItem.externo_id.is_not(None), ano_item == ano_valor)
        .group_by(TrabalhoItem.externo_id)
    ).all()
    ano_por_externo = {eid: (Decimal(str(v or 0)), int(n or 0)) for eid, v, n in ano_rows}

    resultado = []
    for externo, total, num in rows:
        item = ExternoRead.model_validate(externo)
        item.total_ganho = Decimal(str(total or 0))
        item.num_trabalhos = int(num or 0)
        valor_ano, num_ano = ano_por_externo.get(externo.id, (Decimal("0"), 0))
        item.valor_ano = valor_ano
        item.num_trabalhos_ano = num_ano
        resultado.append(item)
    return resultado


@router.post("", response_model=ExternoRead, status_code=status.HTTP_201_CREATED)
def criar(payload: ExternoCreate, db: Session = Depends(get_db)):
    existe = db.scalar(select(Externo).where(Externo.nome == payload.nome))
    if existe:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um externo com esse nome.")
    obj = Externo(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{item_id}", response_model=ExternoRead)
def obter(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Externo, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Externo não encontrado.")
    return obj


@router.put("/{item_id}", response_model=ExternoRead)
def atualizar(item_id: int, payload: ExternoUpdate, db: Session = Depends(get_db)):
    obj = db.get(Externo, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Externo não encontrado.")

    dados = payload.model_dump(exclude_unset=True)
    if "nome" in dados and dados["nome"] != obj.nome:
        duplicado = db.scalar(select(Externo).where(Externo.nome == dados["nome"]))
        if duplicado:
            raise HTTPException(status.HTTP_409_CONFLICT, "Já existe um externo com esse nome.")

    for campo, valor in dados.items():
        setattr(obj, campo, valor)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Externo, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Externo não encontrado.")
    db.delete(obj)
    db.commit()
