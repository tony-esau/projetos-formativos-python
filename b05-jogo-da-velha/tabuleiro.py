VAZIO = " "

# As 8 linhas que dão vitória, pelos índices do tabuleiro:
#  0 | 1 | 2
#  3 | 4 | 5
#  6 | 7 | 8
LINHAS = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # Horizontais.
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # Verticais.
    (0, 4, 8), (2, 4, 6),              # Diagonais.
)


def criar():
    """Devolve um tabuleiro vazio: uma lista com 9 casas vazias."""

    return [VAZIO] * 9


def jogadas_validas(tab):
    """Devolve os índices das casas vazias, em ordem crescente."""

    return [casa for casa, valor in enumerate(tab) if valor == VAZIO]


def jogar(tab, casa, simbolo):
    """Devolve um tabuleiro novo com o símbolo colocado na casa.

    O tabuleiro original não muda, para que a IA possa simular jogadas à
    vontade. Levanta ValueError se a casa não existe ou já está ocupada.
    """

    if casa not in range(9):
        raise ValueError(f"a casa {casa} não existe")
    if tab[casa] != VAZIO:
        raise ValueError(f"a casa {casa + 1} já está ocupada")

    novo = tab.copy()
    novo[casa] = simbolo
    return novo


def vencedor(tab):
    """Devolve "X", "O", "empate" ou None se o jogo ainda não acabou.

    O vencedor é conferido primeiro: um tabuleiro cheio pode ter um
    vencedor na última jogada, e isso não é empate.
    """

    for a, b, c in LINHAS:
        if tab[a] != VAZIO and tab[a] == tab[b] == tab[c]:
            return tab[a]

    if VAZIO not in tab:
        return "empate"
    return None


def outro(simbolo):
    """Devolve o símbolo do outro jogador: "X" -> "O" e "O" -> "X"."""

    return "O" if simbolo == "X" else "X"