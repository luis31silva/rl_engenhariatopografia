"""CRUD de Especialidades."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.apoio import Especialidade
from app.schemas.apoio import (
    EspecialidadeCreate,
    EspecialidadeRead,
    EspecialidadeUpdate,
)

router = APIRouter(
    prefix="/especialidades",
    tags=["especialidades"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[EspecialidadeRead])
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(Especialidade).order_by(Especialidade.codigo)).all()


@router.post("", response_model=EspecialidadeRead, status_code=status.HTTP_201_CREATED)
def criar(payload: EspecialidadeCreate, db: Session = Depends(get_db)):
    existe = db.scalar(select(Especialidade).where(Especialidade.codigo == payload.codigo))
    if existe:
        raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma especialidade com esse código.")
    obj = Especialidade(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{item_id}", response_model=EspecialidadeRead)
def obter(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Especialidade, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Especialidade não encontrada.")
    return obj


@router.put("/{item_id}", response_model=EspecialidadeRead)
def atualizar(item_id: int, payload: EspecialidadeUpdate, db: Session = Depends(get_db)):
    obj = db.get(Especialidade, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Especialidade não encontrada.")

    dados = payload.model_dump(exclude_unset=True)
    if "codigo" in dados and dados["codigo"] != obj.codigo:
        duplicado = db.scalar(select(Especialidade).where(Especialidade.codigo == dados["codigo"]))
        if duplicado:
            raise HTTPException(status.HTTP_409_CONFLICT, "Já existe uma especialidade com esse código.")

    for campo, valor in dados.items():
        setattr(obj, campo, valor)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Especialidade, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Especialidade não encontrada.")
    db.delete(obj)
    db.commit()
