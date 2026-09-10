"""Dashboard financeiro (Relatório de Contas) e CRUD de custos/equipamentos."""
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.financeiro import CustoAnual, Equipamento
from app.models.trabalho import TrabalhoItem
from app.schemas.financeiro import (
    CustoAnualCreate,
    CustoAnualRead,
    CustoAnualUpdate,
    DashboardRead,
    DepreciacaoEquipamentoRead,
    EquipamentoCreate,
    EquipamentoRead,
    EquipamentoUpdate,
    LinhaDepreciacaoRead,
    ResumoAnoRead,
)
from app.services.financeiro import depreciacao_equipamento, resumo_por_ano

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=DashboardRead)
def dashboard(db: Session = Depends(get_db)):
    """Agrega os valores anuais e a depreciação de equipamento."""
    # Brutos por ano: soma dos valores dos ITENS por ano de adjudicação do item.
    brutos_rows = db.execute(
        select(
            extract("year", TrabalhoItem.data_adjudicacao).label("ano"),
            func.coalesce(func.sum(TrabalhoItem.valor), 0),
        )
        .where(TrabalhoItem.data_adjudicacao.is_not(None))
        .group_by("ano")
    ).all()
    brutos_por_ano = {int(ano): Decimal(str(total)) for ano, total in brutos_rows if ano is not None}

    # Custos por ano: valores pagos a externos (por ano de ENTREGA do item, pois
    # o custo do externo materializa-se na entrega) + custos fixos anuais.
    externos_rows = db.execute(
        select(
            extract("year", TrabalhoItem.data_entrega).label("ano"),
            func.coalesce(func.sum(TrabalhoItem.valor_externo), 0),
        )
        .where(TrabalhoItem.data_entrega.is_not(None))
        .group_by("ano")
    ).all()
    custos_por_ano: dict[int, Decimal] = {
        int(ano): Decimal(str(total)) for ano, total in externos_rows if ano is not None
    }

    for custo in db.scalars(select(CustoAnual)).all():
        custos_por_ano[custo.ano] = custos_por_ano.get(custo.ano, Decimal("0")) + Decimal(
            str(custo.valor)
        )

    # Valor de aquisição de cada equipamento conta como custo do ano em que foi comprado.
    # (A depreciação anual NÃO entra nos custos; é apenas informativa.)
    equipamentos_lista = list(db.scalars(select(Equipamento)).all())
    for eq in equipamentos_lista:
        custos_por_ano[eq.ano_aquisicao] = custos_por_ano.get(
            eq.ano_aquisicao, Decimal("0")
        ) + Decimal(str(eq.valor))

    resumo = resumo_por_ano(brutos_por_ano, custos_por_ano)
    resumo_out = [
        ResumoAnoRead(
            ano=r.ano,
            brutos=r.brutos,
            custos=r.custos,
            liquidos=r.liquidos,
            liquidez_pct=r.liquidez_pct,
            variacao_pct=r.variacao_pct,
        )
        for r in resumo
    ]

    # Projeta a depreciação até 5 anos para o futuro (previsão).
    ANOS_PREVISAO_FUTURO = 5
    ate_ano = date.today().year + ANOS_PREVISAO_FUTURO
    depreciacao_out: list[DepreciacaoEquipamentoRead] = []
    for eq in equipamentos_lista:
        linhas = depreciacao_equipamento(eq.valor, eq.percentagem, eq.ano_aquisicao, ate_ano)
        depreciacao_out.append(
            DepreciacaoEquipamentoRead(
                equipamento_id=eq.id,
                nome=eq.nome,
                linhas=[
                    LinhaDepreciacaoRead(
                        ano=l.ano,
                        valor_inicial=l.valor_inicial,
                        depreciacao=l.depreciacao,
                        valor_final=l.valor_final,
                    )
                    for l in linhas
                ],
            )
        )

    total_brutos = sum((r.brutos for r in resumo), Decimal("0"))
    total_custos = sum((r.custos for r in resumo), Decimal("0"))

    return DashboardRead(
        resumo_anual=resumo_out,
        depreciacao=depreciacao_out,
        total_brutos=total_brutos,
        total_custos=total_custos,
        total_liquidos=total_brutos - total_custos,
    )


# ---- CRUD custos anuais ----
@router.get("/custos", response_model=list[CustoAnualRead])
def listar_custos(db: Session = Depends(get_db)):
    return db.scalars(select(CustoAnual).order_by(CustoAnual.ano)).all()


@router.post("/custos", response_model=CustoAnualRead, status_code=status.HTTP_201_CREATED)
def criar_custo(payload: CustoAnualCreate, db: Session = Depends(get_db)):
    obj = CustoAnual(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/custos/{item_id}", response_model=CustoAnualRead)
def atualizar_custo(item_id: int, payload: CustoAnualUpdate, db: Session = Depends(get_db)):
    obj = db.get(CustoAnual, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Custo anual não encontrado.")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(obj, campo, valor)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/custos/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_custo(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(CustoAnual, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Custo anual não encontrado.")
    db.delete(obj)
    db.commit()


# ---- CRUD equipamentos ----
@router.get("/equipamentos", response_model=list[EquipamentoRead])
def listar_equipamentos(db: Session = Depends(get_db)):
    return db.scalars(select(Equipamento).order_by(Equipamento.nome)).all()


@router.post("/equipamentos", response_model=EquipamentoRead, status_code=status.HTTP_201_CREATED)
def criar_equipamento(payload: EquipamentoCreate, db: Session = Depends(get_db)):
    obj = Equipamento(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/equipamentos/{item_id}", response_model=EquipamentoRead)
def atualizar_equipamento(item_id: int, payload: EquipamentoUpdate, db: Session = Depends(get_db)):
    obj = db.get(Equipamento, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipamento não encontrado.")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(obj, campo, valor)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/equipamentos/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def apagar_equipamento(item_id: int, db: Session = Depends(get_db)):
    obj = db.get(Equipamento, item_id)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Equipamento não encontrado.")
    db.delete(obj)
    db.commit()
