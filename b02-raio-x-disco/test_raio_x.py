"""Testes da varredura (raio_x.varrer) e dos argumentos.

Rodar na pasta do projeto com:  python -m pytest
"""

import os

import pytest

import raio_x
from raio_x import RAIZ, SEM_EXTENSAO, TOP_PADRAO, separar_argumentos, varrer
from relatorio import imprimir_maiores, imprimir_rodape

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
    assert dados["sem_permissao"] == []
    assert dados["links_quebrados"] == 0


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


# Extensões.

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


# Casos extremos.

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


# Inacessíveis.

def test_link_quebrado_e_contado_e_nao_soma(tmp_path):
    (tmp_path / "real.txt").write_bytes(b"x" * 100)
    try:
        os.symlink(tmp_path / "nao_existe", tmp_path / "quebrado")
    except OSError:
        # No Windows, criar links exige permissão de administrador.
        pytest.skip("o sistema não permitiu criar o link")

    dados = varrer(tmp_path)
    assert dados["links_quebrados"] == 1
    assert dados["n_arquivos"] == 1
    assert dados["total"] == 100


def test_pasta_sem_permissao_e_registrada(tmp_path, monkeypatch):
    """Simula uma pasta que o sistema não deixa abrir.

    Trocar as permissões de verdade não funciona igual em todo sistema
    (e não tem efeito para o administrador), então o os.walk é trocado
    por uma versão que avisa o erro antes de seguir com a varredura real.
    """

    (tmp_path / "a.txt").write_bytes(b"x" * 10)
    secreta = str(tmp_path / "secreta")
    walk_original = os.walk

    def walk_falso(topo, onerror=None):
        onerror(PermissionError(13, "Acesso negado", secreta))
        yield from walk_original(topo, onerror=onerror)

    monkeypatch.setattr(raio_x.os, "walk", walk_falso)

    dados = varrer(tmp_path)
    assert dados["sem_permissao"] == [secreta]
    assert dados["total"] == 10   # O resto da varredura continua.


def test_rodape_lista_o_que_foi_ignorado(capsys):
    dados = {"sem_permissao": ["C:/sistema"], "links_quebrados": 2,
             "ignorados": 1}
    imprimir_rodape(dados)
    saida = capsys.readouterr().out
    assert "1 pasta(s) sem permissão" in saida
    assert "2 link(s) quebrado(s)" in saida
    assert "1 arquivo(s)" in saida
    assert "C:/sistema" in saida


def test_rodape_nao_imprime_nada_se_nada_foi_ignorado(capsys):
    imprimir_rodape({"sem_permissao": [], "links_quebrados": 0,
                     "ignorados": 0})
    assert capsys.readouterr().out == ""


# Opção -n.

def test_sem_n_usa_o_padrao():
    _, caminhos, top = separar_argumentos(["Downloads"])
    assert caminhos == ["Downloads"]
    assert top == TOP_PADRAO


@pytest.mark.parametrize("argumentos", [
    ["Downloads", "-n", "5"],
    ["-n", "5", "Downloads"],
    ["--top", "5", "Downloads"],
])
def test_n_le_o_numero_e_nao_o_trata_como_caminho(argumentos):
    _, caminhos, top = separar_argumentos(argumentos)
    assert top == 5
    assert caminhos == ["Downloads"]


@pytest.mark.parametrize("argumentos", [
    ["-n"],                 # Faltou o número.
    ["-n", "cinco"],        # Não é número.
    ["-n", "0"],            # Precisa ser pelo menos 1.
    ["-n", "-3"],
])
def test_n_invalido_encerra(argumentos):
    with pytest.raises(SystemExit):
        separar_argumentos(argumentos)


def test_maiores_respeita_o_top(pasta, dados, capsys):
    imprimir_maiores(pasta, dados, top=2)
    linhas = capsys.readouterr().out.strip().splitlines()
    # um título e duas linhas de ranking
    assert len(linhas) == 3

# Opção -s.

@pytest.mark.parametrize("opcao", ["-s", "--salvar"])
def test_opcao_salvar_e_aceita(opcao):
    opcoes, caminhos, _ = separar_argumentos(["Downloads", opcao])
    assert opcao in opcoes
    assert caminhos == ["Downloads"]