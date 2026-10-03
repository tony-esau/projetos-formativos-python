"""Cria a pasta exemplo/ com arquivos falsos para testar o organizador.

Uso: python gerar_exemplo.py

Os arquivos são vazios (0 bytes): servem só para testar a organização
pelas extensões. A pasta fica ao lado deste script.
"""

import shutil
import sys
from pathlib import Path

PASTA_DO_SCRIPT = Path(__file__).parent # Pai da pasta.
PASTA_EXEMPLO = PASTA_DO_SCRIPT / "exemplo"

ARQUIVOS = [
    # Imagens (inclui extensões em maiúsculas)
    "foto_praia.jpg", "FOTO_FESTA.JPG", "logo.png", "meme.gif",
    "wallpaper.webp", "icone.svg",
    # Documentos
    "curriculo.pdf", "contrato.docx", "anotacoes.txt", "resumo.md",
    "artigo_ic.tex",
    # Planilhas
    "gastos_outubro.xlsx", "dados_enem.csv", "notas.ods",
    # Apresentações
    "seminario.pptx", "aula_grafos.odp",
    # Vídeos e áudios
    "aula_gravada.mp4", "trailer.mkv", "podcast.mp3", "musica.flac",
    # Compactados
    "backup.zip", "projeto.tar.gz", "fotos_antigas.rar",
    # Programas
    "instalador.exe", "app.msi",
    # Código
    "script.py", "analise.ipynb", "pagina.html", "consulta.sql",
    # Sem regra: devem ir para Outros
    "arquivo_estranho.xyz", "LEIA-ME", "dados.bin",
    # Nomes com espaços e acentos
    "relatório final.pdf", "música favorita.mp3",
]

# Subpastas que o organizador deve ignorar (só mexe no primeiro nível).
SUBPASTAS = ["pasta_antiga", "pasta_antiga/sub"]

# Arquivo que já está numa subpasta com o mesmo nome de um arquivo da raiz.
# Ao organizar, o da raiz deve virar "logo (1).png".
CONFLITO = "Imagens/logo.png"

def criar_exemplo():
    """Cria a pasta exemplo/ com todos os arquivos de teste."""

    PASTA_EXEMPLO.mkdir()

    for nome in ARQUIVOS:
        (PASTA_EXEMPLO / nome).touch()

    for nome in SUBPASTAS:
        (PASTA_EXEMPLO / nome).mkdir()
    (PASTA_EXEMPLO / "pasta_antiga" / "nao_mexer.txt").touch()

    conflito = PASTA_EXEMPLO / CONFLITO
    conflito.parent.mkdir()
    conflito.touch()

def main():
    if PASTA_EXEMPLO.exists():
        resposta = input(
            f"A pasta {PASTA_EXEMPLO} já existe. "
            "Apagar e criar de novo? (s/n) ").strip().lower()
        if resposta != "s":
            print("Nada foi alterado.")
            sys.exit(0)
        shutil.rmtree(PASTA_EXEMPLO)

    criar_exemplo()

    total = len(ARQUIVOS)
    print(f"Pasta criada: {PASTA_EXEMPLO}")
    print(f"{total} arquivos no primeiro nível, "
          f"{len(SUBPASTAS)} subpastas para ignorar "
          f"e 1 caso de nome repetido ({CONFLITO}).")
    print("\nPara testar:")
    print("  python organizador.py exemplo -s")
    print("  python organizador.py exemplo")
    print("  python organizador.py exemplo -d")


if __name__ == "__main__":
    main()