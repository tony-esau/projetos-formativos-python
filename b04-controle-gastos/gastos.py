import os
import subprocess
from pathlib import Path

from lancamentos import (CAMINHO_PADRAO, adicionar_lancamento,
                         carregar_categorias, carregar_orcamento, filtrar_mes,
                         importar_csv, ler_lancamentos, salvar_categorias,
                         salvar_orcamento)
from relatorio import (formatar_moeda, montar_relatorio, nome_do_mes,
                       resumo_mes, salvar_relatorio)
from validacao import (converter_categoria, converter_data, converter_mes,
                       converter_nova_categoria, converter_tipo,
                       converter_valor)

LARGURA_MENU = 36


def limpar_tela():
    """Apaga tudo o que está no terminal (cls no Windows, clear no resto)."""

    if os.name == "nt":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)


def pausar():
    """Espera o usuário apertar Enter antes de seguir."""

    input("\nPressione Enter para voltar ao menu...")


def linha_da_caixa(texto=""):
    """Devolve uma linha da caixa do menu, com o texto e as bordas laterais."""

    return f"│ {texto:<{LARGURA_MENU}} │"


def mostrar_titulo(titulo):
    """Mostra o título da tela atual, sublinhado."""

    print(titulo.upper())
    print("─" * len(titulo))


def perguntar(rotulo, converter=None):
    """Pergunta um campo e repete enquanto a resposta for inválida.

    converter é uma das funções do validacao.py: ela devolve o valor
    convertido ou levanta ValueError com o motivo, que é mostrado ao
    usuário antes de perguntar de novo. Sem converter, devolve o texto.
    """

    while True:
        resposta = input(f"{rotulo}: ")
        if converter is None:
            return resposta.strip()

        try:
            return converter(resposta)
        except ValueError as erro:
            print(f"  {erro}")


def escolher_categoria(categorias_do_tipo):
    """Mostra as categorias numeradas e devolve a escolhida.

    Aceita o número da lista ou o nome da categoria.
    """

    for numero, categoria in enumerate(categorias_do_tipo, start=1):
        print(f"  {numero}. {categoria}")

    def converter(texto):
        """Converte o número ou o nome digitado na categoria da lista."""

        texto = texto.strip()
        if texto.isdigit() and 1 <= int(texto) <= len(categorias_do_tipo):
            return categorias_do_tipo[int(texto) - 1]
        return converter_categoria(texto, categorias_do_tipo)

    return perguntar("Categoria (número ou nome)", converter)


def ler_com_aviso():
    """Lê os lançamentos do arquivo principal.

    Avisa se alguma linha foi pulada por estar inválida.
    """

    validos, invalidos = ler_lancamentos(CAMINHO_PADRAO)
    if invalidos:
        print(f"Aviso: {len(invalidos)} linha(s) inválida(s) em "
              f"{CAMINHO_PADRAO.name} foram ignoradas.")
    return validos


def novo_lancamento(categorias):
    """Pergunta os dados de um lançamento e acrescenta no CSV."""

    data = perguntar("Data (DD/MM/AAAA, Enter para hoje)", converter_data)
    tipo = perguntar("Tipo (r = receita, d = despesa)", converter_tipo)
    valor = perguntar("Valor (ex.: 12,50)", converter_valor)
    categoria = escolher_categoria(categorias[tipo])
    descricao = perguntar("Descrição (opcional)")

    lancamento = {"data": data, "tipo": tipo, "valor": valor,
                  "categoria": categoria, "descricao": descricao}
    adicionar_lancamento(lancamento)
    print(f"\n{tipo.capitalize()} de {formatar_moeda(valor)} em "
          f"{data.strftime('%d/%m/%Y')} registrada.")


