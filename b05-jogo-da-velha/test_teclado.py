import pytest

from teclado import traduzir


@pytest.mark.parametrize("bruto, acao", [
    # setas no Windows (dois prefixos possíveis)
    ("\xe0H", "cima"), ("\xe0P", "baixo"), ("\xe0K", "esquerda"),
    ("\xe0M", "direita"), ("\x00H", "cima"),
    # setas no Linux e no Mac
    ("\x1b[A", "cima"), ("\x1b[B", "baixo"), ("\x1b[D", "esquerda"),
    ("\x1b[C", "direita"),
    # WASD, maiúsculo ou minúsculo
    ("w", "cima"), ("S", "baixo"), ("a", "esquerda"), ("D", "direita"),
    # confirmar e sair
    ("\r", "enter"), ("\n", "enter"), (" ", "enter"),
    ("\x1b", "sair"), ("q", "sair"),
    # números
    ("1", 1), ("9", 9),
])
def test_traduzir(bruto, acao):
    assert traduzir(bruto) == acao


@pytest.mark.parametrize("bruto", ["0", "x", "\t", "\xe0G", "\x1b[Z"])
def test_teclas_ignoradas(bruto):
    assert traduzir(bruto) is None