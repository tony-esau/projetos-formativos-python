import random

import pytest

from ia import (DIFICULDADES, escolher_jogada, jogada_media, melhor_jogada,
                minimax, minimax_alfa_beta)
from tabuleiro import (VAZIO, criar, jogadas_validas, jogar, outro,
                       vencedor)


def montar(texto):
    """Monta um tabuleiro a partir de um texto de 9 caracteres, '.' vazio."""

    return [VAZIO if letra == "." else letra for letra in texto]


@pytest.mark.parametrize("texto, computador, casa", [
    ("OO.XX....", "O", 2),   # fecha a linha de cima
    ("XX.OO....", "O", 5),   # vence em vez de bloquear o X
    ("O..XO.X..", "O", 8),   # diagonal
    ("X.O.XO...", "O", 8),   # coluna da direita
    (".X.OX.O.X", "O", 0),   # coluna da esquerda
])
def test_vence_em_uma_jogada(texto, computador, casa):
    # Critério de aceite: se pode vencer em uma jogada, vence nessa jogada.
    assert melhor_jogada(montar(texto), computador) == casa


@pytest.mark.parametrize("texto, computador, casa", [
    ("XX..O....", "O", 2),
    ("X...X....", "O", 8),
    ("..X.X....", "O", 6),
])
def test_bloqueia_a_vitoria_do_adversario(texto, computador, casa):
    assert melhor_jogada(montar(texto), computador) == casa


@pytest.mark.parametrize("texto, computador, casa", [
    ("OO.XX....", "O", 2),   # vence
    ("XX..O....", "O", 2),   # bloqueia
])
def test_medio_vence_ou_bloqueia(texto, computador, casa):
    assert jogada_media(montar(texto), computador) == casa


@pytest.mark.parametrize("texto, vez", [
    ("X........", "O"),
    ("X...O....", "X"),
    ("XO..X....", "O"),
    ("X.O.X.O..", "X"),
    ("OX.XO....", "X"),
])
@pytest.mark.parametrize("computador", ["X", "O"])
def test_alfa_beta_da_a_mesma_nota_que_o_minimax(texto, vez, computador):
    tab = montar(texto)
    assert (minimax_alfa_beta(tab, vez, computador)
            == minimax(tab, vez, computador))


def todas_as_partidas(tab, vez, computador):
    """Joga contra o impossível testando toda resposta do adversário.

    Devolve a lista com o resultado de cada partida possível.
    """

    resultado = vencedor(tab)
    if resultado is not None:
        return [resultado]

    if vez == computador:
        casa = melhor_jogada(tab, computador)
        return todas_as_partidas(jogar(tab, casa, vez), outro(vez),
                                 computador)

    resultados = []
    for casa in jogadas_validas(tab):
        resultados += todas_as_partidas(jogar(tab, casa, vez), outro(vez),
                                        computador)
    return resultados


@pytest.mark.parametrize("computador", ["X", "O"])
def test_impossivel_nunca_perde(computador):
    # Critério de aceite: o computador nunca perde. Aqui não são só 10
    # partidas: são todas as sequências de jogadas do adversário.
    random.seed(0)
    resultados = todas_as_partidas(criar(), "X", computador)
    assert outro(computador) not in resultados
    assert len(resultados) > 50


@pytest.mark.parametrize("dificuldade", DIFICULDADES)
def test_toda_dificuldade_joga_numa_casa_livre(dificuldade):
    random.seed(1)
    tab = montar("XO.X.O...")
    for _ in range(20):
        assert escolher_jogada(tab, "O", dificuldade) in jogadas_validas(tab)


@pytest.mark.parametrize("texto, vez", [
    ("X........", "O"), ("X...O....", "X"), ("XO..X....", "O"),
])
def test_memoizacao_da_a_mesma_nota_que_o_minimax(texto, vez):
    from ia import minimax_memo

    tab = montar(texto)
    assert minimax_memo(tab, vez, "O") == minimax(tab, vez, "O")


def test_contagem_de_tabuleiros_visitados():
    # Num tabuleiro com uma casa livre, o minimax visita 2 tabuleiros: o
    # atual e o que fica depois da última jogada.
    minimax.chamadas = 0
    minimax(montar("XOXXOOOX."), "X", "X")
    assert minimax.chamadas == 2


def test_poda_visita_menos_tabuleiros():
    tab = montar("X........")
    minimax.chamadas = 0
    minimax(tab, "O", "X")
    minimax_alfa_beta.chamadas = 0
    minimax_alfa_beta(tab, "O", "X")
    assert minimax_alfa_beta.chamadas < minimax.chamadas