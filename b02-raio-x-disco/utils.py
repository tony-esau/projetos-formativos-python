"""Funções pequenas de formatação, separadas para poderem ser testadas."""

UNIDADES = ["B", "KB", "MB", "GB", "TB"]


def formatar_bytes(n):
    """Converte um número de bytes em texto legível.

    Exemplos: 0 -> '0 B', 1536 -> '1.5 KB', 1073741824 -> '1.0 GB'.
    """

    if n < 1024:
        return f"{n} B"

    valor = float(n)
    for unidade in UNIDADES[1:]:
        valor /= 1024
        if valor < 1024 or unidade == UNIDADES[-1]:
            return f"{valor:.1f} {unidade}"


def barra_proporcional(porcentagem, largura=20):
    """Desenha uma barra de texto proporcional à porcentagem.

    Exemplo com largura 10: 50 -> '█████░░░░░'.
    Valores abaixo de 0 contam como 0, e acima de 100 contam como 100.
    """

    porcentagem = max(0, min(100, porcentagem))
    cheios = round(porcentagem / 100 * largura)
    return "█" * cheios + "░" * (largura - cheios)