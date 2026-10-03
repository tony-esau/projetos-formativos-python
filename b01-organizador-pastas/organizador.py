import sys
import os
from pathlib import Path
import json
from collections import defaultdict
import shutil
from datetime import datetime

# python organizador.py [-h] [-s] [-d] [CAMINHO]

PASTA_DO_SCRIPT = Path(__file__).parent
ARQUIVO_REGRAS = PASTA_DO_SCRIPT / "regras.json"
PASTA_HISTORICOS = PASTA_DO_SCRIPT / "historicos"
PASTA_DESFEITOS = PASTA_HISTORICOS / "desfeitos"
PASTA_OUTROS = "Outros"

OPCOES_AJUDA = {"-h", "--help", "-help"}
OPCOES_SIMULAR = {"-s", "--simular"}
OPCOES_DESFAZER = {"-d", "--desfazer"}

TEXTO_SOBRE = """---------------- O que esse programa faz? -------------------

- Organiza os arquivos de uma pasta, movendo cada um para uma
  subpasta de acordo com a sua extensão. Por exemplo:
      .jpg e .png   ->  Imagens
      .pdf e .docx  ->  Documentos

- Extensões que não estão nas regras vão para a pasta Outros.

- As regras ficam no arquivo regras.json e podem ser editadas
  sem mexer no código.

- Nenhum arquivo é sobrescrito: se já existir um arquivo com o
  mesmo nome no destino, o novo recebe um número, como
  foto (1).jpg.

- Cada organização gera um histórico na pasta historicos/,
  que permite desfazer a operação com a opção -d."""

TEXTO_ARGUMENTOS = """------------ Argumentos deste programa -------------

Uso: python organizador.py [-h] [-s] [-d] [CAMINHO]

CAMINHO
  Caminho da pasta que será organizada. Se não for
  informado, o programa pergunta. Use aspas se o
  caminho tiver espaços.

-s, --simular
  Mostra o que seria feito (origem -> destino),
  sem mover nenhum arquivo.

-d, --desfazer
  Desfaz a última organização, devolvendo os arquivos
  ao lugar original. Com CAMINHO, desfaz a última
  organização daquela pasta. Pode ser combinada com -s
  para só mostrar o que seria desfeito.

-h, --help
  Mostra esta ajuda.

Exemplos:
  python organizador.py C:\\Users\\joao\\Downloads
  python organizador.py exemplo -s
  python organizador.py "C:\\Minha Pasta" --simular
  python organizador.py --desfazer
  python organizador.py exemplo -d -s"""

def limpar_tela(esperar=True):
    """Limpa o terminal."""

    if esperar:
        print()
        input('Enter para continuar...')
    os.system("cls" if os.name == "nt" else "clear")


def encerrar_com_erro(mensagem):
    """Mostra uma mensagem de erro e encerra com código 1."""

    print(f"Erro: {mensagem}")
    print("Use -h para ver a ajuda.")
    sys.exit(1)


def limpar_texto_caminho(texto):
    """Remove espaços e aspas das pontas (ex.: "Copiar como caminho")."""

    return texto.strip().strip('"')

def separar_argumentos(argumentos):
    """Separa o que é opção (começa com '-') do que é caminho.

    Retorno: (conjunto de opções, lista de caminhos em texto).
    """

    opcoes = {a for a in argumentos if a.startswith("-")}
    caminhos = [limpar_texto_caminho(a) for a in argumentos
                if not a.startswith("-")]

    desconhecidas = opcoes - OPCOES_AJUDA - OPCOES_SIMULAR - OPCOES_DESFAZER
    if desconhecidas:
        encerrar_com_erro(
            f"opção desconhecida: {', '.join(sorted(desconhecidas))}")

    return opcoes, caminhos


def mostrar_ajuda():
    """Imprime a ajuda completa."""

    print(TEXTO_SOBRE)
    print()
    print(TEXTO_ARGUMENTOS)


def ler_caminho():
    """ Função para o caso em que o usuário não repassou o caminho.
        Retorno: caminho da pasta.
    """

    while True:
        caminho = input(
            "Digite o caminho (ou só Enter para a pasta atual): ")
        caminho = Path(limpar_texto_caminho(caminho))

        if caminho.is_dir():
            return caminho.resolve()

        print("Pasta não encontrada!")
        print("Digite 'q' para sair do programa ou pressione Enter "
              "para tentar novamente.")
        if input().strip().lower() == 'q':
            sys.exit(0)


