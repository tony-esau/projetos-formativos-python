"""Salvar relatórios em JSON e comparar com a análise anterior.

Os relatórios ficam em relatorios/, na pasta do script, um arquivo por
execução: relatorio_AAAA-MM-DD_HHMMSS.json.
"""

import json
from datetime import datetime
from pathlib import Path

PASTA_RELATORIOS = Path(__file__).parent / "relatorios"


def resumo_para_salvar(pasta, dados):
    """Monta só o que vale guardar: totais e somas por categoria.

    A lista de arquivos fica de fora, porque é grande e não é usada
    na comparação. Os caminhos viram texto, já que o JSON não aceita Path.
    """

    return {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pasta": str(pasta),
        "total": dados["total"],
        "n_arquivos": dados["n_arquivos"],
        "n_pastas": dados["n_pastas"],
        "por_subpasta": dict(dados["por_subpasta"]),
        "por_extensao": dict(dados["por_extensao"]),
    }


def salvar_relatorio(resumo):
    """Grava o resumo num arquivo novo e devolve o caminho dele."""

    PASTA_RELATORIOS.mkdir(exist_ok=True)
    # A data no formato AAAA-MM-DD_HHMMSS também deixa os nomes em ordem.
    momento = resumo["data"].replace(" ", "_").replace(":", "")
    arquivo = PASTA_RELATORIOS / f"relatorio_{momento}.json"
    # Duas execuções no mesmo segundo: numera, como o nome_livre do B01.
    numero = 1
    while arquivo.exists():
        arquivo = PASTA_RELATORIOS / f"relatorio_{momento} ({numero}).json"
        numero += 1
    texto = json.dumps(resumo, ensure_ascii=False, indent=2)
    arquivo.write_text(texto, encoding="utf-8")
    return arquivo


def carregar_ultimo(pasta):
    """Devolve o relatório mais recente da mesma pasta, ou None."""

    if not PASTA_RELATORIOS.is_dir():
        return None

    candidatos = []
    for arquivo in PASTA_RELATORIOS.glob("relatorio_*.json"):
        try:
            resumo = json.loads(arquivo.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue  # arquivo corrompido ou ilegível: ignora
        if resumo.get("pasta") == str(pasta):
            candidatos.append(resumo)

    if not candidatos:
        return None

    # O formato AAAA-MM-DD HH:MM:SS ordena corretamente como texto.
    return max(candidatos, key=lambda resumo: resumo["data"])


def variacoes(antes, depois):
    """Diferença de tamanho de cada nome entre dois dicionários.

    Nomes que só existem num dos lados contam como 0 do outro lado,
    então pastas novas aparecem como crescimento e pastas apagadas como
    redução. Nomes que não mudaram ficam de fora.

    Retorno: lista de pares (nome, diferença), da maior alta à maior queda.
    """

    nomes = set(antes) | set(depois)   # união: todos os nomes dos dois
    diferencas = [(nome, depois.get(nome, 0) - antes.get(nome, 0))
                  for nome in nomes]
    mudaram = [(nome, dif) for nome, dif in diferencas if dif != 0]
    return sorted(mudaram, key=lambda par: par[1], reverse=True)