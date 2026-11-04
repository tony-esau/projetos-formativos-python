"""Impressão do relatório do Raio-X.

Cada função recebe o dicionário montado por varrer() e imprime uma seção.
"""

import shutil

from utils import barra_proporcional, formatar_bytes

TOP = 10  # quantos itens aparecem em cada ranking


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


def imprimir_ranking(titulo, tamanhos, total):
    """Mostra um dicionário nome -> tamanho, do maior para o menor.

    Usada pelas seções de subpastas e de extensões: a lógica é a mesma,
    só mudam o título e os dados.
    """

    if not tamanhos:
        return

    # .items() dá pares (nome, tamanho); ordena pelo tamanho, o 2º elemento.
    ordenados = sorted(tamanhos.items(),
                       key=lambda par: par[1], reverse=True)[:TOP]

    largura = max(len(nome) for nome, _ in ordenados)

    print(f"\n{titulo}")
    for nome, tamanho in ordenados:
        # Evita divisão por zero numa pasta só com arquivos vazios.
        porcentagem = tamanho / total * 100 if total else 0
        barra = barra_proporcional(porcentagem)
        print(f"  {nome:<{largura}}  {barra}  {formatar_bytes(tamanho):>9}"
              f"  {porcentagem:5.1f}%")


def imprimir_subpastas(dados):
    """Subpastas do primeiro nível ordenadas pelo tamanho."""
    imprimir_ranking("Subpastas por tamanho",
                     dados["por_subpasta"], dados["total"])


def imprimir_extensoes(dados):
    """Tipos de arquivo ordenados pelo espaço que ocupam."""
    imprimir_ranking("Tamanho por extensão",
                     dados["por_extensao"], dados["total"])


def imprimir_disco(pasta):
    """Espaço total, usado e livre do disco onde a pasta está."""

    disco = shutil.disk_usage(pasta)
    livre_pct = disco.free / disco.total * 100 if disco.total else 0
    print(f"\nDisco: {formatar_bytes(disco.total)} no total, "
          f"{formatar_bytes(disco.used)} usados, "
          f"{formatar_bytes(disco.free)} livres ({livre_pct:.0f}%)")


def imprimir_rodape(dados):
    """Avisos finais, como itens que não puderam ser lidos."""

    if dados["ignorados"]:
        print(f"\nItens ignorados: {dados['ignorados']} "
              "(sem permissão ou inacessíveis)")