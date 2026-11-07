from datetime import date
from decimal import Decimal

import pytest

from relatorio import (barra, formatar_moeda, grafico_barras_texto,
                       montar_relatorio, nome_do_mes, resumo_mes,
                       salvar_relatorio)


def lancamento(dia, tipo, valor, categoria, descricao=""):
    """Monta um lançamento de novembro de 2026 para os testes."""

    return {"data": date(2026, 11, dia), "tipo": tipo,
            "valor": Decimal(valor), "categoria": categoria,
            "descricao": descricao}


@pytest.fixture
def novembro():
    return [
        lancamento(1, "receita", "1500.00", "Salário", "Pagamento"),
        lancamento(2, "despesa", "600.00", "Moradia", "Aluguel"),
        lancamento(3, "despesa", "45.90", "Alimentação", "Mercado"),
        lancamento(5, "despesa", "12.50", "Alimentação", "Almoço"),
        lancamento(8, "despesa", "4.30", "Transporte", "Ônibus"),
        lancamento(9, "receita", "200.00", "Freelance", "Site"),
        lancamento(10, "despesa", "0.10", "Lazer", "Teste de centavos"),
        lancamento(11, "despesa", "0.20", "Lazer", "Teste de centavos"),
    ]


@pytest.mark.parametrize("valor, esperado", [
    ("0", "R$ 0,00"),
    ("12.5", "R$ 12,50"),
    ("1234.56", "R$ 1.234,56"),
    ("1000000", "R$ 1.000.000,00"),
    ("-80", "R$ -80,00"),
])
def test_formatar_moeda(valor, esperado):
    assert formatar_moeda(Decimal(valor)) == esperado


def test_nome_do_mes():
    assert nome_do_mes("2026-11") == "novembro de 2026"
    assert nome_do_mes("2027-03") == "março de 2027"


def test_totais(novembro):
    resumo = resumo_mes(novembro)
    assert resumo["receitas"] == Decimal("1700.00")
    assert resumo["despesas"] == Decimal("663.00")
    assert resumo["saldo"] == Decimal("1037.00")
    assert resumo["quantidade"] == 8


def test_soma_por_categoria_igual_ao_total(novembro):
    # Critério de aceite do roteiro.
    resumo = resumo_mes(novembro)
    assert sum(resumo["por_categoria"].values()) == resumo["despesas"]


def test_por_categoria(novembro):
    por_categoria = resumo_mes(novembro)["por_categoria"]
    assert por_categoria == {
        "Moradia": Decimal("600.00"),
        "Alimentação": Decimal("58.40"),
        "Transporte": Decimal("4.30"),
        "Lazer": Decimal("0.30"),
    }


def test_receitas_nao_entram_nas_categorias(novembro):
    por_categoria = resumo_mes(novembro)["por_categoria"]
    assert "Salário" not in por_categoria


def test_maior_despesa(novembro):
    assert resumo_mes(novembro)["maior_despesa"]["descricao"] == "Aluguel"


def test_mes_sem_lancamentos():
    resumo = resumo_mes([])
    assert resumo["despesas"] == 0
    assert resumo["maior_despesa"] is None


def test_saldo_negativo():
    resumo = resumo_mes([lancamento(1, "despesa", "80", "Lazer")])
    assert resumo["saldo"] == Decimal("-80")


@pytest.mark.parametrize("porcentagem, esperado", [
    (0, "░" * 10), (100, "█" * 10), (50, "█████░░░░░"), (34, "███░░░░░░░"),
])
def test_barra(porcentagem, esperado):
    assert barra(porcentagem, largura=10) == esperado


def test_grafico_ordena_da_maior_para_a_menor(novembro):
    resumo = resumo_mes(novembro)
    linhas = grafico_barras_texto(resumo["por_categoria"],
                                  resumo["despesas"])
    categorias = [linha.split()[0] for linha in linhas]
    assert categorias == ["Moradia", "Alimentação", "Transporte", "Lazer"]


def test_relatorio_tem_as_partes(novembro):
    texto = montar_relatorio("2026-11", resumo_mes(novembro))
    assert "Relatório de novembro de 2026" in texto
    assert "R$ 1.700,00" in texto
    assert "R$ 663,00" in texto
    assert "R$ 1.037,00" in texto
    assert "Maior despesa: R$ 600,00 em 02/11, Moradia (Aluguel)" in texto
    assert "90,5%" in texto


def test_relatorio_mes_vazio():
    texto = montar_relatorio("2025-01", resumo_mes([]))
    assert "Nenhum lançamento" in texto


def test_relatorio_so_com_receitas():
    resumo = resumo_mes([lancamento(1, "receita", "100", "Salário")])
    texto = montar_relatorio("2026-11", resumo)
    assert "Maior despesa" not in texto


def test_arquivo_salvo_identico_ao_texto(tmp_path, novembro):
    # Critério de aceite do roteiro.
    texto = montar_relatorio("2026-11", resumo_mes(novembro))
    caminho = salvar_relatorio(texto, "2026-11", tmp_path / "relatorios")

    assert caminho.name == "relatorio_2026-11.txt"
    assert caminho.read_text(encoding="utf-8") == texto