"""Testes das funções de utils.py.

Rodar na pasta do projeto com:  python -m pytest
"""

import pytest

from utils import barra_proporcional, formatar_bytes


# parametrize roda o mesmo teste uma vez para cada par (entrada, esperado).
@pytest.mark.parametrize("entrada, esperado", [
    (0, "0 B"),
    (1, "1 B"),
    (1023, "1023 B"),               # ainda não chega a 1 KB
    (1024, "1.0 KB"),               # exatamente 1 KB
    (1536, "1.5 KB"),
    (1024 ** 2, "1.0 MB"),
    (1024 ** 3, "1.0 GB"),          # 1073741824 bytes
    (int(2.5 * 1024 ** 3), "2.5 GB"),
    (1024 ** 4, "1.0 TB"),
])
def test_formatar_bytes(entrada, esperado):
    assert formatar_bytes(entrada) == esperado


def test_formatar_bytes_acima_de_tb_continua_em_tb():
    """Não existe unidade maior que TB na lista, então fica em TB."""
    assert formatar_bytes(1024 ** 5) == "1024.0 TB"


def test_formatar_bytes_usa_uma_casa_decimal():
    """Valores quebrados são arredondados para uma casa decimal."""
    assert formatar_bytes(1100) == "1.1 KB"   # 1100 / 1024 = 1.074...

# Barra.
@pytest.mark.parametrize("porcentagem, esperado", [
    (0, "░░░░░░░░░░"),
    (50, "█████░░░░░"),
    (100, "██████████"),
    (33.3, "███░░░░░░░"),     # 3.33 caracteres -> arredonda para 3
    (36, "████░░░░░░"),       # 3.6 caracteres -> arredonda para 4
])
def test_barra_proporcional(porcentagem, esperado):
    assert barra_proporcional(porcentagem, largura=10) == esperado


@pytest.mark.parametrize("porcentagem", [0, 0.4, 12.5, 49.9, 77.7, 99.9, 100])
def test_barra_tem_sempre_a_largura_pedida(porcentagem):
    """Se o tamanho variar, as colunas do relatório desalinham."""
    assert len(barra_proporcional(porcentagem, largura=20)) == 20


def test_barra_limita_valores_fora_da_faixa():
    assert barra_proporcional(-5, largura=10) == "░" * 10
    assert barra_proporcional(150, largura=10) == "█" * 10


def test_barra_largura_padrao_e_20():
    assert len(barra_proporcional(50)) == 20