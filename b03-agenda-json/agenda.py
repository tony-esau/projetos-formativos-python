"""Agenda de contatos no terminal, com os dados salvos em JSON."""

from armazenamento import carregar, salvar


def mostrar_menu():
    """Mostra as opções do menu principal."""

    print()
    print("=== Agenda de contatos ===")
    print("1. Adicionar contato")
    print("2. Listar contatos")
    print("3. Buscar")
    print("4. Editar")
    print("5. Remover")
    print("6. Aniversariantes do mês")
    print("7. Exportar CSV")
    print("0. Sair")


def adicionar(contatos):
    """Pergunta os dados de um contato novo, adiciona na lista e salva."""

    print("Em construção.")


def listar(contatos):
    """Mostra todos os contatos em ordem alfabética."""

    print("Em construção.")


def buscar(contatos):
    """Procura contatos pelo nome, ignorando acentos e maiúsculas."""

    print("Em construção.")


def editar(contatos):
    """Altera os campos de um contato escolhido pelo id e salva."""

    print("Em construção.")


def remover(contatos):
    """Apaga um contato escolhido pelo id, depois de confirmar, e salva."""

    print("Em construção.")


def aniversariantes(contatos):
    """Mostra quem faz aniversário no mês atual, em ordem de dia."""

    print("Em construção.")


def exportar_csv(contatos):
    """Gera um arquivo .csv com todos os contatos."""

    print("Em construção.")


def main():
    """Carrega os contatos e repete o menu até o usuário escolher sair."""

    contatos = carregar()

    while True:
        mostrar_menu()
        opcao = input("Escolha: ").strip()

        if opcao == "1":
            adicionar(contatos)
        elif opcao == "2":
            listar(contatos)
        elif opcao == "3":
            buscar(contatos)
        elif opcao == "4":
            editar(contatos)
        elif opcao == "5":
            remover(contatos)
        elif opcao == "6":
            aniversariantes(contatos)
        elif opcao == "7":
            exportar_csv(contatos)
        elif opcao == "0":
            print("Até mais!")
            break
        else:
            print("Opção inválida, digite um número de 0 a 7.")


if __name__ == "__main__":
    main()