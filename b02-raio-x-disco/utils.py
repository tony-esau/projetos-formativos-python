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