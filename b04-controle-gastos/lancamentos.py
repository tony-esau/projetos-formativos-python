import csv
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from validacao import (converter_categoria, converter_tipo,
                       converter_valor)

PASTA = Path(__file__).parent
CAMINHO_PADRAO = PASTA / "dados" / "lancamentos.csv"
CAMINHO_CATEGORIAS = PASTA / "categorias.json"
CAMINHO_ORCAMENTO = PASTA / "orcamento.json"

# A ordem das colunas no CSV.
CAMPOS = ["data", "tipo", "valor", "categoria", "descricao"]


def carregar_categorias(caminho=CAMINHO_CATEGORIAS):
    """Lê o categorias.json e devolve o dicionário {tipo: [categorias]}."""

    return json.loads(caminho.read_text(encoding="utf-8"))


def carregar_orcamento(caminho=CAMINHO_ORCAMENTO):
    """Lê o orcamento.json e devolve {categoria: limite como Decimal}.

    Sem o arquivo, devolve um dicionário vazio, e o relatório sai sem a
    parte do orçamento.
    """

    if not caminho.exists():
        return {}

    # parse_float e parse_int fazem o json já criar Decimal, em vez de float.
    texto = caminho.read_text(encoding="utf-8")
    return json.loads(texto, parse_float=Decimal, parse_int=Decimal)


def salvar_categorias(categorias, caminho=CAMINHO_CATEGORIAS):
    """Grava o dicionário {tipo: [categorias]} no categorias.json."""

    texto = json.dumps(categorias, ensure_ascii=False, indent=2)
    caminho.write_text(texto + "\n", encoding="utf-8")


def salvar_orcamento(orcamento, caminho=CAMINHO_ORCAMENTO):
    """Grava o dicionário {categoria: limite} no orcamento.json."""

    # O json não sabe gravar Decimal. Com duas casas, o float é escrito
    # exatamente como o valor digitado (150.5 vira 150.5), e o
    # carregar_orcamento volta a ler como Decimal.
    numeros = {categoria: float(limite)
               for categoria, limite in orcamento.items()}
    texto = json.dumps(numeros, ensure_ascii=False, indent=2)
    caminho.write_text(texto + "\n", encoding="utf-8")


def converter_linha(linha, categorias=None):
    """Transforma uma linha do CSV (só textos) num lançamento.

    No lançamento, a data vira date e o valor vira Decimal. Se algum campo
    for inválido, levanta ValueError com o motivo. Se categorias for
    informado, a categoria também precisa ser uma das permitidas para o tipo.
    """

    try:
        data = date.fromisoformat(linha["data"].strip())
    except ValueError:
        raise ValueError(f"data inválida: '{linha['data']}'")

    tipo = converter_tipo(linha["tipo"])
    valor = converter_valor(linha["valor"])

    categoria = linha["categoria"].strip()
    if categorias is not None:
        categoria = converter_categoria(categoria, categorias[tipo])
    elif categoria == "":
        raise ValueError("a categoria está vazia")

    return {
        "data": data,
        "tipo": tipo,
        "valor": valor,
        "categoria": categoria,
        "descricao": linha["descricao"].strip(),
    }


def ler_lancamentos(caminho=CAMINHO_PADRAO, categorias=None):
    """Lê um CSV de lançamentos e devolve (validos, invalidos).

    validos é a lista de lançamentos convertidos. invalidos é uma lista de
    (número da linha, motivo) com as linhas que foram puladas. Um arquivo que
    ainda não existe devolve duas listas vazias.
    """

    if not caminho.exists():
        return [], []

    validos = []
    invalidos = []

    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)

        faltando = set(CAMPOS) - set(leitor.fieldnames or [])
        if faltando:
            colunas = ", ".join(sorted(faltando))
            raise ValueError(f"o arquivo não tem as colunas: {colunas}")

        # A linha 1 é o cabeçalho, então os dados começam na linha 2.
        for numero, linha in enumerate(leitor, start=2):
            try:
                validos.append(converter_linha(linha, categorias))
            except (ValueError, AttributeError) as erro:
                # AttributeError: linha com colunas a menos vem com None.
                invalidos.append((numero, str(erro)))

    return validos, invalidos


def para_linha(lancamento):
    """Transforma um lançamento numa linha de textos, pronta para o CSV."""

    return {
        "data": lancamento["data"].isoformat(),
        "tipo": lancamento["tipo"],
        "valor": str(lancamento["valor"]),
        "categoria": lancamento["categoria"],
        "descricao": lancamento["descricao"],
    }


def adicionar_lancamento(lancamento, caminho=CAMINHO_PADRAO):
    """Acrescenta um lançamento no fim do CSV.

    Se o arquivo ainda não existe (ou está vazio), escreve o cabeçalho antes.
    """

    caminho.parent.mkdir(parents=True, exist_ok=True)
    precisa_cabecalho = not caminho.exists() or caminho.stat().st_size == 0

    # "a" abre para acrescentar no fim, sem apagar o que já existe.
    with open(caminho, "a", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        if precisa_cabecalho:
            escritor.writeheader()
        escritor.writerow(para_linha(lancamento))


def filtrar_mes(lancamentos, mes):
    """Devolve os lançamentos do mês 'AAAA-MM', em ordem de data."""

    do_mes = []
    for lancamento in lancamentos:
        if lancamento["data"].strftime("%Y-%m") == mes:
            do_mes.append(lancamento)
    return sorted(do_mes, key=lambda lancamento: lancamento["data"])


def importar_csv(origem, categorias, destino=CAMINHO_PADRAO):
    """Copia os lançamentos válidos de outro CSV para o arquivo principal.

    Cada linha passa pelas mesmas conversões do menu, inclusive a das
    categorias. Devolve (quantidade importada, invalidos), em que invalidos
    é a lista de (número da linha, motivo) das linhas puladas.
    """

    validos, invalidos = ler_lancamentos(origem, categorias)
    for lancamento in validos:
        adicionar_lancamento(lancamento, destino)
    return len(validos), invalidos