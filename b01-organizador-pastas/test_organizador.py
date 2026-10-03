"""Testes automatizados do organizador.

Rodar na pasta do projeto com:  pytest
(instalar uma vez com:  pip install pytest)
"""

import pytest

import organizador
from organizador import (
    PASTA_OUTROS,
    executar_plano,
    limpar_texto_caminho,
    montar_plano,
    nome_livre,
    obter_pasta,
    separar_argumentos,
)

# Regras pequenas, definidas aqui mesmo: os testes não dependem do
# regras.json de verdade.
REGRAS = {
    "Imagens": [".jpg", ".png"],
    "Documentos": [".pdf", ".txt"],
}

# fixtures.

@pytest.fixture
def pasta_bagunçada(tmp_path):
    """Cria uma pasta temporária com arquivos variados e uma subpasta."""

    for nome in ["foto.jpg", "FOTO2.JPG", "logo.png", "nota.pdf",
                 "leia.txt", "dados.xyz", "SEM_EXTENSAO"]:
        (tmp_path / nome).touch()

    subpasta = tmp_path / "antiga"
    subpasta.mkdir()
    (subpasta / "nao_mexer.jpg").touch()

    return tmp_path

@pytest.fixture(autouse=True)
def historicos_temporarios(tmp_path_factory, monkeypatch):
    """Faz os históricos irem para uma pasta temporária durante os testes.

    - autouse=True: vale para todos os testes, sem precisar pedir;
    - tmp_path_factory cria uma pasta temporária separada da tmp_path,
    para os históricos não se misturarem com os arquivos testados;
    monkeypatch troca o valor das constantes só enquanto o teste roda,
    para os testes não sujarem a pasta historicos/ real.
    """

    pasta = tmp_path_factory.mktemp("historicos")
    monkeypatch.setattr(organizador, "PASTA_HISTORICOS", pasta)
    monkeypatch.setattr(organizador, "PASTA_DESFEITOS", pasta / "desfeitos")

def test_nome_livre_devolve_o_mesmo_quando_nao_existe(tmp_path):
    destino = tmp_path / "foto.jpg"
    assert nome_livre(destino) == destino

def test_nome_livre_numera_quando_ja_existe(tmp_path):
    (tmp_path / "foto.jpg").touch()
    assert nome_livre(tmp_path / "foto.jpg") == tmp_path / "foto (1).jpg"

def test_nome_livre_pula_numeros_ocupados(tmp_path):
    (tmp_path / "foto.jpg").touch()
    (tmp_path / "foto (1).jpg").touch()
    assert nome_livre(tmp_path / "foto.jpg") == tmp_path / "foto (2).jpg"

def test_nome_livre_arquivo_sem_extensao(tmp_path):
    (tmp_path / "LEIA-ME").touch()
    assert nome_livre(tmp_path / "LEIA-ME") == tmp_path / "LEIA-ME (1)"

def destinos(plano):
    """Transforma o plano num dicionário nome_do_arquivo -> subpasta."""
    return {arquivo.name: subpasta for arquivo, subpasta in plano}

def test_plano_classifica_pela_extensao(pasta_bagunçada):
    plano = destinos(montar_plano(pasta_bagunçada, REGRAS))
    assert plano["foto.jpg"] == "Imagens"
    assert plano["logo.png"] == "Imagens"
    assert plano["nota.pdf"] == "Documentos"
    assert plano["leia.txt"] == "Documentos"

def test_plano_ignora_maiusculas_na_extensao(pasta_bagunçada):
    plano = destinos(montar_plano(pasta_bagunçada, REGRAS))
    assert plano["FOTO2.JPG"] == "Imagens"

def test_plano_manda_sem_regra_para_outros(pasta_bagunçada):
    plano = destinos(montar_plano(pasta_bagunçada, REGRAS))
    assert plano["dados.xyz"] == PASTA_OUTROS
    assert plano["SEM_EXTENSAO"] == PASTA_OUTROS

def test_plano_ignora_subpastas(pasta_bagunçada):
    plano = destinos(montar_plano(pasta_bagunçada, REGRAS))
    assert "antiga" not in plano
    assert "nao_mexer.jpg" not in plano

