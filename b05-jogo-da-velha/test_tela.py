from tabuleiro import criar, jogar
from tela import desenhar_tabuleiro


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