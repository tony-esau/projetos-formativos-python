import re


def validar_email(email):
    padrao = re.compile(r"[\w.+-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}")
    return bool(padrao.fullmatch(email))


def validar_telefone(telefone):
    telefone = re.sub(r'\s', '', telefone)
    telefone = re.sub(r'-', '', telefone)

    ddd = r'(?:\(\d{2}\)|\d{2})'

    brasileiro = r'(?:\+?55)?' + ddd + r'9?\d{8}'
    internacional = r'\+\d{8,15}|\+\d{1,3}\(\d{1,4}\)\d{4,12}'

    padrao = re.compile(brasileiro + '|' + internacional)
    return bool(padrao.fullmatch(telefone))