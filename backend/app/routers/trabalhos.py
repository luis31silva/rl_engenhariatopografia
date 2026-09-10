"""CRUD de Trabalhos (com itens/especialidades aninhados)."""
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.apoio import Especialidade, Externo, Intermediario
from app.models.trabalho import Trabalho, TrabalhoItem
from app.schemas.trabalho import (
    TrabalhoAlerta,
    TrabalhoCreate,
    TrabalhoItemCreate,
    TrabalhoPage,
    TrabalhoRead,
    TrabalhoUpdate,
)
from app.services.alertas import avaliar_alerta
from app.services.classificacao import Estado, classificar
from app.services.fatura import gerar_fatura_pdf
from app.services.situacao import Situacao

router = APIRouter(
    prefix="/trabalhos",
    tags=["trabalhos"],
    dependencies=[Depends(get_current_user)],
)

OrderBy = Literal["id", "referencia", "cliente"]


def _validar_intermediario(db: Session, intermediario_id: int | None) -> None:
    if intermediario_id is not None and not db.get(Intermediario, intermediario_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Intermediário inexistente.")


def _validar_item_fks(db: Session, item: TrabalhoItemCreate) -> None:
    if item.especialidade_id is not None and not db.get(Especialidade, item.especialidade_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Especialidade inexistente.")
    if item.externo_id is not None and not db.get(Externo, item.externo_id):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Externo inexistente.")


def _criar_itens(db: Session, trabalho: Trabalho, itens: list[TrabalhoItemCreate]) -> None:
    for item in itens:
        _validar_item_fks(db, item)
        dados = item.model_dump()
        # A coluna 'situacao' é texto: guarda o valor do enum, não o enum.
        if dados.get("situacao") is not None:
            dados["situacao"] = Situacao(dados["situacao"]).value
        trabalho.itens.append(TrabalhoItem(**dados))


def _trabalho_corresponde_estado(t: Trabalho, estado: Estado) -> bool:
    """True se algum item do trabalho tiver o estado indicado."""
    for i in t.itens:
        e = classificar(
            i.data_adjudicacao,
            i.data_entrega,
            i.especialidade.prazo_top if i.especialidade else None,
            i.especialidade.prazo_ok if i.especialidade else None,
        )
        if e == estado:
            return True
    return False


@router.get("", response_model=TrabalhoPage)
def listar(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, description="Pesquisa em cliente, referência, localidade e endereço."),
    especialidade_id: int | None = None,
    intermediario_id: int | None = None,
    externo_id: int | None = None,
    ano: int | None = Query(default=None, description="Ano da data de adjudicação de algum item."),
    estado: Estado | None = Query(default=None, description="Estado calculado de algum item."),
    situacao: Situacao | None = Query(default=None, description="Situação (pagamento) de algum item."),
    order_by: OrderBy = "id",
    order_dir: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=200),
):
    """Lista trabalhos com filtros, ordenação e paginação.

    Os filtros por especialidade, externo, ano e estado aplicam-se aos itens:
    um trabalho aparece se algum dos seus itens satisfizer o critério.
    """
    stmt = select(Trabalho)

    if q:
        termo = f"%{q}%"
        stmt = stmt.where(
            or_(
                Trabalho.cliente.ilike(termo),
                Trabalho.referencia.ilike(termo),
                Trabalho.localidade.ilike(termo),
                Trabalho.endereco.ilike(termo),
            )
        )
    if intermediario_id is not None:
        stmt = stmt.where(Trabalho.intermediario_id == intermediario_id)

    # Filtros que dependem dos itens: via EXISTS sobre trabalho_itens.
    if especialidade_id is not None:
        stmt = stmt.where(
            Trabalho.itens.any(TrabalhoItem.especialidade_id == especialidade_id)
        )
    if externo_id is not None:
        stmt = stmt.where(Trabalho.itens.any(TrabalhoItem.externo_id == externo_id))
    if situacao is not None:
        stmt = stmt.where(Trabalho.itens.any(TrabalhoItem.situacao == situacao.value))
    if ano is not None:
        stmt = stmt.where(
            Trabalho.itens.any(func.strftime("%Y", TrabalhoItem.data_adjudicacao) == str(ano))
            if db.bind.dialect.name == "sqlite"
            else Trabalho.itens.any(func.year(TrabalhoItem.data_adjudicacao) == ano)
        )

    coluna = getattr(Trabalho, order_by)
    stmt = stmt.order_by(coluna.asc() if order_dir == "asc" else coluna.desc())

    if estado is None:
        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        rows = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
        items = [TrabalhoRead.from_model(t) for t in rows]
    else:
        # Estado é calculado por item: filtrar em memória.
        todos = db.scalars(stmt).all()
        filtrados = [t for t in todos if _trabalho_corresponde_estado(t, estado)]
        total = len(filtrados)
        inicio = (page - 1) * page_size
        items = [TrabalhoRead.from_model(t) for t in filtrados[inicio : inicio + page_size]]

    return TrabalhoPage(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=TrabalhoRead, status_code=status.HTTP_201_CREATED)