def test_plano_tem_um_item_por_arquivo(pasta_bagunçada):
    arquivos = [p for p in pasta_bagunçada.iterdir() if p.is_file()]
    assert len(montar_plano(pasta_bagunçada, REGRAS)) == len(arquivos)

def test_plano_nao_move_nada(pasta_bagunçada):
    antes = sorted(p.name for p in pasta_bagunçada.iterdir())
    montar_plano(pasta_bagunçada, REGRAS)
    depois = sorted(p.name for p in pasta_bagunçada.iterdir())
    assert antes == depois

def test_separa_opcoes_de_caminhos():
    opcoes, caminhos = separar_argumentos(["exemplo", "-s"])
    assert opcoes == {"-s"}
    assert caminhos == ["exemplo"]

def test_tira_aspas_do_caminho():
    assert limpar_texto_caminho('  "C:\\Minha Pasta"  ') == "C:\\Minha Pasta"

def test_opcao_desconhecida_encerra(capsys):
    # capsys captura o que foi impresso, para conferir a mensagem.
    with pytest.raises(SystemExit) as erro:
        separar_argumentos(["--simulr"])
    assert erro.value.code == 1
    assert "--simulr" in capsys.readouterr().out

def test_pasta_inexistente_encerra(tmp_path):
    with pytest.raises(SystemExit):
        obter_pasta([str(tmp_path / "nao_existe")])

def test_mais_de_um_caminho_encerra(tmp_path):
    with pytest.raises(SystemExit):
        obter_pasta([str(tmp_path), str(tmp_path)])

def test_executar_move_os_arquivos(pasta_bagunçada):
    executar_plano(pasta_bagunçada, montar_plano(pasta_bagunçada, REGRAS))

    assert (pasta_bagunçada / "Imagens" / "foto.jpg").exists()
    assert (pasta_bagunçada / "Documentos" / "nota.pdf").exists()
    assert (pasta_bagunçada / PASTA_OUTROS / "dados.xyz").exists()
    assert not (pasta_bagunçada / "foto.jpg").exists()

def test_executar_nao_perde_nenhum_arquivo(pasta_bagunçada):
    """Critério de aceite: o número de arquivos antes e depois é igual."""

    antes = len(list(pasta_bagunçada.rglob("*.*")) +
                list(pasta_bagunçada.rglob("SEM_EXTENSAO")))
    executar_plano(pasta_bagunçada, montar_plano(pasta_bagunçada, REGRAS))
    depois = len(list(pasta_bagunçada.rglob("*.*")) +
                 list(pasta_bagunçada.rglob("SEM_EXTENSAO")))
    assert antes == depois

def test_executar_nao_sobrescreve(pasta_bagunçada):
    (pasta_bagunçada / "Imagens").mkdir()
    (pasta_bagunçada / "Imagens" / "foto.jpg").write_text("antiga")

    executar_plano(pasta_bagunçada, montar_plano(pasta_bagunçada, REGRAS))

    assert (pasta_bagunçada / "Imagens" / "foto.jpg").read_text() == "antiga"
    assert (pasta_bagunçada / "Imagens" / "foto (1).jpg").exists()

def test_desfazer_volta_ao_estado_original(pasta_bagunçada):
    antes = sorted(p.name for p in pasta_bagunçada.iterdir())

    executar_plano(pasta_bagunçada, montar_plano(pasta_bagunçada, REGRAS))
    organizador.desfazer([str(pasta_bagunçada)], simulacao=False)

    depois = sorted(p.name for p in pasta_bagunçada.iterdir())
    assert antes == depois

def test_desfazer_nao_desfaz_duas_vezes(pasta_bagunçada, capsys):
    executar_plano(pasta_bagunçada, montar_plano(pasta_bagunçada, REGRAS))
    organizador.desfazer([str(pasta_bagunçada)], simulacao=False)
    capsys.readouterr()  # descarta o que foi impresso até aqui

    organizador.desfazer([str(pasta_bagunçada)], simulacao=False)
    assert "Nenhuma organização" in capsys.readouterr().out