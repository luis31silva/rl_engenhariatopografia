"""Testes dos cálculos financeiros (agregações e depreciação)."""
from decimal import Decimal

from app.services.financeiro import depreciacao_equipamento, resumo_por_ano


def test_resumo_ano_simples():
    brutos = {2015: 380, 2016: 590}
    custos = {2015: 0, 2016: 0}
    r = resumo_por_ano(brutos, custos)
    assert r[0].ano == 2015
    assert r[0].brutos == Decimal("380")
    assert r[0].custos == Decimal("0")
    assert r[0].liquidos == Decimal("380")
    assert r[0].liquidez_pct == 100.0
    assert r[0].variacao_pct is None  # primeiro ano


def test_resumo_variacao_entre_anos():
    # Líquidos: 2015=380, 2016=590 -> variação = (590-380)/380*100
    brutos = {2015: 380, 2016: 590}
    custos = {2015: 0, 2016: 0}
    r = resumo_por_ano(brutos, custos)
    esperado = (590 - 380) / 380 * 100
    assert abs(r[1].variacao_pct - esperado) < 1e-9


def test_resumo_com_custos():
    brutos = {2020: 20395}
    custos = {2020: 7125}
    r = resumo_por_ano(brutos, custos)
    assert r[0].liquidos == Decimal("13270")


def test_liquidez_none_quando_brutos_zero():
    r = resumo_por_ano({2020: 0}, {2020: 100})
    assert r[0].liquidez_pct is None
    assert r[0].liquidos == Decimal("-100")


def test_uniao_de_anos():
    # Um ano só com custos deve aparecer.
    r = resumo_por_ano({2019: 8130}, {2019: 16275, 2021: 500})
    anos = [x.ano for x in r]
    assert anos == [2019, 2021]


def test_depreciacao_primeiro_ano_estacao_total():
    # Estação Total: 23000 a 16,66% -> 3831.8 no primeiro ano (valor da planilha).
    linhas = depreciacao_equipamento(23000, 0.1666, ano_aquisicao=2021, ate_ano=2021)
    assert linhas[0].ano == 2021
    assert linhas[0].depreciacao == Decimal("3831.80")
    assert linhas[0].valor_final == Decimal("19168.20")


def test_depreciacao_multiplos_anos_decrescente():
    linhas = depreciacao_equipamento(23000, 0.1666, ano_aquisicao=2021, ate_ano=2023)
    assert len(linhas) == 3
    # Segundo ano deprecia sobre o valor restante.
    assert linhas[1].valor_inicial == Decimal("19168.20")
    # Valor final decresce a cada ano.
    assert linhas[0].valor_final > linhas[1].valor_final > linhas[2].valor_final
