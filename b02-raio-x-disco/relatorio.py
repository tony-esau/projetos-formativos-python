"""Impressão do relatório do Raio-X.

Cada função recebe o dicionário montado por varrer() e imprime uma seção.
"""

import shutil

from utils import barra_proporcional, formatar_bytes

TOP = 10  # valor padrão; o raio_x.py passa o que veio do -n


def imprimir_resumo(pasta, dados):
    """Cabeçalho com o total, o número de arquivos e o de pastas."""

    print(f"Raio-X de: {pasta}\n")
    print(f"Total: {formatar_bytes(dados['total'])} em "
          f"{dados['n_arquivos']} arquivo(s) e {dados['n_pastas']} pasta(s)")


def imprimir_maiores(pasta, dados, top=TOP):
    """Ranking dos maiores arquivos, com o caminho relativo à pasta."""

    # Tuplas são ordenadas pelo primeiro elemento: o tamanho.
    maiores = sorted(dados["arquivos"], reverse=True)[:top]

    print("\nMaiores arquivos")
    for posicao, (tamanho, arquivo) in enumerate(maiores, start=1):
        relativo = arquivo.relative_to(pasta)
        print(f"  {posicao:>2}.  {formatar_bytes(tamanho):>9}  {relativo}")


def imprimir_ranking(titulo, tamanhos, total, top=TOP):
    """Mostra um dicionário nome -> tamanho, do maior para o menor.

    Usada pelas seções de subpastas e de extensões: a lógica é a mesma,
    só mudam o título e os dados.
    """

    if not tamanhos:
        return

    # .items() dá pares (nome, tamanho); ordena pelo tamanho, o 2º elemento.
    ordenados = sorted(tamanhos.items(),
                       key=lambda par: par[1], reverse=True)[:top]

    largura = max(len(nome) for nome, _ in ordenados)

    print(f"\n{titulo}")
    for nome, tamanho in ordenados:
        # Evita divisão por zero numa pasta só com arquivos vazios.
        porcentagem = tamanho / total * 100 if total else 0
        barra = barra_proporcional(porcentagem)
        print(f"  {nome:<{largura}}  {barra}  {formatar_bytes(tamanho):>9}"
              f"  {porcentagem:5.1f}%")


def imprimir_subpastas(dados, top=TOP):
    """Subpastas do primeiro nível ordenadas pelo tamanho."""
    imprimir_ranking("Subpastas por tamanho",
                     dados["por_subpasta"], dados["total"], top)


def imprimir_extensoes(dados, top=TOP):
    """Tipos de arquivo ordenados pelo espaço que ocupam."""
    imprimir_ranking("Tamanho por extensão",
                     dados["por_extensao"], dados["total"], top)


def imprimir_disco(pasta):
    """Espaço total, usado e livre do disco onde a pasta está."""

    disco = shutil.disk_usage(pasta)
    livre_pct = disco.free / disco.total * 100 if disco.total else 0
    print(f"\nDisco: {formatar_bytes(disco.total)} no total, "
          f"{formatar_bytes(disco.used)} usados, "
          f"{formatar_bytes(disco.free)} livres ({livre_pct:.0f}%)")


def imprimir_rodape(dados):
    """Avisos finais: o que ficou de fora da contagem e por quê."""

    pastas = dados["sem_permissao"]
    avisos = []
    if pastas:
        avisos.append(f"{len(pastas)} pasta(s) sem permissão de leitura")
    if dados["links_quebrados"]:
        avisos.append(f"{dados['links_quebrados']} link(s) quebrado(s)")
    if dados["ignorados"]:
        avisos.append(f"{dados['ignorados']} arquivo(s) que não puderam "
                      "ser lidos")

    if not avisos:
        return

    print("\nIgnorados na contagem:")
    for aviso in avisos:
        print(f"  - {aviso}")
    # Mostra algumas das pastas, para o usuário saber onde estão.
    for caminho in pastas[:5]:
        print(f"      {caminho}")
    if len(pastas) > 5:
        print(f"      ... e mais {len(pastas) - 5}")