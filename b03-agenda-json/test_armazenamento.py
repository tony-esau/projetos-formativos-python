import pytest

from armazenamento import carregar, salvar


@pytest.fixture
def caminho(tmp_path):
    # Cada teste usa um contatos.json numa pasta temporária, nunca a agenda real.
    return tmp_path / "dados" / "contatos.json"


@pytest.fixture
def contatos():
    return [
        {
            "id": 1,
            "nome": "José da Silva",
            "telefone": "+5588999991234",
            "email": "jose@gmail.com",
            "aniversario": "15/03",
        },
        {
            "id": 2,
            "nome": "Ana Souza",
            "telefone": "+14155552671",
            "email": "ana@gmail.com",
            "aniversario": "02/11",
        },
    ]


def test_arquivo_inexistente_devolve_lista_vazia(caminho):
    assert carregar(caminho) == []


def test_salvar_e_carregar_devolve_os_mesmos_contatos(caminho, contatos):
    salvar(contatos, caminho)
    assert carregar(caminho) == contatos


def test_salvar_cria_a_pasta(caminho, contatos):
    assert not caminho.parent.exists()
    salvar(contatos, caminho)
    assert caminho.exists()


def test_acentos_ficam_legiveis_no_arquivo(caminho, contatos):
    salvar(contatos, caminho)
    texto = caminho.read_text(encoding="utf-8")
    assert "José" in texto
    assert "\\u00e9" not in texto


def test_salvar_sobrescreve_o_anterior(caminho, contatos):
    salvar(contatos, caminho)
    salvar(contatos[:1], caminho)
    assert carregar(caminho) == contatos[:1]


def test_lista_vazia(caminho):
    salvar([], caminho)
    assert carregar(caminho) == []


@pytest.mark.parametrize("conteudo", [
    "{ isso não é json",
    "",
    '{"nome": "José"}',
    "42",
])
def test_arquivo_corrompido_vira_backup(caminho, conteudo, capsys):
    caminho.parent.mkdir(parents=True)
    caminho.write_text(conteudo, encoding="utf-8")

    assert carregar(caminho) == []

    # O conteúdo original foi guardado no .bak, sem perder nada.
    backups = list(caminho.parent.glob("*.bak"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == conteudo

    assert "corrompido" in capsys.readouterr().out


def test_depois_do_backup_a_agenda_volta_a_funcionar(caminho, contatos):
    caminho.parent.mkdir(parents=True)
    caminho.write_text("{ quebrado", encoding="utf-8")

    carregar(caminho)
    salvar(contatos, caminho)
    assert carregar(caminho) == contatos