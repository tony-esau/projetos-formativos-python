from datetime import datetime

from armazenamento import CAMINHO_PADRAO, carregar, gravar_csv, salvar
from formatacao import normalizar_telefone, formatar_telefone, remover_acentos
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


def chave_nome(contato):
    """Chave de ordenação: o nome sem acentos e em minúsculas.

    Assim 'Álvaro' fica junto dos nomes com A, e não no fim da lista.
    """

    return remover_acentos(contato["nome"]).lower()


def mostrar_contatos(lista):
    """Mostra uma lista de contatos em colunas alinhadas."""

    # A coluna do nome fica com a largura do maior nome (no mínimo 4, de "Nome").
    largura_nome = max(4, max(len(contato["nome"]) for contato in lista))

    print(f"{'Id':>3}  {'Nome':<{largura_nome}}  {'Telefone':<20}  {'Aniv.':<5}  E-mail")
    for contato in lista:
        telefone = formatar_telefone(contato["telefone"])
        aniversario = contato["aniversario"] or "-"
        email = contato["email"] or "-"
        print(f"{contato['id']:>3}  {contato['nome']:<{largura_nome}}  "
              f"{telefone:<20}  {aniversario:<5}  {email}")


def listar(contatos):
    """Mostra todos os contatos em ordem alfabética."""

    if not contatos:
        print("A agenda está vazia.")
        return

    print()
    mostrar_contatos(sorted(contatos, key=chave_nome))
    print(f"\n{len(contatos)} contato(s).")


def filtrar_por_nome(contatos, termo):
    """Devolve os contatos cujo nome contém o termo, ignorando acentos e maiúsculas."""

    termo = remover_acentos(termo).lower()

    encontrados = []
    for contato in contatos:
        if termo in chave_nome(contato):
            encontrados.append(contato)
    return encontrados


def buscar(contatos):
    """Procura contatos pelo nome, ignorando acentos e maiúsculas.

    Basta um pedaço do nome: 'silva' encontra 'José da Silva'.
    """

    termo = perguntar("Buscar por nome")
    encontrados = filtrar_por_nome(contatos, termo)

    if not encontrados:
        print("Nenhum contato encontrado.")
        return

    print()
    mostrar_contatos(sorted(encontrados, key=chave_nome))
    print(f"\n{len(encontrados)} contato(s) encontrado(s).")


def procurar_por_id(contatos, texto):
    """Devolve o contato com o id digitado, ou None se não existir."""

    for contato in contatos:
        if contato["id"] == int(texto):
            return contato
    return None


def escolher_contato(contatos):
    """Pede um nome ou um id e devolve o contato escolhido, ou None se o usuário desistir.

    Número: procura pelo id.
    Texto: busca pelo nome. Se achar um só, já escolhe; se achar vários,
    mostra a tabela e pede o id de um dos que apareceram.
    Enter vazio cancela.
    """

    while True:
        resposta = input("Nome ou id do contato (Enter para cancelar): ").strip()
        if resposta == "":
            return None

        # Só número: é um id.
        if resposta.isdigit():
            contato = procurar_por_id(contatos, resposta)
            if contato is None:
                print(f"Não existe contato com id {resposta}.")
                continue
            return contato

        # Texto: é um pedaço do nome.
        encontrados = filtrar_por_nome(contatos, resposta)

        if not encontrados:
            print("Nenhum contato encontrado com esse nome.")
            continue

        if len(encontrados) == 1:
            print(f"Contato encontrado: {encontrados[0]['nome']}")
            return encontrados[0]

        # Vários: mostra só os encontrados e pede o id de um deles.
        print(f"\n{len(encontrados)} contatos encontrados:")
        mostrar_contatos(sorted(encontrados, key=chave_nome))
        print()
        return escolher_entre(encontrados)


def escolher_entre(encontrados):
    """Pede o id de um dos contatos mostrados e devolve ele, ou None se o usuário desistir.

    Só aceita ids que estão na lista de encontrados.
    """

    while True:
        resposta = input("Id de qual deles (Enter para cancelar): ").strip()
        if resposta == "":
            return None

        if not resposta.isdigit():
            print("Digite só o número do id.")
            continue

        contato = procurar_por_id(encontrados, resposta)
        if contato is None:
            print(f"O id {resposta} não está entre os mostrados.")
            continue
        return contato


