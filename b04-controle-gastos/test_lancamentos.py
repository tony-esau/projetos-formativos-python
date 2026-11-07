from datetime import date
from decimal import Decimal

import pytest

from lancamentos import (CAMINHO_CATEGORIAS, adicionar_lancamento,
                         carregar_categorias, converter_linha, filtrar_mes,
                         ler_lancamentos)


@pytest.fixture
def caminho(tmp_path):
    # Cada teste usa um CSV numa pasta temporária, nunca o arquivo real.
    return tmp_path / "dados" / "lancamentos.csv"


@pytest.fixture
def categorias():
    return {"receita": ["Salário"], "despesa": ["Alimentação", "Transporte"]}


def lancamento(dia, tipo="despesa", valor="10.00", categoria="Alimentação",
               descricao="teste"):
    """Monta um lançamento de novembro de 2026 para os testes."""

    return {"data": date(2026, 11, dia), "tipo": tipo,
            "valor": Decimal(valor), "categoria": categoria,
            "descricao": descricao}


def test_categorias_do_projeto_tem_receita_e_despesa():
    categorias = carregar_categorias(CAMINHO_CATEGORIAS)
    assert set(categorias) == {"receita", "despesa"}
    assert "Alimentação" in categorias["despesa"]


def test_arquivo_inexistente_devolve_listas_vazias(caminho):
    assert ler_lancamentos(caminho) == ([], [])


def test_adicionar_e_ler(caminho):
    primeiro = lancamento(5, valor="12.50", descricao="Almoço")
    segundo = lancamento(6, tipo="receita", valor="1500.00",
                         categoria="Salário", descricao="Pagamento")
    adicionar_lancamento(primeiro, caminho)
    adicionar_lancamento(segundo, caminho)

    validos, invalidos = ler_lancamentos(caminho)
    assert validos == [primeiro, segundo]
    assert invalidos == []


def test_cabecalho_so_na_primeira_linha(caminho):
    for dia in (1, 2, 3):
        adicionar_lancamento(lancamento(dia), caminho)

    linhas = caminho.read_text(encoding="utf-8").splitlines()
    assert linhas[0] == "data,tipo,valor,categoria,descricao"
    assert len(linhas) == 4
    assert linhas.count(linhas[0]) == 1


def test_valor_salvo_com_ponto_e_duas_casas(caminho):
    adicionar_lancamento(lancamento(5, valor="12.50"), caminho)
    texto = caminho.read_text(encoding="utf-8")
    assert "2026-11-05,despesa,12.50,Alimentação,teste" in texto


def test_descricao_com_virgula_e_aspas(caminho):
    original = lancamento(5, descricao='Pão, leite e "café"')
    adicionar_lancamento(original, caminho)
    validos, _ = ler_lancamentos(caminho)
    assert validos[0]["descricao"] == 'Pão, leite e "café"'


def test_linhas_invalidas_sao_puladas_com_motivo(caminho):
    caminho.parent.mkdir(parents=True)
    caminho.write_text(
        "data,tipo,valor,categoria,descricao\n"
        "2026-11-05,despesa,12.50,Alimentação,ok\n"
        "2026-02-31,despesa,10.00,Alimentação,data errada\n"
        "2026-11-06,despesa,abc,Alimentação,valor errado\n"
        "2026-11-07,gasto,10.00,Alimentação,tipo errado\n"
        "2026-11-08,despesa\n"
        "2026-11-09,receita,100,Salário,ok\n",
        encoding="utf-8",
    )

    validos, invalidos = ler_lancamentos(caminho)
    assert len(validos) == 2
    assert [numero for numero, _ in invalidos] == [3, 4, 5, 6]
    assert "data inválida" in invalidos[0][1]


def test_categoria_conferida_quando_informada(caminho, categorias):
    caminho.parent.mkdir(parents=True)
    caminho.write_text(
        "data,tipo,valor,categoria,descricao\n"
        "2026-11-05,despesa,10,alimentacao,ok\n"
        "2026-11-05,despesa,10,Salário,despesa com categoria de receita\n"
        "2026-11-05,despesa,10,Comida,não existe\n",
        encoding="utf-8",
    )

    validos, invalidos = ler_lancamentos(caminho, categorias)
    assert validos[0]["categoria"] == "Alimentação"
    assert [numero for numero, _ in invalidos] == [3, 4]


