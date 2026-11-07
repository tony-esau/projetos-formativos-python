from collections import defaultdict
from decimal import Decimal
from pathlib import Path

PASTA_RELATORIOS = Path(__file__).parent / "relatorios"

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]

LARGURA_BARRA = 20


def formatar_moeda(valor):
    """Formata um Decimal como dinheiro: 1234.5 -> 'R$ 1.234,50'.

    Valores negativos ficam com o sinal na frente: 'R$ -80,00'.
    """

    # O formato ',.2f' usa vírgula no milhar e ponto nos centavos, como nos
    # Estados Unidos. As trocas abaixo invertem para o padrão brasileiro.
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"


def nome_do_mes(mes):
    """Transforma '2026-11' em 'novembro de 2026'."""

    ano, numero = mes.split("-")
    return f"{MESES[int(numero) - 1]} de {ano}"


def resumo_mes(lancamentos):
    """Calcula o resumo de uma lista de lançamentos (normalmente de um mês).

    Devolve um dicionário com o total de receitas, o total de despesas, o
    saldo, a soma das despesas por categoria e a maior despesa (ou None).
    """

    receitas = Decimal("0")
    despesas = Decimal("0")
    por_categoria = defaultdict(Decimal)
    maior_despesa = None

    for lancamento in lancamentos:
        valor = lancamento["valor"]

        if lancamento["tipo"] == "receita":
            receitas += valor
            continue

        despesas += valor
        por_categoria[lancamento["categoria"]] += valor
        if maior_despesa is None or valor > maior_despesa["valor"]:
            maior_despesa = lancamento

    return {
        "quantidade": len(lancamentos),
        "receitas": receitas,
        "despesas": despesas,
        "saldo": receitas - despesas,
        "por_categoria": dict(por_categoria),
        "maior_despesa": maior_despesa,
    }


def barra(porcentagem, largura=LARGURA_BARRA):
    """Desenha uma barra proporcional: 50 com largura 10 -> '█████░░░░░'."""

    cheios = round(porcentagem / 100 * largura)
    return "█" * cheios + "░" * (largura - cheios)


def grafico_barras_texto(por_categoria, total):
    """Devolve as linhas do gráfico de despesas por categoria.

    As categorias ficam da maior para a menor despesa, cada uma com a barra,
    o valor e a porcentagem do total.
    """

    if not por_categoria:
        return []

    largura_nome = max(len(categoria) for categoria in por_categoria)
    ordenadas = sorted(por_categoria.items(),
                       key=lambda item: item[1], reverse=True)

    linhas = []
    for categoria, valor in ordenadas:
        porcentagem = valor / total * 100
        texto_porcentagem = f"{porcentagem:5.1f}%".replace(".", ",")
        linhas.append(f"  {categoria:<{largura_nome}}  {barra(porcentagem)}"
                      f"  {formatar_moeda(valor):>13}  {texto_porcentagem}")
    return linhas


def comparar_orcamento(por_categoria, orcamento):
    """Compara o gasto de cada categoria com o limite do orçamento.

    Devolve uma lista de (categoria, gasto, limite), só das categorias que
    têm limite, com as que mais passaram do limite primeiro.
    """

    comparacao = []
    for categoria, limite in orcamento.items():
        gasto = por_categoria.get(categoria, Decimal("0"))
        comparacao.append((categoria, gasto, limite))

    # Ordena pela sobra: gasto - limite. Quem passou mais fica em cima.
    return sorted(comparacao, key=lambda item: item[1] - item[2],
                  reverse=True)


def linhas_orcamento(por_categoria, orcamento):
    """Devolve as linhas da parte do orçamento no relatório."""

    comparacao = comparar_orcamento(por_categoria, orcamento)
    largura_nome = max(len(categoria) for categoria, _, _ in comparacao)
    passaram = 0

    linhas = ["Orçamento"]
    for categoria, gasto, limite in comparacao:
        if gasto > limite:
            passaram += 1
            situacao = f"passou {formatar_moeda(gasto - limite)}"
        else:
            situacao = f"sobram {formatar_moeda(limite - gasto)}"

        linhas.append(f"  {categoria:<{largura_nome}}  "
                      f"{formatar_moeda(gasto):>12} de "
                      f"{formatar_moeda(limite):>12}  {situacao}")

    if passaram == 0:
        linhas.append("  Nenhuma categoria passou do limite.")
    else:
        linhas.append(f"  {passaram} categoria(s) passaram do limite.")
    return linhas


def montar_relatorio(mes, resumo, orcamento=None):
    """Monta o relatório do mês como um texto só.

    O mesmo texto é mostrado na tela e gravado no arquivo, então os dois
    ficam sempre idênticos. Com um orçamento, o relatório mostra também o
    gasto de cada categoria comparado ao limite.
    """

    titulo = f"Relatório de {nome_do_mes(mes)}"
    linhas = [titulo, "=" * len(titulo), ""]

    if resumo["quantidade"] == 0:
        linhas.append("Nenhum lançamento neste mês.")
        return "\n".join(linhas) + "\n"

    linhas += [
        f"  Receitas:  {formatar_moeda(resumo['receitas']):>15}",
        f"  Despesas:  {formatar_moeda(resumo['despesas']):>15}",
        f"  Saldo:     {formatar_moeda(resumo['saldo']):>15}",
        "",
    ]

    if resumo["despesas"] > 0:
        linhas.append("Despesas por categoria")
        linhas += grafico_barras_texto(resumo["por_categoria"],
                                       resumo["despesas"])
        linhas.append("")

        maior = resumo["maior_despesa"]
        data = maior["data"].strftime("%d/%m")
        linhas.append(f"Maior despesa: {formatar_moeda(maior['valor'])} "
                      f"em {data}, {maior['categoria']}"
                      f" ({maior['descricao'] or 'sem descrição'})")
        linhas.append("")

    if orcamento:
        linhas += linhas_orcamento(resumo["por_categoria"], orcamento)
        linhas.append("")

    linhas.append(f"{resumo['quantidade']} lançamento(s) no mês.")
    return "\n".join(linhas) + "\n"


def salvar_relatorio(texto, mes, pasta=PASTA_RELATORIOS):
    """Grava o relatório em relatorios/relatorio_AAAA-MM.txt.

    Devolve o caminho do arquivo gravado.
    """

    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / f"relatorio_{mes}.txt"
    caminho.write_text(texto, encoding="utf-8")
    return caminho