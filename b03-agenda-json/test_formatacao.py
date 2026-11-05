import pytest

from formatacao import normalizar_telefone, formatar_telefone, remover_acentos
from test_validacao import TELEFONES_VALIDOS


@pytest.mark.parametrize("digitado, guardado", [
    ("(88) 99999-1234", "+5588999991234"),
    ("(88)99999-1234", "+5588999991234"),
    ("88 99999-1234", "+5588999991234"),
    ("88999991234", "+5588999991234"),
    ("55 88 99999-1234", "+5588999991234"),
    ("55 (88) 99999-1234", "+5588999991234"),
    ("+55 88 99999-1234", "+5588999991234"),
    ("+55 (88) 99999-1234", "+5588999991234"),
    ("(88) 3521-1234", "+558835211234"),
    ("55 99999-1234", "+5555999991234"),
    ("+1 (415) 555-2671", "+14155552671"),
    ("+44 7911 123456", "+447911123456"),
    ("+351 912 345 678", "+351912345678"),
])
def test_normalizar_telefone(digitado, guardado):
    assert normalizar_telefone(digitado) == guardado


@pytest.mark.parametrize("guardado, mostrado", [
    ("+5588999991234", "+55 (88) 99999-1234"),
    ("+558835211234", "+55 (88) 3521-1234"),
    ("+14155552671", "+14155552671"),
    ("+447911123456", "+447911123456"),
])
def test_formatar_telefone(guardado, mostrado):
    assert formatar_telefone(guardado) == mostrado


@pytest.mark.parametrize("telefone", TELEFONES_VALIDOS)
def test_normalizar_duas_vezes_nao_muda(telefone):
    # O formato guardado, se passar de novo pela normalização, continua igual.
    guardado = normalizar_telefone(telefone)
    assert normalizar_telefone(guardado) == guardado


def test_formas_diferentes_do_mesmo_numero_viram_uma_so():
    formas = ["(88) 99999-1234", "88999991234",
              "+55 (88) 99999-1234", "55 88 99999-1234"]
    guardados = {normalizar_telefone(f) for f in formas}
    assert guardados == {"+5588999991234"}


@pytest.mark.parametrize("entrada, esperado", [
    ("José", "Jose"),
    ("ÁÉÍÓÚ", "AEIOU"),
    ("ação", "acao"),
    ("pão de açúcar", "pao de acucar"),
    ("Müller", "Muller"),
    ("à vontade", "a vontade"),
    ("sem acento", "sem acento"),
    ("", ""),
])
def test_remover_acentos(entrada, esperado):
    assert remover_acentos(entrada) == esperado


def test_busca_ignora_acento_e_maiuscula():
    # É assim que a busca da agenda vai comparar os nomes.
    nome = "José da Silva"
    busca = "jose"
    assert remover_acentos(busca).lower() in remover_acentos(nome).lower()