def test_cabecalho_errado(caminho):
    caminho.parent.mkdir(parents=True)
    caminho.write_text("dia,quanto\n05,10\n", encoding="utf-8")
    with pytest.raises(ValueError, match="colunas"):
        ler_lancamentos(caminho)


def test_converter_linha():
    linha = {"data": "2026-11-05", "tipo": "despesa", "valor": "12,5",
             "categoria": " Transporte ", "descricao": " Ônibus "}
    assert converter_linha(linha) == {
        "data": date(2026, 11, 5), "tipo": "despesa",
        "valor": Decimal("12.50"), "categoria": "Transporte",
        "descricao": "Ônibus",
    }


def test_filtrar_mes_e_ordenar():
    outubro = {**lancamento(1), "data": date(2026, 10, 31)}
    dia_20 = lancamento(20)
    dia_3 = lancamento(3)
    dezembro = {**lancamento(1), "data": date(2026, 12, 1)}

    resultado = filtrar_mes([outubro, dia_20, dia_3, dezembro], "2026-11")
    assert resultado == [dia_3, dia_20]


def test_filtrar_mes_sem_lancamentos():
    assert filtrar_mes([lancamento(5)], "2025-01") == []


def test_importar_csv(tmp_path, caminho, categorias):
    from lancamentos import importar_csv

    adicionar_lancamento(lancamento(1), caminho)

    origem = tmp_path / "extrato.csv"
    origem.write_text(
        "data,tipo,valor,categoria,descricao\n"
        "2026-11-05,despesa,\"12,50\",alimentacao,Almoço\n"
        "2026-11-31,despesa,10,Alimentação,data que não existe\n"
        "2026-11-06,receita,1500,Salário,Pagamento\n"
        "2026-11-07,despesa,10,Comida,categoria que não existe\n",
        encoding="utf-8",
    )

    quantidade, invalidos = importar_csv(origem, categorias, caminho)
    assert quantidade == 2
    assert [numero for numero, _ in invalidos] == [3, 5]

    # O lançamento que já existia continua lá, e os novos vêm depois.
    validos, _ = ler_lancamentos(caminho)
    assert len(validos) == 3
    assert validos[1]["valor"] == Decimal("12.50")
    assert validos[1]["categoria"] == "Alimentação"


def test_carregar_orcamento(tmp_path):
    from lancamentos import carregar_orcamento

    caminho = tmp_path / "orcamento.json"
    caminho.write_text('{"Lazer": 50, "Alimentação": 150.5}',
                       encoding="utf-8")
    orcamento = carregar_orcamento(caminho)
    assert orcamento == {"Lazer": Decimal("50"),
                         "Alimentação": Decimal("150.5")}
    assert isinstance(orcamento["Alimentação"], Decimal)


def test_orcamento_inexistente_fica_vazio(tmp_path):
    from lancamentos import carregar_orcamento

    assert carregar_orcamento(tmp_path / "nao_existe.json") == {}


def test_salvar_e_carregar_categorias(tmp_path):
    from lancamentos import salvar_categorias

    caminho = tmp_path / "categorias.json"
    categorias = {"receita": ["Salário"], "despesa": ["Pão", "Café"]}
    salvar_categorias(categorias, caminho)
    assert carregar_categorias(caminho) == categorias
    assert "Pão" in caminho.read_text(encoding="utf-8")


@pytest.mark.parametrize("limite", ["150.00", "12.30", "0.10", "99.99"])
def test_salvar_e_carregar_orcamento_sem_perder_centavos(tmp_path, limite):
    from lancamentos import carregar_orcamento, salvar_orcamento

    caminho = tmp_path / "orcamento.json"
    salvar_orcamento({"Lazer": Decimal(limite)}, caminho)
    assert carregar_orcamento(caminho) == {"Lazer": Decimal(limite)}