def obter_pasta(caminhos):
    """Decide qual pasta será organizada.

    - Nenhum caminho: pergunta ao usuário.
    - Mais de um: erro (provavelmente faltaram aspas).
    - Um: usa, se for uma pasta válida.
    Retorno: Path absoluto de uma pasta que existe.
    """

    if not caminhos:
        return ler_caminho()

    if len(caminhos) > 1:
        encerrar_com_erro(
            f"foram informados {len(caminhos)} caminhos. "
            "Se o caminho tem espaços, coloque-o entre aspas.")

    pasta = Path(caminhos[0])
    if not pasta.is_dir():
        encerrar_com_erro(f"a pasta '{caminhos[0]}' não existe.")

    return pasta.resolve()


def carregar_regras():
    """Lê o regras.json que fica na pasta do script."""

    try:
        texto = ARQUIVO_REGRAS.read_text(encoding="utf-8")
        return json.loads(texto)
    except FileNotFoundError:
        encerrar_com_erro(
                f"arquivo de regras não encontrado: {ARQUIVO_REGRAS}"
            )
    except json.JSONDecodeError as erro:
        encerrar_com_erro(f"regras.json com formato inválido ({erro}).")


def montar_plano(pasta, regras):
    """Decide, sem mover nada, para qual subpasta vai cada arquivo.

    Retorno: lista de pares (arquivo, nome_da_subpasta).
    """

    arquivos = [item for item in pasta.iterdir() if item.is_file()]
    plano = []

    for arquivo in arquivos:
        associou = False
        for chave in regras.keys():
            # .suffix devolve uma string após o último ponto.
            if arquivo.suffix.lower() in regras[chave]:
                plano.append((arquivo, chave))
                associou = True
                break
        if not associou:
            plano.append((arquivo, PASTA_OUTROS))

    return plano

def imprimir_simulacao(pasta, plano):
    """Mostra em formato de árvore como a pasta ficaria após organizar."""

    # Todo append já começa com uma coleção vazia.
    impressao = defaultdict(list)
    for arquivo, subpasta in plano:
        impressao[subpasta].append(arquivo.name)

    print("[SIMULAÇÃO] Nenhum arquivo será movido.\n")
    print(f"{pasta}/")

    pastas = list(impressao.items())
    for i, (nome_pasta, arquivos) in enumerate(pastas):
        ultima_pasta = i == len(pastas) - 1
        print(("└── " if ultima_pasta else "├── ") + f"{nome_pasta}/")

        recuo = "    " if ultima_pasta else "│   "
        for j, arquivo in enumerate(arquivos):
            ultimo_arquivo = j == len(arquivos) - 1
            ponta = "└── " if ultimo_arquivo else "├── "
            print(recuo + ponta + arquivo)

    print(f"\nTotal: {len(plano)} arquivo(s) em "
          f"{len(pastas)} pasta(s) distintas.")

def nome_livre(destino):
    """Devolve um caminho que ainda não existe, numerando se preciso.

    Exemplo: se foto.jpg já existe, tenta foto (1).jpg, foto (2).jpg...
    """
    if not destino.exists():
        return destino

    numero = 1
    while True:
        candidato = destino.with_name(
            f"{destino.stem} ({numero}){destino.suffix}"
        )
        if not candidato.exists():
            return candidato
        numero += 1

def salvar_historico(pasta, movimentos):
    """Grava os movimentos feitos num histórico novo, para poder desfazer.

    Cada organização gera um arquivo próprio em historicos/. Se o nome já
    existir, nome_livre numera: historico.json, historico (1).json...
    """

    historico = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pasta": str(pasta),
        "movimentos": movimentos,
    }

    # Fica na pasta do script (Path(__file__).parent): Path.cwd() mudaria
    # conforme a pasta de onde o programa é chamado no terminal.
    PASTA_HISTORICOS.mkdir(exist_ok=True)
    arquivo = nome_livre(PASTA_HISTORICOS / "historico.json")
    texto = json.dumps(historico, ensure_ascii=False, indent=2)
    arquivo.write_text(texto, encoding="utf-8")
    print(f"Histórico salvo em: {arquivo}")

