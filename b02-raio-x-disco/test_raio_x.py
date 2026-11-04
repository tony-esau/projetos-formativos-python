"""Testes da varredura (raio_x.varrer).

Rodar na pasta do projeto com:  python -m pytest
"""

import pytest

from raio_x import RAIZ, SEM_EXTENSAO, varrer

# Tamanhos fáceis de somar de cabeça.
#
# pasta/
# ├── leia.txt                  500
# ├── LEIA-ME                   300   (sem extensão)
# ├── videos/
# │   ├── aula.mp4             2000
# │   └── antigos/
# │       └── AULA_VELHA.MP4   1000   (extensão em maiúsculas)
# ├── docs/
# │   └── nota.pdf             1500
# └── vazia/                          (pasta sem arquivos)
ARQUIVOS = {
    "leia.txt": 500,
    "LEIA-ME": 300,
    "videos/aula.mp4": 2000,
    "videos/antigos/AULA_VELHA.MP4": 1000,
    "docs/nota.pdf": 1500,
}
TOTAL = sum(ARQUIVOS.values())  # 5300


# Fixtures.

@pytest.fixture
def pasta(tmp_path):
    """Monta a pasta do desenho acima com arquivos de tamanho exato."""

    for caminho, tamanho in ARQUIVOS.items():
        arquivo = tmp_path / caminho
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        arquivo.write_bytes(b"x" * tamanho)

    (tmp_path / "vazia").mkdir()
    return tmp_path


@pytest.fixture
def dados(pasta):
    """Resultado da varredura da pasta de teste."""
    return varrer(pasta)


# Totais.

def test_total_soma_todos_os_arquivos(dados):
    assert dados["total"] == TOTAL


def test_conta_arquivos(dados):
    assert dados["n_arquivos"] == len(ARQUIVOS)


def test_conta_pastas_inclusive_aninhadas_e_vazias(dados):
    # videos, videos/antigos, docs e vazia
    assert dados["n_pastas"] == 4


def test_nada_ignorado_numa_pasta_normal(dados):
    assert dados["ignorados"] == 0


# Ranking.

def test_lista_de_arquivos_tem_um_par_por_arquivo(dados):
    assert len(dados["arquivos"]) == len(ARQUIVOS)


def test_maior_arquivo_vem_primeiro_ao_ordenar(dados):
    tamanho, arquivo = sorted(dados["arquivos"], reverse=True)[0]
    assert tamanho == 2000
    assert arquivo.name == "aula.mp4"


# Subpastas.

def test_soma_por_subpasta_do_primeiro_nivel(dados):
    por_subpasta = dados["por_subpasta"]
    # videos inclui o arquivo de videos/antigos: 2000 + 1000
    assert por_subpasta["videos"] == 3000
    assert por_subpasta["docs"] == 1500


def test_arquivos_soltos_vao_para_a_raiz(dados):
    assert dados["por_subpasta"][RAIZ] == 500 + 300


def test_subpasta_aninhada_nao_aparece_sozinha(dados):
    assert "antigos" not in dados["por_subpasta"]


def test_soma_das_subpastas_e_o_total(dados):
    assert sum(dados["por_subpasta"].values()) == TOTAL


def test_soma_por_extensao(dados):
    assert dados["por_extensao"][".txt"] == 500
    assert dados["por_extensao"][".pdf"] == 1500


def test_extensao_em_maiusculas_soma_com_minusculas(dados):
    assert dados["por_extensao"][".mp4"] == 2000 + 1000
    assert ".MP4" not in dados["por_extensao"]


def test_arquivo_sem_extensao(dados):
    assert dados["por_extensao"][SEM_EXTENSAO] == 300


def test_soma_das_extensoes_e_o_total(dados):
    assert sum(dados["por_extensao"].values()) == TOTAL


def test_pasta_vazia(tmp_path):
    dados = varrer(tmp_path)
    assert dados["total"] == 0
    assert dados["n_arquivos"] == 0
    assert dados["n_pastas"] == 0
    assert not dados["por_subpasta"]
    assert not dados["por_extensao"]


def test_arquivos_vazios_contam_mas_nao_somam(tmp_path):
    (tmp_path / "vazio.txt").touch()
    dados = varrer(tmp_path)
    assert dados["n_arquivos"] == 1
    assert dados["total"] == 0