def editar(contatos):
    """Altera os campos de um contato escolhido pelo id e salva.

    Para cada campo, mostra o valor atual; Enter vazio mantém o valor.
    """

    if not contatos:
        print("A agenda está vazia.")
        return

    contato = escolher_contato(contatos)
    if contato is None:
        return

    print("\nEnter vazio mantém o valor que está entre colchetes.")
    telefone_atual = formatar_telefone(contato["telefone"])

    nome = perguntar(f"Nome [{contato['nome']}]", obrigatorio=False)
    telefone = perguntar(f"Telefone [{telefone_atual}]", validar_telefone, obrigatorio=False,
                         erro="Telefone inválido. Ex.: (88) 99999-1234 ou +1 415 555 2671")
    email = perguntar(f"E-mail [{contato['email'] or '-'}]", validar_email, obrigatorio=False,
                      erro="E-mail inválido. Ex.: ana.souza@gmail.com")
    aniversario = perguntar(f"Aniversário [{contato['aniversario'] or '-'}]", validar_aniversario,
                            obrigatorio=False, erro="Data inválida. Use DD/MM, como 15/03.")

    # Só troca o que foi digitado; o que ficou vazio continua como estava.
    if nome:
        contato["nome"] = nome
    if telefone:
        contato["telefone"] = normalizar_telefone(telefone)
    if email:
        contato["email"] = email
    if aniversario:
        contato["aniversario"] = aniversario

    salvar(contatos)
    print(f"Contato {contato['nome']} atualizado.")


def confirmar(pergunta):
    """Faz uma pergunta de sim ou não e devolve True só se a resposta for 's'."""

    resposta = input(f"{pergunta} (s/n): ").strip().lower()
    return resposta == "s"


def remover(contatos):
    """Apaga um contato escolhido pelo nome ou pelo id, depois de confirmar, e salva."""

    if not contatos:
        print("A agenda está vazia.")
        return

    contato = escolher_contato(contatos)
    if contato is None:
        return

    telefone = formatar_telefone(contato["telefone"])
    if not confirmar(f"Remover {contato['nome']} ({telefone})?"):
        print("Nada foi removido.")
        return

    contatos.remove(contato)
    salvar(contatos)
    print(f"Contato {contato['nome']} removido.")


MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def aniversariantes(contatos):
    """Mostra quem faz aniversário no mês atual, em ordem de dia.

    Contatos sem aniversário cadastrado ficam de fora.
    """

    hoje = datetime.now()

    # O aniversário é "DD/MM": [:2] é o dia e [3:] é o mês.
    do_mes = []
    for contato in contatos:
        aniversario = contato["aniversario"]
        if aniversario and int(aniversario[3:]) == hoje.month:
            do_mes.append(contato)

    nome_do_mes = MESES[hoje.month - 1]
    if not do_mes:
        print(f"Ninguém faz aniversário em {nome_do_mes}.")
        return

    do_mes.sort(key=lambda contato: int(contato["aniversario"][:2]))

    largura_nome = max(len(contato["nome"]) for contato in do_mes)

    print(f"\nAniversariantes de {nome_do_mes}:")
    for contato in do_mes:
        dia = int(contato["aniversario"][:2])
        telefone = formatar_telefone(contato["telefone"])

        if dia == hoje.day:
            situacao = "  ← hoje!"
        elif dia < hoje.day:
            situacao = "  (já passou)"
        else:
            situacao = ""

        print(f"  {contato['aniversario']}  {contato['nome']:<{largura_nome}}  "
              f"{telefone:<20}{situacao}")


def exportar_csv(contatos):
    """Gera um arquivo .csv com todos os contatos, em ordem alfabética, na pasta dados/.

    O nome do arquivo leva a data, como contatos_2026-11-05.csv.
    """

    if not contatos:
        print("A agenda está vazia, não há o que exportar.")
        return

    data = datetime.now().strftime("%Y-%m-%d")
    caminho = CAMINHO_PADRAO.parent / f"contatos_{data}.csv"

    if caminho.exists() and not confirmar(f"{caminho.name} já existe. Substituir?"):
        print("Nada foi exportado.")
        return

    # No CSV o telefone vai formatado: assim o Excel trata como texto,
    # e não como um número enorme em notação científica.
    linhas = []
    for contato in sorted(contatos, key=chave_nome):
        linha = dict(contato)
        linha["telefone"] = formatar_telefone(contato["telefone"])
        linhas.append(linha)

    gravar_csv(linhas, caminho)
    print(f"{len(linhas)} contato(s) exportado(s) para {caminho}")


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