def listar_mes(categorias):
    """Mostra os lançamentos de um mês, em ordem de data, com o saldo."""

    mes = perguntar("Mês (MM-AAAA, Enter para o atual)", converter_mes)
    do_mes = filtrar_mes(ler_com_aviso(), mes)

    if not do_mes:
        print(f"\nNenhum lançamento em {nome_do_mes(mes)}.")
        return

    largura = max(len(lancamento["categoria"]) for lancamento in do_mes)
    print(f"\nLançamentos de {nome_do_mes(mes)}\n")
    for lancamento in do_mes:
        # Receitas aparecem com +, despesas com -.
        sinal = "+" if lancamento["tipo"] == "receita" else "-"
        valor = f"{sinal} {formatar_moeda(lancamento['valor'])}"
        print(f"  {lancamento['data'].strftime('%d/%m')}  "
              f"{lancamento['categoria']:<{largura}}  {valor:>15}  "
              f"{lancamento['descricao']}")

    saldo = resumo_mes(do_mes)["saldo"]
    print(f"\n{len(do_mes)} lançamento(s). Saldo: {formatar_moeda(saldo)}")


def relatorio_mes(categorias):
    """Mostra o relatório de um mês e salva o mesmo texto em relatorios/."""

    mes = perguntar("Mês (MM-AAAA, Enter para o atual)", converter_mes)
    do_mes = filtrar_mes(ler_com_aviso(), mes)

    # O orçamento é lido a cada relatório, então mudanças no orcamento.json
    # valem sem precisar reiniciar o programa.
    orcamento = carregar_orcamento()
    texto = montar_relatorio(mes, resumo_mes(do_mes), orcamento)
    print()
    print(texto)

    if do_mes:
        caminho = salvar_relatorio(texto, mes)
        print(f"Relatório salvo em relatorios/{caminho.name}")


def importar(categorias):
    """Importa os lançamentos válidos de outro CSV e explica os pulados."""

    print("O arquivo precisa ter as colunas: "
          "data,tipo,valor,categoria,descricao")
    print("com a data no formato AAAA-MM-DD.\n")

    texto = perguntar("Caminho do CSV (Enter para cancelar)")
    if texto == "":
        return

    # Tira as aspas que o Windows coloca ao copiar o caminho de um arquivo.
    origem = Path(texto.strip('"'))
    if not origem.is_file():
        print(f"Arquivo não encontrado: {origem}")
        return
    if origem.resolve() == CAMINHO_PADRAO.resolve():
        print("Esse já é o arquivo principal de lançamentos.")
        return

    try:
        quantidade, invalidos = importar_csv(origem, categorias)
    except ValueError as erro:
        print(f"Não foi possível importar: {erro}")
        return

    print(f"\n{quantidade} lançamento(s) importado(s).")
    if invalidos:
        print(f"{len(invalidos)} linha(s) ignorada(s):")
        for numero, motivo in invalidos:
            print(f"  linha {numero}: {motivo}")


def converter_limite(texto):
    """Converte o limite do orçamento. Enter vazio vira None (sem limite)."""

    if texto.strip() == "":
        return None
    return converter_valor(texto)


def mostrar_categorias(categorias, orcamento):
    """Mostra as categorias de despesa com o limite e as de receita."""

    print("Despesas (limite do orçamento por mês)")
    for categoria in categorias["despesa"]:
        limite = orcamento.get(categoria)
        texto = formatar_moeda(limite) if limite is not None else "-"
        print(f"  {categoria:<20}  {texto:>12}")

    print("\nReceitas")
    for categoria in categorias["receita"]:
        print(f"  {categoria}")


def adicionar_categoria(categorias, orcamento):
    """Cria uma categoria nova e, se for de despesa, pergunta o limite."""

    tipo = perguntar("Tipo (r = receita, d = despesa)", converter_tipo)
    todas = categorias["receita"] + categorias["despesa"]
    nome = perguntar("Nome da categoria",
                     lambda texto: converter_nova_categoria(texto, todas))

    categorias[tipo].append(nome)
    salvar_categorias(categorias)

    if tipo == "despesa":
        limite = perguntar("Limite por mês (Enter para não ter limite)",
                           converter_limite)
        if limite is not None:
            orcamento[nome] = limite
            salvar_orcamento(orcamento)

    print(f"\nCategoria {nome} criada.")


