from tabuleiro import criar, jogar, outro, vencedor
from teclado import ler_tecla
from tela import desenhar_tabuleiro, limpar_tela, mover_cursor


AJUDA = ("Setas ou WASD para mover, Enter para jogar, "
         "1 a 9 para jogar direto, Q para sair.")


def ler_jogada(tab, simbolo, cursor):
    """Deixa o jogador escolher a casa com o cursor ou com os números.

    Devolve (tabuleiro novo, posição do cursor), ou (None, cursor) se o
    jogador desistir da partida. Casas ocupadas mostram um aviso e a
    escolha continua.
    """

    aviso = ""
    while True:
        limpar_tela()
        print(desenhar_tabuleiro(tab, cursor))
        print(f"\nVez do {simbolo}.")
        print(AJUDA)
        if aviso:
            print(f"\n  {aviso}")

        acao = ler_tecla()
        aviso = ""

        if acao == "sair":
            return None, cursor
        if acao in ("cima", "baixo", "esquerda", "direita"):
            cursor = mover_cursor(cursor, acao)
            continue

        # Enter joga na casa do cursor; um número joga direto naquela casa.
        if isinstance(acao, int):
            cursor = acao - 1
        try:
            return jogar(tab, cursor, simbolo), cursor
        except ValueError:
            aviso = f"A casa {cursor + 1} já está ocupada."


def mostrar_resultado(resultado):
    """Mostra quem venceu ou se deu empate."""

    if resultado == "empate":
        print("\nDeu velha! Empate.")
    else:
        print(f"\n{resultado} venceu!")


def partida_dois_jogadores():
    """Joga uma partida entre duas pessoas e devolve o resultado.

    O resultado é "X", "O", "empate" ou None se a partida foi abandonada.
    """

    tab = criar()
    simbolo = "X"
    cursor = 4  # começa no centro

    while vencedor(tab) is None:
        tab, cursor = ler_jogada(tab, simbolo, cursor)
        if tab is None:
            print("\nPartida abandonada.")
            return None
        simbolo = outro(simbolo)

    resultado = vencedor(tab)
    limpar_tela()
    print(desenhar_tabuleiro(tab))
    mostrar_resultado(resultado)
    return resultado


def main():
    """Joga partidas até os jogadores não quererem mais."""

    while True:
        partida_dois_jogadores()

        resposta = input("\nOutra partida? (s/n): ").strip().lower()
        if resposta != "s":
            print("Até mais!")
            break


if __name__ == "__main__":
    main()