def criar(payload: TrabalhoCreate, db: Session = Depends(get_db)):
    _validar_intermediario(db, payload.intermediario_id)
    obj = Trabalho(**payload.model_dump(exclude={"itens"}))
    _criar_itens(db, obj, payload.itens)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return TrabalhoRead.from_model(obj)


@router.get("/proxima-referencia")
def proxima_referencia(db: Session = Depends(get_db)):
    """Sugere a próxima referência no formato NNN.AA (ano atual, 2 dígitos)."""
    ano2 = date.today().strftime("%y")  # ex.: "26"
    sufixo = f".{ano2}"

    referencias = db.scalars(
        select(Trabalho.referencia).where(Trabalho.referencia.is_not(None))
    ).all()

    maior = 0
    for ref in referencias:
        if not ref or not ref.endswith(sufixo):
            continue
        num_str = ref[: -len(sufixo)].strip()
        try:
            maior = max(maior, int(num_str))
        except ValueError:
            continue

    proximo = maior + 1
    return {"referencia": f"{proximo:03d}.{ano2}"}


@router.get("/alertas", response_model=list[TrabalhoAlerta])
def alertas(db: Session = Depends(get_db)):
    """Itens (especialidades) por entregar em risco de prazo ou já em atraso.

    Ordenados por urgência (menos dias restantes primeiro).
    """
    hoje = date.today()
    candidatos = db.scalars(
        select(TrabalhoItem).where(TrabalhoItem.data_entrega.is_(None))
    ).all()

    resultado: list[TrabalhoAlerta] = []
    for item in candidatos:
        prazo_ok = item.especialidade.prazo_ok if item.especialidade else None
        avaliacao = avaliar_alerta(item.data_adjudicacao, item.data_entrega, prazo_ok, hoje)
        if avaliacao is None:
            continue
        nivel, dias_restantes = avaliacao
        trab = item.trabalho
        resultado.append(
            TrabalhoAlerta(
                trabalho_id=trab.id,
                item_id=item.id,
                referencia=trab.referencia,
                cliente=trab.cliente,
                especialidade_codigo=item.especialidade.codigo if item.especialidade else None,
                data_adjudicacao=item.data_adjudicacao,
                prazo_ok=prazo_ok,
                dias_restantes=dias_restantes,
                nivel=nivel.value,
            )
        )

    resultado.sort(key=lambda a: a.dias_restantes)
    return resultado


@router.get("/{trabalho_id}", response_model=TrabalhoRead)
def obter(trabalho_id: int, db: Session = Depends(get_db)):
    obj = db.get(Trabalho, trabalho_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Trabalho não encontrado.")
    return TrabalhoRead.from_model(obj)


@router.put("/{trabalho_id}", response_model=TrabalhoRead)
def atualizar(trabalho_id: int, payload: TrabalhoUpdate, db: Session = Depends(get_db)):
    obj = db.get(Trabalho, trabalho_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Trabalho não encontrado.")

    dados = payload.model_dump(exclude_unset=True)
    _validar_intermediario(db, dados.get("intermediario_id"))

    # Campos que não são colunas do trabalho: tratados à parte.
    novos_itens = dados.pop("itens", None)
    situacao_todos = dados.pop("situacao_todos", None)

    for campo, valor in dados.items():
        setattr(obj, campo, valor)

    if novos_itens is not None:
        obj.itens.clear()
        db.flush()
        _criar_itens(db, obj, payload.itens or [])

    # Aplicar uma situação a todas as especialidades do trabalho.
    if situacao_todos is not None:
        valor_sit = Situacao(situacao_todos).value
        for item in obj.itens:
            item.situacao = valor_sit

    db.commit()
    db.refresh(obj)
    return TrabalhoRead.from_model(obj)


@router.delete("/{trabalho_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar(trabalho_id: int, db: Session = Depends(get_db)):
    obj = db.get(Trabalho, trabalho_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Trabalho não encontrado.")
    db.delete(obj)
    db.commit()


@router.get("/{trabalho_id}/fatura")
def fatura(trabalho_id: int, db: Session = Depends(get_db)):
    """Gera e devolve a fatura/recibo do trabalho em PDF."""
    obj = db.get(Trabalho, trabalho_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Trabalho não encontrado.")

    pdf = gerar_fatura_pdf(obj)
    nome_ficheiro = f"recibo-{(obj.referencia or obj.id)}.pdf".replace("/", "-").replace(" ", "")
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{nome_ficheiro}"'},
    )
