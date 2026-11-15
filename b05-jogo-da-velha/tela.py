"""Funções que desenham o jogo no terminal."""

import os
import subprocess

from tabuleiro import VAZIO


def limpar_tela():
    """Apaga tudo o que está no terminal (cls no Windows, clear no resto)."""

    if os.name == "nt":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)


# Quanto o cursor anda em cada direção. O tabuleiro tem 3 colunas, então
# subir ou descer uma linha é andar 3 casas na lista.
PASSOS = {"cima": -3, "baixo": 3, "esquerda": -1, "direita": 1}


def mover_cursor(cursor, direcao):
    """Devolve a nova posição do cursor (de 0 a 8) depois de andar.

    Nas bordas o cursor fica parado: não sai do tabuleiro nem passa do fim
    de uma linha para o começo da próxima.
    """

    linha, coluna = divmod(cursor, 3)

    if direcao == "cima" and linha == 0:
        return cursor
    if direcao == "baixo" and linha == 2:
        return cursor
    if direcao == "esquerda" and coluna == 0:
        return cursor
    if direcao == "direita" and coluna == 2:
        return cursor
    return cursor + PASSOS[direcao]


def desenhar_tabuleiro(tab, cursor=None):
    """Devolve o tabuleiro como texto, com o número das casas livres.

    As casas são numeradas de 1 a 9 para o jogador, embora os índices da
    lista vão de 0 a 8. A casa do cursor, se houver, fica entre colchetes.
    """

    celulas = []
    for casa, valor in enumerate(tab):
        conteudo = str(casa + 1) if valor == VAZIO else valor
        if casa == cursor:
            celulas.append(f"[{conteudo}]")
        else:
            celulas.append(f" {conteudo} ")

    linhas = []
    for inicio in (0, 3, 6):
        linhas.append("|".join(celulas[inicio:inicio + 3]))
    return "\n---+---+---\n".join(linhas)


def desenhar_menu(titulo, opcoes, selecionada):
    """Devolve um menu como texto, com uma seta na opção selecionada.

    As opções são numeradas a partir de 1, para também poderem ser
    escolhidas pelo número.
    """

    linhas = [titulo, "─" * len(titulo), ""]
    for numero, opcao in enumerate(opcoes, start=1):
        marca = "▶" if numero - 1 == selecionada else " "
        linhas.append(f" {marca} {numero}. {opcao}")
    return "\n".join(linhas)


def desenhar_placar(placar):
    """Devolve o placar da sessão numa linha, como 'Você 2 · Empates 1'."""

    return "  ·  ".join(f"{nome} {pontos}" for nome, pontos in placar.items())