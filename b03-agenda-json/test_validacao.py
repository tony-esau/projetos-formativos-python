import pytest

from validacao import validar_email, validar_telefone, validar_aniversario


EMAILS_VALIDOS = [
    "ana@gmail.com",
    "ana.souza@gmail.com",
    "ana_souza@gmail.com",
    "ana-souza@gmail.com",
    "ana.souza+trabalho@gmail.com",
    "ana123@gmail.com",
    "ANA@GMAIL.COM",
    "ana@ufca.edu.br",
    "ana@mail.site2.com",
    "ana@mail.meu-site.com",
    "josé@gmail.com",
]

EMAILS_INVALIDOS = [
    "",
    "ana",
    "ana@",
    "@gmail.com",
    "ana@gmail",
    "ana gmail.com",
    "ana@@gmail.com",
    "ana @gmail.com",
    "ana@gmail .com",
    "ana@gmail.c",
    "ana@gmail.com.",
    "ana@.com",
    "ana@gmail..com",
    "ana@gm_ail.com",
    "ana@gmail.c0m",
]

TELEFONES_VALIDOS = [
    "(88) 99999-1234",
    "(88)99999-1234",
    "88 99999-1234",
    "88999991234",
    "(88) 3521-1234",
    "55 88 99999-1234",
    "55 (88) 99999-1234",
    "+55 88 99999-1234",
    "+55 (88) 99999-1234",
    "+1 (415) 555-2671",
    "+44 7911 123456",
    "+351 912 345 678",
]

TELEFONES_INVALIDOS = [
    "",
    "( )",
    "99999-1234",
    "(88 99999-1234",
    "88) 99999-1234",
    ")88( 99999-1234",
    "(88) (99) 999-1234",
    "() 88 99999-1234",
    "((88)) 99999-1234",
    "(8a) 99999-1234",
    "(88 9 922341414",
    "8899a-1234",
    "88.99999.1234",
    "88 +99999-1234",
    "1 415 555 2671",
]


@pytest.mark.parametrize("email", EMAILS_VALIDOS)
def test_email_valido(email):
    assert validar_email(email)


@pytest.mark.parametrize("email", EMAILS_INVALIDOS)
def test_email_invalido(email):
    assert not validar_email(email)


@pytest.mark.parametrize("telefone", TELEFONES_VALIDOS)
def test_telefone_valido(telefone):
    assert validar_telefone(telefone)


@pytest.mark.parametrize("telefone", TELEFONES_INVALIDOS)
def test_telefone_invalido(telefone):
    assert not validar_telefone(telefone)


@pytest.mark.parametrize("aniversario", [
    "15/03", "01/01", "31/12", "29/02", "30/04",
])
def test_aniversario_valido(aniversario):
    assert validar_aniversario(aniversario)


@pytest.mark.parametrize("aniversario", [
    "", "15-03", "15/3", "5/03", "15/03/2000", "32/01",
    "31/04", "30/02", "00/05", "15/13", "aa/bb",
])
def test_aniversario_invalido(aniversario):
    assert not validar_aniversario(aniversario)