"""Desafio extra: quantos tabuleiros cada versão do minimax visita.

Calcula a primeira jogada do computador num tabuleiro vazio com as três
versões e mostra quantos tabuleiros cada uma visitou e quanto tempo levou.

    python desafio.py
"""

import time

from ia import minimax, minimax_alfa_beta, minimax_memo
from tabuleiro import criar, jogadas_validas, jogar

VERSOES = [
    ("Minimax", minimax),
    ("Com poda alfa-beta", minimax_alfa_beta),
    ("Com memoização", minimax_memo),
]


def medir(funcao):
    """Avalia as 9 primeiras jogadas do X num tabuleiro vazio.

    Devolve as notas das 9 jogadas, os tabuleiros visitados e o tempo.
    """

    funcao.chamadas = 0
    inicio = time.perf_counter()

    notas = []
    for casa in jogadas_validas(criar()):
        novo = jogar(criar(), casa, "X")
        notas.append(funcao(novo, "O", "X", 1))

    segundos = time.perf_counter() - inicio
    return notas, funcao.chamadas, segundos


def main():
    """Mede as três versões e mostra a comparação."""

    print("Primeira jogada do X num tabuleiro vazio\n")
    print(f"{'Versão':<20} {'Tabuleiros':>12} {'Tempo':>9}")

    resultados = []
    for nome, funcao in VERSOES:
        notas, tabuleiros, segundos = medir(funcao)
        resultados.append(notas)
        print(f"{nome:<20} {tabuleiros:>12,} {segundos:>8.2f}s"
              .replace(",", "."))

    iguais = all(notas == resultados[0] for notas in resultados)
    print(f"\nAs três versões deram as mesmas notas: "
          f"{'sim' if iguais else 'não'}")
    print(f"Notas das 9 casas: {resultados[0]}")


if __name__ == "__main__":
    main()