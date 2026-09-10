"""CRUD de Externos (colaboradores externos)."""
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
def listar(db: Session = Depends(get_db)):
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

    resultado = []
    for externo, total, num in rows:
        item = ExternoRead.model_validate(externo)
        item.total_ganho = Decimal(str(total or 0))
        item.num_trabalhos = int(num or 0)
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
