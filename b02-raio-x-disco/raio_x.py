import sys
from pathlib import Path
import shutil
from collections import defaultdict

from utils import barra_proporcional, formatar_bytes

# python raio_x.py [-h] [CAMINHO]

OPCOES_AJUDA = {"-h", "--help", "-help"}
TOP = 10  # quantos itens aparecem em cada ranking
RAIZ = "(arquivos na raiz)"  # chave dos arquivos soltos na pasta analisada

TEXTO_AJUDA = """------------------- Raio-X do disco -------------------

Varre uma pasta e todas as suas subpastas e mostra onde
está o espaço ocupado: tamanho total, maiores arquivos,
subpastas mais pesadas e tamanho por extensão.

Uso: python raio_x.py [-h] [CAMINHO]

CAMINHO
  Pasta a ser analisada. Se não for informada, o
  programa pergunta. Use aspas se o caminho tiver
  espaços.

-h, --help
  Mostra esta ajuda.

Exemplos:
  python raio_x.py C:\\Users\\joao\\Downloads
  python raio_x.py "C:\\Minha Pasta"
  python raio_x.py ."""


def encerrar_com_erro(mensagem):
    """Mostra uma mensagem de erro e encerra com código 1."""

    print(f"Erro: {mensagem}")
    print("Use -h para ver a ajuda.")
    sys.exit(1)


def limpar_texto_caminho(texto):
    """Remove espaços e aspas das pontas (ex.: "Copiar como caminho")."""

    return texto.strip().strip('"')


def separar_argumentos(argumentos):
    """Separa o que é opção (começa com '-') do que é caminho.

    Retorno: (conjunto de opções, lista de caminhos em texto).
    """

    opcoes = {a for a in argumentos if a.startswith("-")}
    caminhos = [limpar_texto_caminho(a) for a in argumentos
                if not a.startswith("-")]

    desconhecidas = opcoes - OPCOES_AJUDA
    if desconhecidas:
        encerrar_com_erro(
            f"opção desconhecida: {', '.join(sorted(desconhecidas))}")

    return opcoes, caminhos


def ler_caminho():
    """Pergunta a pasta quando o usuário não informou nenhuma.

    Retorno: Path absoluto de uma pasta que existe.
    """

    while True:
        texto = input("Digite o caminho (ou só Enter para a pasta atual): ")
        caminho = Path(limpar_texto_caminho(texto))

        if caminho.is_dir():
            return caminho.resolve()

        print("Pasta não encontrada!")
        print("Digite 'q' para sair ou pressione Enter para tentar de novo.")
        if input().strip().lower() == "q":
            sys.exit(0)


def obter_pasta(caminhos):
    """Decide qual pasta será analisada.

    - Nenhum caminho: pergunta ao usuário.
    - Mais de um: erro (provavelmente faltaram aspas).
    - Um: usa, se for uma pasta válida.
    Retorno: Path absoluto de uma pasta que existe.
    """

    if not caminhos:
        return ler_caminho()

    if len(caminhos) > 1:
        encerrar_com_erro(
            f"foram informados {len(caminhos)} caminhos. "
            "Se o caminho tem espaços, coloque-o entre aspas.")

    pasta = Path(caminhos[0])
    if not pasta.is_dir():
        encerrar_com_erro(f"a pasta '{caminhos[0]}' não existe.")

    return pasta.resolve()


def varrer(pasta):
    """Percorre a pasta e todas as subpastas uma única vez.

    Retorno: um dicionário com tudo o que o relatório precisa.
    """

    dados = {
        "total": 0,           # soma dos tamanhos dos arquivos, em bytes
        "n_arquivos": 0,
        "n_pastas": 0,
        "arquivos": [],       # pares (tamanho, caminho) para o ranking
        "ignorados": 0,       # itens que não puderam ser lidos
        # Toda chave nova começa em 0, então dá para somar direto.
        "por_subpasta": defaultdict(int),
    }

    # .rglob("*") percorre recursivamente todos os arquivos e pastas.
    for item in pasta.rglob("*"):
        try:
            if item.is_file():
                # .stat().st_size é o tamanho do arquivo em bytes.
                tamanho = item.stat().st_size
                dados["total"] += tamanho
                dados["n_arquivos"] += 1
                dados["arquivos"].append((tamanho, item))

                # Subpasta do primeiro nível onde o arquivo está. Se o
                # caminho relativo tem um pedaço só, o arquivo está na raiz.
                partes = item.relative_to(pasta).parts
                subpasta = partes[0] if len(partes) > 1 else RAIZ
                dados["por_subpasta"][subpasta] += tamanho
            elif item.is_dir():
                dados["n_pastas"] += 1
            # O que não é arquivo nem pasta (ex.: link quebrado) é ignorado.
        except OSError:
            # Sem permissão, arquivo apagado no meio da varredura etc.
            dados["ignorados"] += 1

    return dados


def imprimir_resumo(pasta, dados):
    """Cabeçalho com o total, o número de arquivos e o de pastas."""

    print(f"Raio-X de: {pasta}\n")
    print(f"Total: {formatar_bytes(dados['total'])} em "
          f"{dados['n_arquivos']} arquivo(s) e {dados['n_pastas']} pasta(s)")


def imprimir_maiores(pasta, dados):
    """Ranking dos maiores arquivos, com o caminho relativo à pasta."""

    # Tuplas são ordenadas pelo primeiro elemento: o tamanho.
    maiores = sorted(dados["arquivos"], reverse=True)[:TOP]

    print("\nMaiores arquivos")
    for posicao, (tamanho, arquivo) in enumerate(maiores, start=1):
        relativo = arquivo.relative_to(pasta)
        print(f"  {posicao:>2}.  {formatar_bytes(tamanho):>9}  {relativo}")


def imprimir_subpastas(dados):
    """Subpastas do primeiro nível ordenadas pelo tamanho."""

    if not dados["por_subpasta"]:
        return

    # .items() dá pares (nome, tamanho); ordena pelo tamanho.
    ordenadas = sorted(dados["por_subpasta"].items(),
                       key=lambda par: par[1], reverse=True)[:TOP]

    largura = max(len(nome) for nome, _ in ordenadas)
    total = dados["total"]

    print("\nSubpastas por tamanho")
    for nome, tamanho in ordenadas:
        # Evita divisão por zero numa pasta só com arquivos vazios.
        porcentagem = tamanho / total * 100 if total else 0
        barra = barra_proporcional(porcentagem)
        print(f"  {nome:<{largura}}  {barra}  {formatar_bytes(tamanho):>9}"
              f"  {porcentagem:5.1f}%")


def imprimir_rodape(dados):
    """Avisos finais, como itens que não puderam ser lidos."""

    if dados["ignorados"]:
        print(f"\nItens ignorados: {dados['ignorados']} "
              "(sem permissão ou inacessíveis)")


def main():
    """Fluxo principal: argumentos -> pasta -> varredura -> relatório."""

    opcoes, caminhos = separar_argumentos(sys.argv[1:])

    if opcoes & OPCOES_AJUDA:
        print(TEXTO_AJUDA)
        return

    pasta = obter_pasta(caminhos)
    dados = varrer(pasta)

    imprimir_resumo(pasta, dados)
    imprimir_maiores(pasta, dados)
    imprimir_subpastas(dados)
    imprimir_rodape(dados)


if __name__ == "__main__":
    main()