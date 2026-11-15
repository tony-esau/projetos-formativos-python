import pytest

from tabuleiro import (LINHAS, VAZIO, criar, jogadas_validas, jogar, outro,
                       vencedor)


def montar(texto):
    """Monta um tabuleiro a partir de um texto de 9 caracteres.

    O '.' é uma casa vazia. Exemplo: "XXX.OO..." é X na primeira linha.
    """

    return [VAZIO if letra == "." else letra for letra in texto]


def test_criar():
    assert criar() == [" "] * 9


def test_criar_devolve_listas_independentes():
    a = criar()
    b = criar()
    a[0] = "X"
    assert b[0] == " "


def test_jogadas_validas_tabuleiro_vazio():
    assert jogadas_validas(criar()) == list(range(9))


def test_jogadas_validas_com_casas_ocupadas():
    assert jogadas_validas(montar("X.O.X...O")) == [1, 3, 5, 6, 7]


def test_jogadas_validas_tabuleiro_cheio():
    assert jogadas_validas(montar("XOXXOOOXX")) == []


def test_jogar_coloca_o_simbolo():
    assert jogar(criar(), 4, "X") == montar("....X....")


def test_jogar_nao_altera_o_original():
    original = criar()
    jogar(original, 4, "X")
    assert original == criar()


@pytest.mark.parametrize("casa", [-1, 9, 10])
def test_jogar_casa_inexistente(casa):
    with pytest.raises(ValueError):
        jogar(criar(), casa, "X")


def test_jogar_casa_ocupada():
    with pytest.raises(ValueError, match="ocupada"):
        jogar(montar("....X...."), 4, "O")


@pytest.mark.parametrize("linha", LINHAS)
@pytest.mark.parametrize("simbolo", ["X", "O"])
def test_vencedor_detecta_as_8_linhas(linha, simbolo):
    # Critério de aceite: as 8 linhas, para os dois símbolos.
    tab = criar()
    for casa in linha:
        tab[casa] = simbolo
    assert vencedor(tab) == simbolo


def test_existem_8_linhas_diferentes():
    assert len(set(LINHAS)) == 8


@pytest.mark.parametrize("texto", [
    ".........",
    "X........",
    "XO.......",
    "XX.OO....",
    "XOXOXO...",
])
def test_jogo_em_andamento(texto):
    assert vencedor(montar(texto)) is None


def test_empate():
    assert vencedor(montar("XOXXOOOXX")) == "empate"


def test_vitoria_na_ultima_jogada_nao_e_empate():
    # Tabuleiro cheio, mas o X fechou a coluna da esquerda na última jogada.
    assert vencedor(montar("XOXXOOXXO")) == "X"


def test_outro():
    assert outro("X") == "O"
    assert outro("O") == "X"