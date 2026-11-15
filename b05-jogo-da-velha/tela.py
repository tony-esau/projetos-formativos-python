import os
import subprocess

from tabuleiro import VAZIO


def limpar_tela():
    """Apaga tudo o que está no terminal."""

    if os.name == "nt":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)


def desenhar_tabuleiro(tab):
    """Devolve o tabuleiro como texto, com o número das casas livres.

    As casas são numeradas de 1 a 9 para o jogador, embora os índices da
    lista vão de 0 a 8.
    """

    celulas = []
    for casa, valor in enumerate(tab):
        if valor == VAZIO:
            celulas.append(str(casa + 1))
        else:
            celulas.append(valor)

    linhas = []
    for inicio in (0, 3, 6):
        a, b, c = celulas[inicio:inicio + 3]
        linhas.append(f" {a} | {b} | {c} ")
    return "\n---+---+---\n".join(linhas)