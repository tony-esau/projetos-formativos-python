from datetime import date
from decimal import Decimal

import pytest

from validacao import (converter_categoria, converter_data, converter_mes,
                       converter_tipo, converter_valor)


@pytest.mark.parametrize("texto, esperado", [
    ("12,50", "12.50"),
    ("12.50", "12.50"),
    ("12", "12.00"),
    ("12,5", "12.50"),
    ("0,01", "0.01"),
    ("1500", "1500.00"),
    ("  7,90  ", "7.90"),
])
def test_valor_valido(texto, esperado):
    assert converter_valor(texto) == Decimal(esperado)


@pytest.mark.parametrize("texto", [
    "", "   ", "abc", "12a", "-12,50", "0", "0,00",
    "12,505", "1.234,56", "12,", ",50", "12 50", "R$ 12",
])
def test_valor_invalido(texto):
    with pytest.raises(ValueError):
        converter_valor(texto)


def test_valor_guarda_duas_casas_como_texto():
    # É assim que o valor vai ser escrito no CSV.
    assert str(converter_valor("12,5")) == "12.50"


def test_soma_com_decimal_e_exata():
    # Com float, 0.1 + 0.2 daria 0.30000000000000004.
    soma = converter_valor("0,10") + converter_valor("0,20")
    assert soma == Decimal("0.30")


@pytest.mark.parametrize("texto, esperado", [
    ("06/11/2026", date(2026, 11, 6)),
    ("29/02/2024", date(2024, 2, 29)),
    ("31/12/2025", date(2025, 12, 31)),
    ("01/01/2026", date(2026, 1, 1)),
])
def test_data_valida(texto, esperado):
    assert converter_data(texto) == esperado


def test_data_vazia_vira_hoje():
    assert converter_data("") == date.today()


@pytest.mark.parametrize("texto", [
    "31/02/2026", "29/02/2026", "31/04/2026", "00/01/2026", "15/13/2026",
    "6/11/2026", "06-11-2026", "2026-11-06", "06/11/26", "abc",
])
def test_data_invalida(texto):
    with pytest.raises(ValueError):
        converter_data(texto)


def test_mensagem_de_data_inexistente_e_clara():
    with pytest.raises(ValueError, match="não existe"):
        converter_data("31/02/2026")


@pytest.mark.parametrize("texto, esperado", [
    ("11-2026", "2026-11"),
    ("01-2025", "2025-01"),
    ("12/2026", "2026-12"),
    (" 03-2027 ", "2027-03"),
])
def test_mes_valido(texto, esperado):
    assert converter_mes(texto) == esperado


def test_mes_vazio_vira_mes_atual():
    assert converter_mes("") == date.today().strftime("%Y-%m")


@pytest.mark.parametrize("texto", [
    "13-2026", "00-2026", "1-2026", "2026-11", "11-26", "11.2026", "abc",
])
def test_mes_invalido(texto):
    with pytest.raises(ValueError):
        converter_mes(texto)


@pytest.mark.parametrize("texto, esperado", [
    ("receita", "receita"), ("Despesa", "despesa"), ("R", "receita"),
    ("d", "despesa"), (" DESPESA ", "despesa"),
])
def test_tipo_valido(texto, esperado):
    assert converter_tipo(texto) == esperado


@pytest.mark.parametrize("texto", ["", "x", "gasto", "receitas"])
def test_tipo_invalido(texto):
    with pytest.raises(ValueError):
        converter_tipo(texto)


PERMITIDAS = ["Alimentação", "Transporte", "Saúde", "Outras despesas"]


@pytest.mark.parametrize("texto, esperado", [
    ("Alimentação", "Alimentação"),
    ("alimentacao", "Alimentação"),
    ("  SAUDE ", "Saúde"),
    ("outras despesas", "Outras despesas"),
])
def test_categoria_valida(texto, esperado):
    assert converter_categoria(texto, PERMITIDAS) == esperado


@pytest.mark.parametrize("texto", ["", "Comida", "Salário", "outras"])
def test_categoria_invalida(texto):
    with pytest.raises(ValueError):
        converter_categoria(texto, PERMITIDAS)