"""CRUD de Especialidades."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.apoio import Especialidade
from app.models.trabalho import TrabalhoItem
from app.schemas.apoio import (
    EspecialidadeCreate,
    EspecialidadeDesempenhoRead,
    EspecialidadeRead,
    EspecialidadeUpdate,
)
from app.services.classificacao import classificar_media

router = APIRouter(
    prefix="/especialidades",
    tags=["especialidades"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=list[EspecialidadeRead])
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(Especialidade).order_by(Especialidade.codigo)).all()


@router.get("/desempenho", response_model=list[EspecialidadeDesempenhoRead])
def desempenho(db: Session = Depends(get_db)):
    """Prazo médio de execução por especialidade e respetiva classificação.

    O prazo médio é a média, em dias, de (data_entrega - data_adjudicacao) dos
    itens concluídos (com ambas as datas) de cada especialidade. A classificação
    (Excelente / Bom / Mau) compara essa média com os prazos da especialidade.
    """
    # Carrega os itens concluídos (com adjudicação e entrega) por especialidade.
    itens = db.scalars(
        select(TrabalhoItem).where(
            TrabalhoItem.especialidade_id.is_not(None),
            TrabalhoItem.data_adjudicacao.is_not(None),
            TrabalhoItem.data_entrega.is_not(None),
        )
    ).all()

    # Acumula os dias por especialidade.
    dias_por_esp: dict[int, list[int]] = {}
    for item in itens:
        dias = (item.data_entrega - item.data_adjudicacao).days
        # Ignora valores negativos (entrega antes da adjudicação; dados inconsistentes).
        if dias < 0:
            continue
        dias_por_esp.setdefault(item.especialidade_id, []).append(dias)

    resultado: list[EspecialidadeDesempenhoRead] = []
    for esp in db.scalars(select(Especialidade).order_by(Especialidade.codigo)).all():
        dias_lista = dias_por_esp.get(esp.id, [])
        num = len(dias_lista)
        media = round(sum(dias_lista) / num, 1) if num else None
        resultado.append(
            EspecialidadeDesempenhoRead(
                especialidade_id=esp.id,
                codigo=esp.codigo,
                descricao=esp.descricao,
                prazo_top=esp.prazo_top,
                prazo_ok=esp.prazo_ok,
                num_concluidos=num,
                prazo_medio=media,
                classificacao=classificar_media(media, esp.prazo_top, esp.prazo_ok),
            )
        )
    return resultado


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
