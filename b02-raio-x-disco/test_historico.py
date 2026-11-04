"""Testes do salvamento e da comparação de relatórios (historico.py).

Rodar na pasta do projeto com:  python -m pytest
"""

import json

import pytest

import historico
from historico import carregar_ultimo, salvar_relatorio, variacoes


@pytest.fixture(autouse=True)
def relatorios_temporarios(tmp_path, monkeypatch):
    """Faz os relatórios irem para uma pasta temporária nos testes."""
    monkeypatch.setattr(historico, "PASTA_RELATORIOS", tmp_path / "relatorios")


def resumo(data, pasta="C:/Downloads", total=100, por_subpasta=None):
    """Monta um resumo no formato salvo em JSON, só com o necessário."""
    return {
        "data": data,
        "pasta": pasta,
        "total": total,
        "n_arquivos": 1,
        "n_pastas": 0,
        "por_subpasta": por_subpasta or {},
        "por_extensao": {},
    }


# Variações.

def test_variacoes_ordena_da_maior_alta_a_maior_queda():
    antes = {"a": 100, "b": 100, "c": 100}
    depois = {"a": 300, "b": 50, "c": 150}
    assert variacoes(antes, depois) == [("a", 200), ("c", 50), ("b", -50)]


def test_variacoes_pasta_nova_e_pasta_apagada():
    antes = {"velha": 400}
    depois = {"nova": 250}
    assert variacoes(antes, depois) == [("nova", 250), ("velha", -400)]


def test_variacoes_ignora_o_que_nao_mudou():
    assert variacoes({"a": 10, "b": 5}, {"a": 10, "b": 7}) == [("b", 2)]


def test_variacoes_sem_mudanca_devolve_lista_vazia():
    assert variacoes({"a": 10}, {"a": 10}) == []


# Salvar e carregar.

def test_salvar_cria_json_legivel():
    arquivo = salvar_relatorio(resumo("2026-11-04 10:00:00"))
    conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
    assert conteudo["total"] == 100
    assert arquivo.name == "relatorio_2026-11-04_100000.json"


def test_salvar_duas_vezes_no_mesmo_segundo_nao_sobrescreve():
    primeiro = salvar_relatorio(resumo("2026-11-04 10:00:00", total=1))
    segundo = salvar_relatorio(resumo("2026-11-04 10:00:00", total=2))
    assert primeiro != segundo
    assert primeiro.exists() and segundo.exists()


def test_carregar_sem_relatorios_devolve_none():
    assert carregar_ultimo("C:/Downloads") is None


def test_carregar_pega_o_mais_recente_da_mesma_pasta():
    salvar_relatorio(resumo("2026-11-01 09:00:00", total=1))
    salvar_relatorio(resumo("2026-11-03 09:00:00", total=3))
    salvar_relatorio(resumo("2026-11-02 09:00:00", total=2))
    assert carregar_ultimo("C:/Downloads")["total"] == 3


def test_carregar_ignora_outras_pastas():
    salvar_relatorio(resumo("2026-11-05 09:00:00", pasta="C:/Outra"))
    assert carregar_ultimo("C:/Downloads") is None


def test_carregar_ignora_arquivo_corrompido():
    salvar_relatorio(resumo("2026-11-01 09:00:00", total=1))
    corrompido = historico.PASTA_RELATORIOS / "relatorio_quebrado.json"
    corrompido.write_text("{ isso não é json", encoding="utf-8")
    assert carregar_ultimo("C:/Downloads")["total"] == 1


# Impressão.

def test_comparacao_mostra_altas_e_quedas(capsys):
    from relatorio import imprimir_comparacao

    anterior = resumo("2026-11-01 09:00:00", total=1000,
                      por_subpasta={"videos": 600, "docs": 400})
    atual = resumo("2026-11-04 09:00:00", total=1500,
                   por_subpasta={"videos": 1300, "docs": 200})
    imprimir_comparacao(anterior, atual)

    saida = capsys.readouterr().out
    assert "2026-11-01 09:00:00" in saida
    assert "+500 B" in saida      # total
    assert "+700 B" in saida      # videos
    assert "-200 B" in saida      # docs