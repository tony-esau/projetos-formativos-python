import os
import sys
from pathlib import Path
from collections import defaultdict

from relatorio import (
    imprimir_disco,
    imprimir_extensoes,
    imprimir_maiores,
    imprimir_resumo,
    imprimir_rodape,
    imprimir_subpastas,
)

# python raio_x.py [-h] [-n N] [CAMINHO]

OPCOES_AJUDA = {"-h", "--help", "-help"}
OPCOES_TOP = {"-n", "--top"}  # opções que recebem um número logo depois
TOP_PADRAO = 10  # quantos itens aparecem em cada ranking, se -n não vier
RAIZ = "(arquivos na raiz)"  # chave dos arquivos soltos na pasta analisada
SEM_EXTENSAO = "(sem extensão)"  # chave dos arquivos sem extensão

TEXTO_AJUDA = """------------------- Raio-X do disco -------------------

Varre uma pasta e todas as suas subpastas e mostra onde
está o espaço ocupado: tamanho total, maiores arquivos,
subpastas mais pesadas e tamanho por extensão.

Uso: python raio_x.py [-h] [-n N] [CAMINHO]

CAMINHO
  Pasta a ser analisada. Se não for informada, o
  programa pergunta. Use aspas se o caminho tiver
  espaços.

-n N, --top N
  Quantos itens mostrar em cada ranking (padrão: 10).

-h, --help
  Mostra esta ajuda.

Exemplos:
  python raio_x.py C:\\Users\\joao\\Downloads
  python raio_x.py "C:\\Minha Pasta" -n 5
  python raio_x.py ."""


def encerrar_com_erro(mensagem):
    """Mostra uma mensagem de erro e encerra com código 1."""

    print(f"Erro: {mensagem}")
    print("Use -h para ver a ajuda.")
    sys.exit(1)


def limpar_texto_caminho(texto):
    """Remove espaços e aspas das pontas (ex.: "Copiar como caminho")."""

    return texto.strip().strip('"')


def ler_top(texto):
    """Converte o valor do -n num inteiro positivo, ou encerra com erro."""

    try:
        top = int(texto)
    except ValueError:
        encerrar_com_erro(f"-n precisa de um número inteiro, não '{texto}'.")
    if top < 1:
        encerrar_com_erro("-n precisa ser pelo menos 1.")
    return top


def separar_argumentos(argumentos):
    """Separa as opções, os caminhos e o valor do -n.

    O -n é diferente das outras opções: o item seguinte da lista é o
    valor dele, e não um caminho. Por isso a lista é percorrida com um
    índice, que pula duas posições quando encontra o -n.

    Retorno: (conjunto de opções, lista de caminhos em texto, top).
    """

    opcoes = set()
    caminhos = []
    top = TOP_PADRAO

    i = 0
    while i < len(argumentos):
        atual = argumentos[i]

        if atual in OPCOES_TOP:
            if i + 1 >= len(argumentos):
                encerrar_com_erro(f"{atual} precisa de um número depois.")
            top = ler_top(argumentos[i + 1])
            i += 2      # pula o -n e o número
            continue

        if atual.startswith("-"):
            opcoes.add(atual)
        else:
            caminhos.append(limpar_texto_caminho(atual))
        i += 1

    desconhecidas = opcoes - OPCOES_AJUDA
    if desconhecidas:
        encerrar_com_erro(
            f"opção desconhecida: {', '.join(sorted(desconhecidas))}")

    return opcoes, caminhos, top


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

    Usa os.walk em vez de rglob porque o os.walk avisa (pelo onerror)
    quando não consegue abrir uma pasta; o rglob pula em silêncio.

    Retorno: um dicionário com tudo o que o relatório precisa.
    """

    dados = {
        "total": 0,           # soma dos tamanhos dos arquivos, em bytes
        "n_arquivos": 0,
        "n_pastas": 0,
        "arquivos": [],       # pares (tamanho, caminho) para o ranking
        "ignorados": 0,       # arquivos que não puderam ser lidos
        "sem_permissao": [],  # pastas que não puderam ser abertas
        "links_quebrados": 0, # atalhos que apontam para algo que não existe
        # Toda chave nova começa em 0, então dá para somar direto.
        "por_subpasta": defaultdict(int),
        "por_extensao": defaultdict(int),
    }

    def registrar_pasta_inacessivel(erro):
        """Chamada pelo os.walk quando uma pasta não pode ser aberta."""
        dados["sem_permissao"].append(erro.filename)

    # Em cada passo, o os.walk entrega uma pasta, os nomes das subpastas
    # dela e os nomes dos arquivos dela, descendo até o fim da árvore.
    for raiz, subpastas, nomes in os.walk(
            pasta, onerror=registrar_pasta_inacessivel):
        dados["n_pastas"] += len(subpastas)

        for nome in nomes:
            item = Path(raiz) / nome
            try:
                # Link cujo destino não existe: conta e segue.
                if item.is_symlink() and not item.exists():
                    dados["links_quebrados"] += 1
                    continue

                # .stat().st_size é o tamanho do arquivo em bytes.
                tamanho = item.stat().st_size
            except OSError:
                # Sem permissão, arquivo apagado no meio da varredura etc.
                dados["ignorados"] += 1
                continue

            dados["total"] += tamanho
            dados["n_arquivos"] += 1
            dados["arquivos"].append((tamanho, item))

            # Subpasta do primeiro nível onde o arquivo está. Se o
            # caminho relativo tem um pedaço só, o arquivo está na raiz.
            partes = item.relative_to(pasta).parts
            subpasta = partes[0] if len(partes) > 1 else RAIZ
            dados["por_subpasta"][subpasta] += tamanho

            # Extensão em minúsculas; string vazia conta como falsa,
            # então arquivos sem extensão caem em SEM_EXTENSAO.
            extensao = item.suffix.lower() or SEM_EXTENSAO
            dados["por_extensao"][extensao] += tamanho

    return dados


def main():
    """Fluxo principal: argumentos -> pasta -> varredura -> relatório."""

    opcoes, caminhos, top = separar_argumentos(sys.argv[1:])

    if opcoes & OPCOES_AJUDA:
        print(TEXTO_AJUDA)
        return

    pasta = obter_pasta(caminhos)
    dados = varrer(pasta)

    imprimir_resumo(pasta, dados)
    imprimir_maiores(pasta, dados, top)
    imprimir_subpastas(dados, top)
    imprimir_extensoes(dados, top)
    imprimir_disco(pasta)
    imprimir_rodape(dados)


if __name__ == "__main__":
    main()