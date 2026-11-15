"""As jogadas do computador, uma para cada dificuldade.

fácil:      escolhe uma casa livre ao acaso.
médio:      vence se puder, bloqueia se o adversário for vencer, senão joga
            ao acaso.
difícil:    joga a melhor jogada do minimax na maioria das vezes, mas às
            vezes erra de propósito.
impossível: sempre a melhor jogada do minimax (com poda alfa-beta). Nunca
            perde.
"""

import functools
import math
import random

from tabuleiro import jogadas_validas, jogar, outro, vencedor

DIFICULDADES = ["fácil", "médio", "difícil", "impossível"]

# No difícil, a chance de o computador jogar ao acaso em vez da melhor
# jogada. Com 25%, ele ainda joga bem, mas dá para vencer com atenção.
CHANCE_DE_ERRO_DIFICIL = 0.25


def contar_chamadas(funcao):
    """Decorador que conta quantas vezes a função foi chamada.

    A contagem fica em funcao.chamadas. Como o minimax chama a si mesmo
    pelo nome, as chamadas recursivas também passam pelo decorador, e a
    contagem é o número de tabuleiros visitados.
    """

    @functools.wraps(funcao)
    def contadora(*args, **kwargs):
        contadora.chamadas += 1
        return funcao(*args, **kwargs)

    contadora.chamadas = 0
    return contadora


def jogada_aleatoria(tab):
    """Devolve uma casa livre qualquer."""

    return random.choice(jogadas_validas(tab))


def jogada_que_vence(tab, simbolo):
    """Devolve uma casa que faz o simbolo vencer agora, ou None."""

    for casa in jogadas_validas(tab):
        if vencedor(jogar(tab, casa, simbolo)) == simbolo:
            return casa
    return None


def jogada_media(tab, computador):
    """Vence se puder, senão bloqueia o adversário, senão joga ao acaso."""

    casa = jogada_que_vence(tab, computador)
    if casa is None:
        casa = jogada_que_vence(tab, outro(computador))
    if casa is None:
        casa = jogada_aleatoria(tab)
    return casa


def pontuacao_final(tab, computador, profundidade):
    """Dá uma nota a um tabuleiro em que o jogo acabou.

    Vitória do computador vale 10 menos a profundidade, para ele preferir
    vencer mais cedo. Derrota vale a profundidade menos 10, para ele
    preferir perder mais tarde. Empate vale 0.
    """

    resultado = vencedor(tab)
    if resultado == computador:
        return 10 - profundidade
    if resultado == "empate":
        return 0
    return profundidade - 10


@contar_chamadas
def minimax(tab, vez, computador, profundidade=0):
    """Devolve a nota do tabuleiro supondo que os dois jogam perfeitamente.

    vez é quem joga agora. Na vez do computador, ele escolhe a jogada de
    maior nota; na vez do adversário, supõe que ele escolhe a de menor
    nota, a pior para o computador.
    """

    if vencedor(tab) is not None:
        return pontuacao_final(tab, computador, profundidade)

    notas = []
    for casa in jogadas_validas(tab):
        novo = jogar(tab, casa, vez)
        notas.append(minimax(novo, outro(vez), computador, profundidade + 1))

    if vez == computador:
        return max(notas)
    return min(notas)


@contar_chamadas
def minimax_alfa_beta(tab, vez, computador, profundidade=0,
                      alfa=-math.inf, beta=math.inf):
    """Mesmo resultado do minimax, visitando bem menos tabuleiros.

    alfa é a melhor nota que o computador já tem garantida em algum ramo
    acima; beta é a melhor (menor) que o adversário já tem garantida.
    Quando alfa >= beta, o ramo atual nunca seria escolhido por um dos
    dois, e as jogadas que faltam nele não precisam ser testadas.
    """

    if vencedor(tab) is not None:
        return pontuacao_final(tab, computador, profundidade)

    if vez == computador:
        melhor = -math.inf
        for casa in jogadas_validas(tab):
            novo = jogar(tab, casa, vez)
            nota = minimax_alfa_beta(novo, outro(vez), computador,
                                     profundidade + 1, alfa, beta)
            melhor = max(melhor, nota)
            alfa = max(alfa, melhor)
            if alfa >= beta:
                break  # o adversário nunca deixaria o jogo chegar aqui
        return melhor

    pior = math.inf
    for casa in jogadas_validas(tab):
        novo = jogar(tab, casa, vez)
        nota = minimax_alfa_beta(novo, outro(vez), computador,
                                 profundidade + 1, alfa, beta)
        pior = min(pior, nota)
        beta = min(beta, pior)
        if alfa >= beta:
            break  # o computador nunca deixaria o jogo chegar aqui
    return pior


@contar_chamadas
def minimax_memo(tab, vez, computador, profundidade=0, memoria=None):
    """Mesmo resultado do minimax, guardando as notas já calculadas.

    O mesmo tabuleiro aparece por vários caminhos: X no 1 e depois no 2
    dá o mesmo tabuleiro que X no 2 e depois no 1. A memória é um
    dicionário que guarda a nota de cada tabuleiro já resolvido, para não
    explorar a mesma subárvore de novo.
    """

    if memoria is None:
        memoria = {}

    # A lista vira tupla porque chaves de dicionário não podem mudar.
    chave = (tuple(tab), vez)
    if chave in memoria:
        return memoria[chave]

    if vencedor(tab) is not None:
        nota = pontuacao_final(tab, computador, profundidade)
    else:
        notas = []
        for casa in jogadas_validas(tab):
            novo = jogar(tab, casa, vez)
            notas.append(minimax_memo(novo, outro(vez), computador,
                                      profundidade + 1, memoria))
        nota = max(notas) if vez == computador else min(notas)

    memoria[chave] = nota
    return nota


def melhor_jogada(tab, computador):
    """Testa todas as jogadas e devolve a de maior nota no minimax.

    Se várias jogadas empatam com a maior nota, escolhe uma delas ao
    acaso, para o computador não jogar sempre igual.
    """

    notas = {}
    for casa in jogadas_validas(tab):
        novo = jogar(tab, casa, computador)
        notas[casa] = minimax_alfa_beta(novo, outro(computador),
                                        computador, profundidade=1)

    maior = max(notas.values())
    melhores = [casa for casa, nota in notas.items() if nota == maior]
    return random.choice(melhores)


def escolher_jogada(tab, computador, dificuldade):
    """Devolve a casa em que o computador joga, conforme a dificuldade."""

    if dificuldade == "fácil":
        return jogada_aleatoria(tab)
    if dificuldade == "médio":
        return jogada_media(tab, computador)
    if dificuldade == "difícil":
        if random.random() < CHANCE_DE_ERRO_DIFICIL:
            return jogada_aleatoria(tab)
        return melhor_jogada(tab, computador)
    return melhor_jogada(tab, computador)