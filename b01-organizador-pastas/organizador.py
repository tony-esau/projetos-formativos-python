import sys
import os
from pathlib import Path
import json
from collections import defaultdict
import shutil

# python organizador.py [-h] [-s] [caminho]

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
  foto (1).jpg."""

TEXTO_ARGUMENTOS = """------------ Argumentos deste programa -------------

Uso: python organizador.py [-h] [-s] [CAMINHO]

CAMINHO
  Caminho da pasta que será organizada. Se não for
  informado, o programa pergunta. Use aspas se o
  caminho tiver espaços.

-s
  Mostra o que seria feito (origem -> destino),
  sem mover nenhum arquivo.

-h, -help
  Abre este modo de ajuda.

Exemplos:
  python organizador.py C:\\Users\\joao\\Downloads
  python organizador.py exemplo -s
  python organizador.py "C:\\Minha Pasta" --simular"""

MENU_AJUDA = """------ O que você deseja saber? ------
-h: O que esse programa faz?..........
-a: Argumentos desse programa.........
-v: Voltar e testar o programa........
-q: Sair do programa.................."""

def limpar_tela(esperar=True):
    """Limpa o terminal."""

    if esperar:
    	print()	
    	input('Enter para continuar...')
    os.system("cls" if os.name == "nt" else "clear")

def ler_caminho():
	""" Função para o caso em que o usuário não repassou o caminho.
		Retorno: caminho da pasta.
	"""

	while(True):
		caminho = input(
			"Digite o caminho (ou só Enter para a pasta atual): ")
		caminho = Path(caminho)
		if(caminho.is_dir()):
			limpar_tela(esperar=False)
			print(f"A pasta selecionada foi: {Path.cwd().name}")
			limpar_tela()
			break
		else:
			print("Pasta não encontrada!")
			print("Digite 'q' para sair do programa ou pressione Enter "
				  "para tentar novamente.")
			opcao = input()
			if(opcao == 'q'):
				limpar_tela(esperar=False)
				sys.exit(0)
			else: 
				continue
	return caminho

def modo_ajuda():
    """Mostra um menu de terminal para tirar dúvidas de uso."""
    limpar_tela(esperar=False)
    print("-" * 11 + " Menu de ajuda! " + "-" * 11)

    while True:
        print(MENU_AJUDA)
        opcao = input("Opção: ").strip().lower()

        if opcao == "h":
            limpar_tela(esperar=False)
            print(TEXTO_SOBRE)
            limpar_tela()

        elif opcao == "a":
            limpar_tela(esperar=False)
            print(TEXTO_ARGUMENTOS)
            limpar_tela()

        elif opcao == "v":
            limpar_tela(esperar=False)
            return

        elif opcao == "q":
       		limpar_tela(esperar=False)
       		sys.exit(0)

        else:
            print("Escolha inválida!")
            limpar_tela()

def ler_argumentos():
	""" Lê os argumentos do terminal com sys.argv.
		Retorno: argumentos lidos.
	"""
	argumentos = sys.argv[1:]

	return argumentos

def imprimir_simulacao(impressao):
    """Mostra em formato de árvore como a pasta ficaria após organizar."""

    print(f"{Path.cwd()}/") # Pasta atual.

    pastas = list(impressao.items())
    for i, (pasta, arquivos) in enumerate(pastas):
        ultima_pasta = i == len(pastas) - 1
        print(("└── " if ultima_pasta else "├── ") + f"{pasta}/")

        recuo = "    " if ultima_pasta else "│   "
        for j, arquivo in enumerate(arquivos):
            ultimo_arquivo = j == len(arquivos) - 1
            ponta = "└── " if ultimo_arquivo else "├── "
            print(recuo + ponta + arquivo)

    total = sum(len(arquivos) for arquivos in impressao.values())
    print(f"\nTotal: {total} arquivo(s) em {len(pastas)} pasta(s) distintas.")


def nome_livre(destino):
    """Devolve um caminho que ainda não existe, numerando se preciso.

    Exemplo: se foto.jpg já existe, tenta foto (1).jpg, foto (2).jpg...
    """
    if not destino.exists():
        return destino

    numero = 1
    while True:
        candidato = destino.with_name(f"{destino.stem} ({numero}){destino.suffix}")
        if not candidato.exists():
            return candidato
        numero += 1

def organizar(caminho, simulacao):
	"""
		Lê o arquivo de regras .json e decide:
			- Se simulacao = False, reorganiza o pasta do caminho.
			- Senão apenas constrói uma simulação que será impressa.
	"""

	caminho = Path(caminho) 

	texto = Path("regras.json").read_text(encoding="utf-8") # Lido como string.
	regras = json.loads(texto) #.loads() recebe uma string.
	
	arquivos = [item for item in caminho.iterdir() if item.is_file()]

	if (simulacao):
		# Todo append já começa com uma coleção vazia.
		impressao = defaultdict(list)
		for arquivo in arquivos:
			associou = False 
			for chave in regras.keys():
				# .suffix devolve uma string após o último ponto.
				if(arquivo.suffix.lower() in regras[chave]):
					impressao[chave].append(arquivo.name)
					associou = True
					break
			if (associou == False):
				impressao['outros'].append(arquivo.name)

		imprimir_simulacao(impressao)
	else:
	    for arquivo in arquivos:
	        associou = False
	        for chave in regras.keys():
	            # .suffix devolve uma string após o último ponto.
	            if arquivo.suffix.lower() in regras[chave]:
	                subpasta = caminho / chave
	                subpasta.mkdir(exist_ok=True)
	                destino = nome_livre(subpasta / arquivo.name)
	                shutil.move(arquivo, destino)
	                associou = True
	                break

	        if not associou:
	            subpasta = caminho / "Outros"
	            subpasta.mkdir(exist_ok=True)
	            destino = nome_livre(subpasta / arquivo.name)
	            shutil.move(arquivo, destino)
	    

def organizador():
	"""Fluxo principal do programa: organizador dos arquivos."""

	argumentos = ler_argumentos()
	if '-h' in argumentos or '-help' in argumentos:
		modo_ajuda()

	simulacao = False
	if '-s' in argumentos:
		simulacao = True 

	candidatos_caminho = [  
		valor for valor in argumentos if not valor.startswith("-") 
		and Path(valor).is_dir()
	]

	if(candidatos_caminho):
		if(len(candidatos_caminho) > 1):
			print("Foram informados mais de um caminho válido:")
			numeros = []
			while(True):
				for i, caminho in enumerate(candidatos_caminho, start=1):
					print(f'Caminho {i}: {caminho}')
					numeros.append(str(i))

				print()
				print("O que você deseja fazer?")
				print("  1: Usar um desses caminhos;")
				print("  2: Informar um novo caminho;")
				print("  q: Sair do programa.")
				opcao = input("Opção: ")

				if (opcao == '1'):
					numero = input('Digite o número do caminho: ')
					if (numero in numeros):
						organizar(candidatos_caminho[int(numero)-1], simulacao)
						limpar_tela()
						break

				elif (opcao == '2'):
					caminho = ler_caminho()
					limpar_tela(esperar=False)
					organizar(caminho, simulacao)
					break

				elif (opcao == 'q'):
					limpar_tela(esperar=False)
					sys.exit(0)

				print("Opção inválida! Tente novamente...")
				limpar_tela()
		else:
			organizar(candidatos_caminho[0],simulacao)

	else:
		while(True):
			opcao = input(
				"Deseja informar a pasta (s) ou sair do programa (q)? ")
			if (opcao == 'q'):
				limpar_tela(esperar=False)
				sys.exit(0)
			elif (opcao == 's'):
				limpar_tela(esperar=False)
				caminho = ler_caminho()
				organizar(caminho, simulacao)
				break
		
		print("Opção inválida! Tente novamente...")
		limpar_tela()

def main():
	organizador()

if __name__ == "__main__":
    main()