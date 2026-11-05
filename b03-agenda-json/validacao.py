import re


def validar_email(email):
    padrao = re.compile(r"[\w.+-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}")
    return bool(padrao.fullmatch(email))


def validar_telefone(telefone):
    # Tira só espaços e hífens; os parênteses ficam, para o padrão conferir.
    telefone = re.sub(r'\s', '', telefone)
    telefone = re.sub(r'-', '', telefone)

    # O DDD pode vir com parênteses, (88), ou sem, 88.
    ddd = r'(?:\(\d{2}\)|\d{2})'

    # Brasileiro: (+55 opcional) + DDD + 9 opcional + 8 dígitos.
    # Internacional: + país, código de área opcional entre parênteses, número.
    brasileiro = r'(?:\+?55)?' + ddd + r'9?\d{8}'
    internacional = r'\+\d{8,15}|\+\d{1,3}\(\d{1,4}\)\d{4,12}'

    padrao = re.compile(brasileiro + '|' + internacional)
    return bool(padrao.fullmatch(telefone))