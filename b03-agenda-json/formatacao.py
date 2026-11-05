import re
import unicodedata


def normalizar_telefone(telefone):
    """Deixa um telefone já validado no formato que vai para o JSON.

    Só o + e os dígitos: '(88) 99999-1234' -> '+5588999991234'.
    """

    digitos = re.sub(r'\D', '', telefone)

    # Já veio com +: o código do país está nos dígitos.
    if telefone.strip().startswith('+'):
        return '+' + digitos

    # Brasileiro sem código do país: DDD + 8 ou 9 dígitos = 10 ou 11 dígitos.
    if len(digitos) in (10, 11):
        return '+55' + digitos

    # Brasileiro com 55 na frente, sem o +: 12 ou 13 dígitos.
    return '+' + digitos


def formatar_telefone(telefone):
    """Deixa o telefone guardado legível para mostrar na tela.

    Brasileiro: '+5588999991234' -> '+55 (88) 99999-1234'.
    Internacional: fica do jeito que está guardado.
    """

    if not telefone.startswith('+55'):
        return telefone

    resto = telefone[3:]
    ddd = resto[:2]
    numero = resto[2:]
    return f"+55 ({ddd}) {numero[:-4]}-{numero[-4:]}"


def remover_acentos(texto):
    """Tira os acentos e a cedilha do texto: 'São João' -> 'Sao Joao'."""

    # NFD separa cada letra acentuada em duas partes: a letra e o acento.
    # "é" vira "e" + "´". Depois, fica só com o que não é acento.
    separado = unicodedata.normalize("NFD", texto)
    sem_acentos = ""
    for caractere in separado:
        if not unicodedata.combining(caractere):
            sem_acentos += caractere
    return sem_acentos