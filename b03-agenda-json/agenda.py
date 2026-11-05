from armazenamento import carregar, salvar
from formatacao import normalizar_telefone
from validacao import validar_email, validar_telefone, validar_aniversario


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


def perguntar(rotulo, validar=None, obrigatorio=True, erro="Valor inválido."):
    """Pergunta um campo e repete enquanto a resposta for inválida.

    validar é uma função que recebe o texto e devolve True ou False.
    Se o campo não for obrigatório, Enter vazio devolve "".
    """

    while True:
        resposta = input(f"{rotulo}: ").strip()

        if resposta == "":
            if obrigatorio:
                print("Este campo é obrigatório.")
                continue
            return ""

        if validar is None or validar(resposta):
            return resposta

        print(erro)


def proximo_id(contatos):
    """Devolve o id do próximo contato: o maior id da lista mais 1."""

    if not contatos:
        return 1
    return max(contato["id"] for contato in contatos) + 1


def adicionar(contatos):
    """Pergunta os dados de um contato novo, adiciona na lista e salva."""

    print("\nNovo contato (campos com * são obrigatórios)")
    nome = perguntar("Nome*")
    telefone = perguntar("Telefone*", validar_telefone,
                         erro="Telefone inválido. Ex.: (88) 99999-1234 ou +1 415 555 2671")
    email = perguntar("E-mail", validar_email, obrigatorio=False,
                      erro="E-mail inválido. Ex.: ana.souza@gmail.com")
    aniversario = perguntar("Aniversário (DD/MM)", validar_aniversario, obrigatorio=False,
                            erro="Data inválida. Use DD/MM, como 15/03.")

    contato = {
        "id": proximo_id(contatos),
        "nome": nome,
        "telefone": normalizar_telefone(telefone),
        "email": email,
        "aniversario": aniversario,
    }
    contatos.append(contato)
    salvar(contatos)
    print(f"Contato {nome} adicionado.")


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