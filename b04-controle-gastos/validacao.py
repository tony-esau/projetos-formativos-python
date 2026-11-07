import re
import unicodedata
from datetime import date, datetime
from decimal import Decimal

TIPOS = ["receita", "despesa"]


def converter_valor(texto):
    """Converte '12,50' ou '12.50' em Decimal('12.50').

    Aceita até duas casas decimais, com vírgula ou ponto. Recusa texto vazio,
    letras, separador de milhar, zero e valores negativos.
    """

    texto = texto.strip()

    if texto == "":
        raise ValueError("o valor está vazio")
    if texto.startswith("-"):
        raise ValueError("o valor não pode ser negativo")
    if not re.fullmatch(r"\d+([.,]\d{1,2})?", texto):
        raise ValueError(f"'{texto}' não é um valor válido, use 12,50")

    valor = Decimal(texto.replace(",", "."))
    if valor == 0:
        raise ValueError("o valor precisa ser maior que zero")

    # quantize deixa sempre com duas casas: 12 vira 12.00, 12.5 vira 12.50.
    return valor.quantize(Decimal("0.01"))


def converter_data(texto):
    """Converte 'DD/MM/AAAA' num date. Texto vazio vira a data de hoje.

    Recusa formatos diferentes e datas que não existem, como 31/02/2026.
    """

    texto = texto.strip()

    if texto == "":
        return date.today()
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", texto):
        raise ValueError(f"'{texto}' não está no formato DD/MM/AAAA")

    try:
        return datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError(f"a data {texto} não existe")


def converter_mes(texto):
    """Converte um mês digitado como 'MM-AAAA' (ou 'MM/AAAA') em 'AAAA-MM'.

    Por dentro o programa usa 'AAAA-MM', que é o começo das datas guardadas
    no CSV e deixa os nomes dos relatórios em ordem cronológica.
    Texto vazio vira o mês atual. Recusa meses fora de 01 a 12.
    """

    texto = texto.strip()

    if texto == "":
        return date.today().strftime("%Y-%m")

    encontrado = re.fullmatch(r"(\d{2})[-/](\d{4})", texto)
    if not encontrado:
        raise ValueError(f"'{texto}' não está no formato MM-AAAA")

    mes, ano = encontrado.groups()
    if not 1 <= int(mes) <= 12:
        raise ValueError(f"o mês {mes} não existe")
    return f"{ano}-{mes}"


def converter_tipo(texto):
    """Converte o texto em 'receita' ou 'despesa'.

    Aceita maiúsculas e as iniciais: 'R' vira 'receita', 'd' vira 'despesa'.
    """

    texto = texto.strip().lower()

    for tipo in TIPOS:
        if texto in (tipo, tipo[0]):
            return tipo
    raise ValueError(f"'{texto}' não é um tipo válido, use receita ou despesa")


def remover_acentos(texto):
    """Tira os acentos e a cedilha do texto: 'Alimentação' -> 'Alimentacao'."""

    separado = unicodedata.normalize("NFD", texto)
    sem_acentos = ""
    for caractere in separado:
        if not unicodedata.combining(caractere):
            sem_acentos += caractere
    return sem_acentos


def comparavel(texto):
    """Deixa o texto pronto para comparar: sem acentos e em minúsculas."""

    return remover_acentos(texto.strip()).lower()


def converter_nova_categoria(texto, existentes):
    """Confere o nome de uma categoria nova e devolve ele já limpo.

    Recusa nome vazio, nome com mais de 20 letras e nome que já existe,
    ignorando acentos e maiúsculas.
    """

    nome = texto.strip()

    if nome == "":
        raise ValueError("o nome está vazio")
    if len(nome) > 20:
        raise ValueError("use no máximo 20 caracteres")
    for existente in existentes:
        if comparavel(nome) == comparavel(existente):
            raise ValueError(f"a categoria {existente} já existe")
    return nome


def converter_categoria(texto, permitidas):
    """Devolve a categoria da lista permitidas que corresponde ao texto.

    A comparação ignora acentos e maiúsculas: 'alimentacao' devolve
    'Alimentação', escrita do jeito que está no categorias.json.
    """

    for categoria in permitidas:
        if comparavel(texto) == comparavel(categoria):
            return categoria

    opcoes = ", ".join(permitidas)
    raise ValueError(f"'{texto.strip()}' não é uma categoria válida. "
                     f"Use uma destas: {opcoes}")