def executar_plano(pasta, plano):
    """Move os arquivos conforme o plano e grava o histórico.

    O histórico é salvo mesmo se der erro no meio (finally).
    """

    movimentos = []
    try:
        for arquivo, nome_subpasta in plano:
            subpasta = pasta / nome_subpasta
            subpasta.mkdir(exist_ok=True)
            destino = nome_livre(subpasta / arquivo.name)
            shutil.move(arquivo, destino)

            # Guardando os movimentos caso o usuário queira voltar
            # ao estado inicial.
            movimentos.append({
                "origem": str(arquivo),
                "destino": str(destino),
            })
    finally:
        salvar_historico(pasta, movimentos)
        print(f"{len(movimentos)} de {len(plano)} arquivo(s) movido(s).")

def ultimo_historico(pasta=None):
    """Encontra o histórico mais recente ainda não desfeito.

    Se a pasta for informada, considera só os históricos dela.
    Retorno: (caminho do arquivo, conteúdo) ou (None, None).
    """

    if not PASTA_HISTORICOS.is_dir():
        return None, None

    candidatos = []
    for arquivo in PASTA_HISTORICOS.glob("*.json"):
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"Aviso: histórico ilegível ignorado: {arquivo.name}")
            continue
        if pasta is None or Path(dados["pasta"]) == pasta:
            candidatos.append((dados["data"], arquivo, dados))

    if not candidatos:
        return None, None

    # A data no formato AAAA-MM-DD HH:MM:SS ordena corretamente como texto.
    _, arquivo, dados = max(
        candidatos, key=lambda c: (c[0], c[1].stat().st_mtime)
    )
    return arquivo, dados


def desfazer(caminhos, simulacao):
    """Devolve os arquivos da última organização aos lugares originais."""

    pasta = obter_pasta(caminhos) if caminhos else None
    arquivo, dados = ultimo_historico(pasta)

    if arquivo is None:
        alvo = f"da pasta {pasta}" if pasta else "registrada"
        print(f"Nenhuma organização {alvo} para desfazer.")
        return

    movimentos = dados["movimentos"]
    print(f"Desfazendo a organização de {dados['data']} em {dados['pasta']}")
    print(f"({len(movimentos)} arquivo(s), histórico {arquivo.name})\n")

    if simulacao:
        print("[SIMULAÇÃO] Nenhum arquivo será movido.\n")
        for mov in reversed(movimentos):
            print(f"{Path(mov['destino']).name}  ->  {mov['origem']}")
        return

    devolvidos = 0
    subpastas = set()
    # Ordem inversa: desfaz do último movimento para o primeiro.
    for mov in reversed(movimentos):
        atual = Path(mov["destino"])
        original = Path(mov["origem"])

        if not atual.exists():
            print(f"Aviso: {atual} não existe mais, ignorado.")
            continue

        destino = nome_livre(original)
        if destino != original:
            print(f"Aviso: {original.name} já existe, "
                  f"devolvido como {destino.name}.")

        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(atual, destino)
        subpastas.add(atual.parent)
        devolvidos += 1

    # Remove as subpastas que ficaram vazias. rmdir só apaga pasta vazia,
    # então nunca remove arquivos do usuário.
    for subpasta in subpastas:
        try:
            subpasta.rmdir()
        except OSError:
            pass

    # Guarda o histórico em desfeitos/, para não desfazer duas vezes.
    PASTA_DESFEITOS.mkdir(parents=True, exist_ok=True)
    shutil.move(arquivo, nome_livre(PASTA_DESFEITOS / arquivo.name))

    print(f"{devolvidos} de {len(movimentos)} arquivo(s) devolvido(s).")


def main():
    opcoes, caminhos = separar_argumentos(sys.argv[1:])

    if opcoes & OPCOES_AJUDA:
        mostrar_ajuda()
        return

    if opcoes & OPCOES_DESFAZER:
        desfazer(caminhos, simulacao=bool(opcoes & OPCOES_SIMULAR))
        return

    pasta = obter_pasta(caminhos)
    regras = carregar_regras()
    plano = montar_plano(pasta, regras)

    if not plano:
        print(f"Nenhum arquivo para organizar em {pasta}.")
        return

    if opcoes & OPCOES_SIMULAR:
        imprimir_simulacao(pasta, plano)
    else:
        executar_plano(pasta, plano)


if __name__ == "__main__":
    main()