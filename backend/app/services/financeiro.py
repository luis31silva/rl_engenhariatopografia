"""Cálculos financeiros do dashboard (Relatório de Contas).

Funções puras e testáveis que não dependem da base de dados, para facilitar a
validação dos valores contra a folha de cálculo original.
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ResumoAno:
    ano: int
    brutos: Decimal
    custos: Decimal
    liquidos: Decimal
    liquidez_pct: float | None  # liquidos / brutos, em percentagem
    variacao_pct: float | None  # variação dos líquidos face ao ano anterior


def _dec(v) -> Decimal:
    return Decimal(str(v or 0))


def resumo_por_ano(
    brutos_por_ano: dict[int, Decimal | float],
    custos_por_ano: dict[int, Decimal | float],
) -> list[ResumoAno]:
    """Calcula o resumo anual (brutos, custos, líquidos, liquidez, variação).

    - brutos_por_ano: soma dos valores dos trabalhos por ano de adjudicação.
    - custos_por_ano: soma de (valores externos + custos fixos) por ano.
    Os anos resultantes são a união das chaves de ambos, ordenados crescentemente.
    """
    anos = sorted(set(brutos_por_ano) | set(custos_por_ano))
    resultado: list[ResumoAno] = []
    liquidos_anterior: Decimal | None = None

    for ano in anos:
        brutos = _dec(brutos_por_ano.get(ano, 0))
        custos = _dec(custos_por_ano.get(ano, 0))
        liquidos = brutos - custos

        liquidez = float(liquidos / brutos * 100) if brutos != 0 else None

        if liquidos_anterior is None or liquidos_anterior == 0:
            variacao = None
        else:
            variacao = float((liquidos - liquidos_anterior) / abs(liquidos_anterior) * 100)

        resultado.append(
            ResumoAno(
                ano=ano,
                brutos=brutos,
                custos=custos,
                liquidos=liquidos,
                liquidez_pct=liquidez,
                variacao_pct=variacao,
            )
        )
        liquidos_anterior = liquidos

    return resultado


@dataclass
class LinhaDepreciacao:
    ano: int
    valor_inicial: Decimal
    depreciacao: Decimal
    valor_final: Decimal


def depreciacao_equipamento(
    valor: Decimal | float,
    percentagem: Decimal | float,
    ano_aquisicao: int,
    ate_ano: int,
) -> list[LinhaDepreciacao]:
    """Calcula a depreciação anual de um equipamento (método do saldo decrescente).

    Cada ano deprecia `percentagem` sobre o valor no início desse ano, replicando
    a lógica da planilha (valor_ano_seguinte = valor - valor*percentagem).
    """
    linhas: list[LinhaDepreciacao] = []
    valor_atual = _dec(valor)
    perc = _dec(percentagem)

    for ano in range(ano_aquisicao, ate_ano + 1):
        dep = valor_atual * perc
        linhas.append(
            LinhaDepreciacao(
                ano=ano,
                valor_inicial=valor_atual,
                depreciacao=dep,
                valor_final=valor_atual - dep,
            )
        )
        valor_atual = valor_atual - dep

    return linhas
