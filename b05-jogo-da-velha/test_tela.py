import pytest

from tabuleiro import criar, jogar
from tela import desenhar_tabuleiro, mover_cursor


def test_tabuleiro_vazio_mostra_os_numeros():
    assert desenhar_tabuleiro(criar()) == (
        " 1 | 2 | 3 \n"
        "---+---+---\n"
        " 4 | 5 | 6 \n"
        "---+---+---\n"
        " 7 | 8 | 9 "
    )


def test_casas_ocupadas_mostram_o_simbolo():
    tab = jogar(jogar(criar(), 0, "X"), 4, "O")
    linhas = desenhar_tabuleiro(tab).split("\n")
    assert linhas[0] == " X | 2 | 3 "
    assert linhas[2] == " 4 | O | 6 "


def test_cursor_fica_entre_colchetes():
    linhas = desenhar_tabuleiro(criar(), cursor=4).split("\n")
    assert linhas[2] == " 4 |[5]| 6 "


def test_cursor_em_casa_ocupada():
    tab = jogar(criar(), 0, "X")
    assert desenhar_tabuleiro(tab, cursor=0).startswith("[X]| 2 | 3 ")



@pytest.mark.parametrize("cursor, direcao, esperado", [
    (4, "cima", 1), (4, "baixo", 7), (4, "esquerda", 3), (4, "direita", 5),
    (0, "cima", 0), (0, "esquerda", 0),
    (8, "baixo", 8), (8, "direita", 8),
    (2, "direita", 2),   # não passa da linha de cima para a do meio
    (3, "esquerda", 3),  # não volta para o fim da linha de cima
    (6, "cima", 3),
])
def test_mover_cursor(cursor, direcao, esperado):
    assert mover_cursor(cursor, direcao) == esperado