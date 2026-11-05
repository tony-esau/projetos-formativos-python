import csv
import json
import shutil
from datetime import datetime
from pathlib import Path

# O arquivo fica em dados/, ao lado deste script,
# de onde quer que o programa seja rodado.
CAMINHO_PADRAO = Path(__file__).parent / "dados" / "contatos.json"


def carregar(caminho=CAMINHO_PADRAO):
    """Lê os contatos do JSON e devolve uma lista.

    Se o arquivo não existe, devolve uma lista vazia. Se está corrompido,
    guarda uma cópia em .bak e também devolve uma lista vazia.
    """

    # Primeira vez rodando: ainda não existe arquivo, a agenda começa vazia.
    if not caminho.exists():
        return []

    try:
        contatos = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        contatos = None

    # Se o JSON está quebrado ou não é uma lista,
    # guarda uma cópia e começa do zero.
    if not isinstance(contatos, list):
        backup = fazer_backup(caminho)
        print(f"Aviso: {caminho.name} estava corrompido.")
        print(f"Uma cópia foi guardada em {backup.name}.")
        print("A agenda começou vazia.")
        return []

    return contatos


def fazer_backup(caminho):
    """Copia o arquivo para um .bak e devolve o caminho da cópia.

    O nome leva a data e a hora: contatos_2026-11-05_144100.json.bak.
    """

    # A data e a hora no nome evitam apagar um backup antigo.
    agora = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup = caminho.with_name(f"{caminho.stem}_{agora}.json.bak")
    shutil.copy(caminho, backup)
    return backup


def salvar(contatos, caminho=CAMINHO_PADRAO):
    """Grava a lista de contatos no JSON, mantendo os acentos legíveis."""

    # Cria a pasta dados/ se ela ainda não existir.
    caminho.parent.mkdir(parents=True, exist_ok=True)

    # ensure_ascii=False mantém "José" como "José",
    # e indent=2 deixa o arquivo legível.
    texto = json.dumps(contatos, ensure_ascii=False, indent=2)
    caminho.write_text(texto, encoding="utf-8")


CAMPOS_CSV = ["id", "nome", "telefone", "email", "aniversario"]


def gravar_csv(contatos, caminho):
    """Grava os contatos num arquivo .csv que abre no Excel e no LibreOffice.

    Usa ; como separador, que é o que o Excel em português espera, e
    utf-8-sig, que avisa ao Excel que o arquivo é UTF-8 e preserva os acentos.
    """

    caminho.parent.mkdir(parents=True, exist_ok=True)

    with open(caminho, "w", encoding="utf-8-sig", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                  delimiter=";")
        escritor.writeheader()
        escritor.writerows(contatos)