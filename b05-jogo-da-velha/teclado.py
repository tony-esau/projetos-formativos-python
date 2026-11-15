"""Leitura de uma tecla por vez, sem esperar o Enter, no Windows e no Linux.

O input() só devolve o texto depois do Enter. Para mover o cursor com as
setas, o programa precisa saber de cada tecla no momento em que ela é
apertada, e isso é feito de um jeito diferente em cada sistema.
"""

import os
import sys

# Como cada sistema manda as setas: no Windows, um prefixo e uma letra;
# no Linux e no Mac, a sequência de escape \x1b[ seguida de uma letra.
SETAS = {
    "\xe0H": "cima", "\xe0P": "baixo", "\xe0K": "esquerda", "\xe0M": "direita",
    "\x00H": "cima", "\x00P": "baixo", "\x00K": "esquerda", "\x00M": "direita",
    "\x1b[A": "cima", "\x1b[B": "baixo", "\x1b[D": "esquerda",
    "\x1b[C": "direita",
}

WASD = {"w": "cima", "s": "baixo", "a": "esquerda", "d": "direita"}


def traduzir(bruto):
    """Transforma o que o teclado mandou numa ação do jogo.

    Devolve "cima", "baixo", "esquerda", "direita", "enter", "sair", um
    número de 1 a 9 (como int) ou None para teclas que o jogo ignora.
    """

    if bruto in SETAS:
        return SETAS[bruto]
    if bruto in ("\r", "\n", " "):
        return "enter"
    if bruto in ("\x1b", "q", "Q"):
        return "sair"
    if bruto.lower() in WASD:
        return WASD[bruto.lower()]
    if len(bruto) == 1 and bruto in "123456789":
        return int(bruto)
    return None


def _ler_bruto_windows():
    """Lê uma tecla no Windows, juntando o prefixo das teclas especiais."""

    import msvcrt

    tecla = msvcrt.getwch()
    # Setas e outras teclas especiais chegam em duas partes.
    if tecla in ("\x00", "\xe0"):
        tecla += msvcrt.getwch()
    return tecla


def _ler_bruto_unix():
    """Lê uma tecla no Linux e no Mac, juntando as sequências de escape."""

    import select
    import termios
    import tty

    entrada = sys.stdin.fileno()
    configuracao_antiga = termios.tcgetattr(entrada)
    try:
        # cbreak entrega cada tecla na hora, mas mantém o Ctrl+C.
        tty.setcbreak(entrada)

        # os.read lê direto do terminal, sem o buffer do sys.stdin. Com o
        # sys.stdin.read, o resto de uma seta ficaria guardado no buffer, e
        # o select abaixo não enxergaria que ainda há caracteres esperando.
        tecla = os.read(entrada, 1)

        # Um \x1b sozinho é o Esc; seguido de mais caracteres, é uma seta.
        # O select espera um pouquinho para ver se vem mais alguma coisa.
        if tecla == b"\x1b":
            pronto, _, _ = select.select([entrada], [], [], 0.05)
            if pronto:
                tecla += os.read(entrada, 2)
        return tecla.decode(errors="ignore")
    finally:
        # Devolve o terminal ao normal, mesmo se der erro no meio.
        termios.tcsetattr(entrada, termios.TCSADRAIN, configuracao_antiga)


def ler_tecla():
    """Espera uma tecla e devolve a ação correspondente (veja traduzir).

    Teclas que o jogo não usa são ignoradas, e a espera continua.
    """

    ler_bruto = _ler_bruto_windows if os.name == "nt" else _ler_bruto_unix

    while True:
        acao = traduzir(ler_bruto())
        if acao is not None:
            return acao