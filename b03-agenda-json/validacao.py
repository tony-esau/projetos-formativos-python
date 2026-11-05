import re
from datetime import datetime


def validar_email(email):
    """Diz se o e-mail tem um formato válido, como ana.souza@gmail.com."""

    padrao = re.compile(r"[\w.+-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}")
    return bool(padrao.fullmatch(email))


def validar_telefone(telefone):
    """Diz se o telefone é brasileiro (com ou sem +55) ou internacional (com +).

    Espaços e hífens são ignorados. Parênteses só valem em volta do código
    de área inteiro, como (88) ou (415).
    """

    # Tira só espaços e hífens; os parênteses ficam, para o padrão conferir.
    telefone = re.sub(r'\s', '', telefone)
    telefone = re.sub(r'-', '', telefone)

    # O DDD pode vir com parênteses, (88), ou sem, 88.
    ddd = r'(?:\(\d{2}\)|\d{2})'

    # Duas formas aceitas (o | é "ou"):
    #   brasileiro: (+55 opcional) + DDD + 9 opcional + 8 dígitos
    #   internacional: + país, código de área opcional entre parênteses, número
    brasileiro = r'(?:\+?55)?' + ddd + r'9?\d{8}'
    internacional = r'\+\d{8,15}|\+\d{1,3}\(\d{1,4}\)\d{4,12}'

    padrao = re.compile(brasileiro + '|' + internacional)
    return bool(padrao.fullmatch(telefone))



def validar_aniversario(aniversario):
    """Diz se o aniversário está no formato DD/MM e é uma data que existe.

    '15/03' e '29/02' valem; '31/04' e '15-03' não.
    """

    if not re.fullmatch(r'\d{2}/\d{2}', aniversario):
        return False

    # O strptime recusa datas que não existem, como 31/04.
    # 2024 foi bissexto, então 29/02 é aceito.
    try:
        datetime.strptime(aniversario + "/2024", "%d/%m/%Y")
    except ValueError:
        return False
    return True