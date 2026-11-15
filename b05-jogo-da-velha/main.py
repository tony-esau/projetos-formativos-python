import time

from ia import DIFICULDADES, escolher_jogada
from tabuleiro import criar, jogar, outro, vencedor
from teclado import ler_tecla
from tela import (desenhar_menu, desenhar_placar, desenhar_tabuleiro,
                  limpar_tela, mover_cursor)

AJUDA = ("Setas ou WASD para mover, Enter para jogar, "
         "1 a 9 para jogar direto, Q para sair.")

# Tempo que o computador "pensa", só para a jogada dele não aparecer de
# repente.
PAUSA_DO_COMPUTADOR = 0.6


def escolher_opcao(titulo, opcoes):
    """Mostra um menu e devolve o índice da opção escolhida, ou None.

    Escolhe com as setas e o Enter, ou direto pelo número. Q ou Esc
    devolvem None.
    """

    selecionada = 0
    while True:
        limpar_tela()
        print(desenhar_menu(titulo, opcoes, selecionada))
        print("\nSetas ou W/S para escolher, Enter para confirmar.")

        acao = ler_tecla()
        if acao == "sair":
            return None
        if acao == "enter":
            return selecionada
        if acao == "cima":
            selecionada = max(0, selecionada - 1)
        elif acao == "baixo":
            selecionada = min(len(opcoes) - 1, selecionada + 1)
        elif isinstance(acao, int) and acao <= len(opcoes):
            return acao - 1


def ler_jogada(tab, simbolo, cursor, cabecalho):
    """Deixa o jogador escolher a casa com o cursor ou com os números.

    Devolve (tabuleiro novo, posição do cursor), ou (None, cursor) se o
    jogador desistir da partida. Casas ocupadas mostram um aviso e a
    escolha continua.
    """

    aviso = ""
    while True:
        limpar_tela()
        print(cabecalho)
        print(desenhar_tabuleiro(tab, cursor))
        print(f"\nSua vez ({simbolo}).")
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


def vez_do_computador(tab, simbolo, dificuldade, cabecalho):
    """Mostra o computador pensando e devolve o tabuleiro com a jogada."""

    limpar_tela()
    print(cabecalho)
    print(desenhar_tabuleiro(tab))
    print(f"\nO computador ({simbolo}) está pensando...")
    time.sleep(PAUSA_DO_COMPUTADOR)

    casa = escolher_jogada(tab, simbolo, dificuldade)
    return jogar(tab, casa, simbolo)


def partida(jogadores, cabecalho):
    """Joga uma partida e devolve "X", "O", "empate" ou None se abandonada.

    jogadores diz quem controla cada símbolo: "humano" ou uma das
    dificuldades do computador, como {"X": "humano", "O": "difícil"}.
    O X sempre começa.
    """

    tab = criar()
    vez = "X"
    cursor = 4  # começa no centro

    while vencedor(tab) is None:
        if jogadores[vez] == "humano":
            tab, cursor = ler_jogada(tab, vez, cursor, cabecalho)
            if tab is None:
                return None
        else:
            tab = vez_do_computador(tab, vez, jogadores[vez], cabecalho)
        vez = outro(vez)

    limpar_tela()
    print(cabecalho)
    print(desenhar_tabuleiro(tab))
    return vencedor(tab)


def configurar():
    """Pergunta o modo, o símbolo e a dificuldade.

    Devolve (jogadores, nomes) ou None se o usuário sair. nomes diz como
    chamar cada símbolo no placar, como {"X": "Você", "O": "Computador"}.
    """

    modo = escolher_opcao("JOGO DA VELHA",
                          ["Contra o computador", "Duas pessoas"])
    if modo is None:
        return None
    if modo == 1:
        return ({"X": "humano", "O": "humano"},
                {"X": "Jogador X", "O": "Jogador O"})

    escolha = escolher_opcao("Com qual símbolo você quer jogar?",
                             ["X (você começa)", "O (o computador começa)"])
    if escolha is None:
        return None
    humano = "X" if escolha == 0 else "O"

    nivel = escolher_opcao("Dificuldade",
                           [d.capitalize() for d in DIFICULDADES])
    if nivel is None:
        return None

    computador = outro(humano)
    jogadores = {humano: "humano", computador: DIFICULDADES[nivel]}
    nomes = {humano: "Você", computador: "Computador"}
    return jogadores, nomes


def anunciar(resultado, nomes):
    """Mostra o resultado da partida."""

    if resultado == "empate":
        print("\nDeu velha! Empate.")
    elif nomes[resultado] == "Você":
        print("\nVocê venceu!")
    elif nomes[resultado] == "Computador":
        print("\nO computador venceu.")
    else:
        print(f"\n{nomes[resultado]} venceu!")


def main():
    """Configura o jogo e repete partidas, mantendo o placar da sessão."""

    configuracao = configurar()
    if configuracao is None:
        return
    jogadores, nomes = configuracao

    # No placar, "Você" vem primeiro; entre duas pessoas, X e depois O.
    ordem = sorted(nomes.values(), key=lambda nome: nome != "Você")
    placar = {ordem[0]: 0, ordem[1]: 0, "Empates": 0}

    titulo = "Jogo da velha"
    for controle in jogadores.values():
        if controle != "humano":
            titulo += f" · {controle.capitalize()}"

    while True:
        cabecalho = f"{titulo}\n{desenhar_placar(placar)}\n"
        resultado = partida(jogadores, cabecalho)

        if resultado is None:
            print("\nPartida abandonada.")
        else:
            if resultado == "empate":
                placar["Empates"] += 1
            else:
                placar[nomes[resultado]] += 1
            anunciar(resultado, nomes)
            print(desenhar_placar(placar))

        resposta = input("\nOutra partida? (s/n): ").strip().lower()
        if resposta != "s":
            print("Até mais!")
            break


if __name__ == "__main__":
    main()