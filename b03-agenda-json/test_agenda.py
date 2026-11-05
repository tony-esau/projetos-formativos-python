import pytest

from agenda import chave_nome, filtrar_por_nome, procurar_por_id, proximo_id


@pytest.fixture
def contatos():
    nomes = ["José da Silva", "Maria José Souza", "Álvaro Bezerra",
             "ana lima", "Zuleide"]
    ids = [1, 2, 3, 4, 7]
    return [{"id": i, "nome": n} for i, n in zip(ids, nomes)]


def test_proximo_id_lista_vazia():
    assert proximo_id([]) == 1


def test_proximo_id_usa_o_maior_e_nao_o_tamanho(contatos):
    # São 5 contatos, mas o maior id é 7: o próximo precisa ser 8, não 6.
    assert proximo_id(contatos) == 8


def test_ordem_alfabetica_ignora_acento_e_maiuscula(contatos):
    nomes = [c["nome"] for c in sorted(contatos, key=chave_nome)]
    assert nomes == ["Álvaro Bezerra", "ana lima", "José da Silva",
                     "Maria José Souza", "Zuleide"]


@pytest.mark.parametrize("termo, ids", [
    ("jose", [1, 2]),
    ("JOSÉ", [1, 2]),
    ("silva", [1]),
    ("alvaro", [3]),
    ("e", [1, 2, 3, 7]),
    ("xyz", []),
])
def test_filtrar_por_nome(contatos, termo, ids):
    assert [c["id"] for c in filtrar_por_nome(contatos, termo)] == ids


def test_procurar_por_id(contatos):
    assert procurar_por_id(contatos, "3")["nome"] == "Álvaro Bezerra"
    assert procurar_por_id(contatos, "5") is None