def definir_limite(categorias, orcamento):
    """Define, troca ou apaga o limite de uma categoria de despesa."""

    categoria = escolher_categoria(categorias["despesa"])
    atual = orcamento.get(categoria)
    texto_atual = formatar_moeda(atual) if atual is not None else "sem limite"

    print(f"Limite atual: {texto_atual}")
    limite = perguntar("Novo limite (Enter para ficar sem limite)",
                       converter_limite)

    if limite is None:
        orcamento.pop(categoria, None)
        print(f"\n{categoria} ficou sem limite.")
    else:
        orcamento[categoria] = limite
        print(f"\nLimite de {categoria}: {formatar_moeda(limite)}.")
    salvar_orcamento(orcamento)


def remover_categoria(categorias, orcamento):
    """Apaga uma categoria e o limite dela, mantendo os lançamentos antigos."""

    tipo = perguntar("Tipo (r = receita, d = despesa)", converter_tipo)
    if len(categorias[tipo]) == 1:
        print("É preciso ter pelo menos uma categoria de cada tipo.")
        return

    categoria = escolher_categoria(categorias[tipo])
    resposta = input(f"Remover {categoria}? Os lançamentos já feitos "
                     f"continuam no CSV. (s/n): ")
    if resposta.strip().lower() != "s":
        print("Nada foi removido.")
        return

    categorias[tipo].remove(categoria)
    salvar_categorias(categorias)
    if orcamento.pop(categoria, None) is not None:
        salvar_orcamento(orcamento)
    print(f"\nCategoria {categoria} removida.")


def gerenciar_categorias(categorias):
    """Mostra as categorias e o orçamento e deixa criar, alterar e apagar."""

    acoes = {
        "1": adicionar_categoria,
        "2": definir_limite,
        "3": remover_categoria,
    }

    while True:
        orcamento = carregar_orcamento()
        mostrar_categorias(categorias, orcamento)

        print("\n1. Nova categoria   2. Definir limite   "
              "3. Remover categoria   0. Voltar")
        opcao = input("Escolha: ").strip()
        if opcao == "0":
            return
        if opcao not in acoes:
            print("Opção inválida.")
        else:
            print()
            acoes[opcao](categorias, orcamento)

        input("\nPressione Enter para continuar...")
        limpar_tela()
        mostrar_titulo("Categorias e orçamento")


# Cada opção do menu: o número, o título que aparece e a função chamada.
OPCOES = {
    "1": ("Novo lançamento", novo_lancamento),
    "2": ("Lançamentos do mês", listar_mes),
    "3": ("Relatório do mês", relatorio_mes),
    "4": ("Importar CSV", importar),
    "5": ("Categorias e orçamento", gerenciar_categorias),
}


def mostrar_menu():
    """Mostra o menu principal numa caixa."""

    borda = "─" * (LARGURA_MENU + 2)

    print(f"┌{borda}┐")
    print(linha_da_caixa("CONTROLE DE GASTOS".center(LARGURA_MENU)))
    print(f"├{borda}┤")
    for numero, (titulo, _) in OPCOES.items():
        print(linha_da_caixa(f" {numero}  {titulo}"))
    print(f"├{borda}┤")
    print(linha_da_caixa(" 0  Sair"))
    print(f"└{borda}┘")


def main():
    """Carrega as categorias e repete o menu até o usuário escolher sair."""

    categorias = carregar_categorias()
    limpar_tela()

    while True:
        mostrar_menu()
        opcao = input("Escolha: ").strip()

        if opcao == "0":
            print("Até mais!")
            break

        if opcao not in OPCOES:
            print(f"Opção inválida, digite um número de 0 a {len(OPCOES)}.")
        else:
            titulo, funcao = OPCOES[opcao]
            limpar_tela()
            mostrar_titulo(titulo)
            funcao(categorias)

        pausar()
        limpar_tela()


if __name__ == "__main__":
    main()