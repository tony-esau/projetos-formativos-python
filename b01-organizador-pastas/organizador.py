import sys
import os
from pathlib import Path
#python organizador.py [-h] [-s] [caminho]

TEXTO_SOBRE = """----------------- O que esse programa faz? -------------------

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

TEXTO_ARGUMENTOS = """------------ Argumentos deste programa ------------

Uso: python organizador.py [-h] [-s] [CAMINHO]

CAMINHO
  Caminho da pasta que será organizada. Se não for
  informado, o programa pergunta. Use aspas se o
  caminho tiver espaços.

-s, 
  Mostra o que seria feito (origem -> destino),
  sem mover nenhum arquivo.

-h, 
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
		caminho = input("""
			Digite o caminho. Aperte somente enter para a pasta 
			atual:
		""")
		caminho = Path(caminho)
		if(caminho.is_dir()):
			limpar_tela(esperarar=False)
			print(f"A pasta selecionada foi: {caminho.name}")
			limpar_tela()
			break
		else:
			print(
				"""
					Pasta de destino não encontrada! Digite 's' para sair do
					programa ou pressione outra tecla para tentar novamente...
				"""
			)
			opcao = input()
			if(opcao == 's'):
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

def organizar(caminho, simulacao):
	print('Chego já')

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
	print(candidatos_caminho)

	if(candidatos_caminho):
		if(len(candidatos_caminho) > 1):
			print("""
				Foram informados mais de um caminho válido para uma pasta: 
			""")
			numeros = []
			for i, caminho in enumerate(candidatos_caminho, start=1):
				print(f'Caminho {i}: {caminho}')
				numeros = numeros.append(str(i))
			while(True):
				print("""
					O que você deseja fazer:
						1: Usar um desses caminhos;
						2: informar um novo caminho;
						q: sair do programa; 
				""")
				input()
				if (opcao == '1'):
					numero = input('Digite o número do caminho:')
					if (numero in numeros):
						organizar(candidatos_caminho[numero-1], simulacao)
						break

				elif (opcao == '2'):
					caminho = ler_caminho()
					organizar(caminho, simulacao)
					break

				elif (opcao == 'q'):
					limpar_tela()
					sys.exit(0)

				print("Opção inválida! Tente novamente...")
				limpar_tela()
		else:
			organizar(candidatos_caminho[0],simulacao)

	else:
		while(True):
			opcao = input("Deseja informar a pasta (s) ou sair do programa (q)?")
			if (opcao == 'q'):
				limpar_tela(esperar=False)
				sys.exit(0)
			elif (opcao == 's'):
				limpar_tela()
				caminho = ler_caminho()
				organizar(caminho, simulacao)
				break
		
		print("Opção inválida! Tente novamente...")
		limpar_tela()

def main():
	organizador()

if __name__ == "__main__":
    main()
