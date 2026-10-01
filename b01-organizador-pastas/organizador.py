import sys
import os
#python organizador.py [-h] [-s] [caminho]

def limpar_tela(esperar=True):
    """Limpa o terminal."""

    if esperar:
    	print()	
    	input('Enter para continuar...')
    os.system("cls" if os.name == "nt" else "clear")

def modo_ajuda(argumentos):
	"""Define um menu simples de terminal para tirar dúvidas de uso."""
	
	estado = True
	print(10*'-'+'Modo de ajuda!'+10*'-')
	while(estado):
		print("-----O que você deseja saber?-----")
		print("- h: O que esse programa faz?.....")
		print("- a: Argumentos desse programa?...")
		print("- v: Voltar e testar o programa...")
		print("- s: Sair do programa.............")
		opcao = input()

		if(opcao == 'h'):
			limpar_tela(esperar=False)
			print("------------------O que esse programa faz?-------------------")
			print("- Organiza os arquivos de uma pasta, movendo cada um para")
			print("uma subpasta de acordo com a sua extensão. Por exemplo:")
			print("  .jpg e .png  ->  Imagens")
			print("  .pdf e .docx ->  Documentos")
			print("- Extensões que não estão nas regras vão para a pasta Outros.")
			print()
			print("- As regras ficam no arquivo regras.json e podem ser")
			print("editadas sem mexer no código.")
			print()
			print("- Nenhum arquivo é sobrescrito: se já existir um arquivo com")
			print("o mesmo nome no destino, o novo recebe um número, como")
			print("foto (1).jpg.")
			limpar_tela()

		elif(opcao == 'a'):
			limpar_tela(esperar=False)
			print("--------------Argumentos deste programa------------")
			print("Uso: python organizador.py [-h] [-s] [caminho]")
			print()
			print("caminho:")
			print("  Caminho da pasta que será organizada. Se não for")
			print("  informado, o programa pergunta. Use aspas se o")
			print("  caminho tiver espaços.")
			print()
			print("-s:")
			print("  Mostra o que seria feito (origem -> destino),")
			print("  sem mover nenhum arquivo.")
			print()
			print("-h, -help:")
			print("  Abre este modo de ajuda.")
			print()
			print("Exemplos:")
			print("  python organizador.py C:\\Users\\tonye\\Downloads")
			print("  python organizador.py exemplo -s")
			print('  python organizador.py "C:\\Minha Pasta" -s')
			limpar_tela()

		elif(opcao == 'v'):
			# Aqui o usuário é reinserido no fluxo de funcionamento do Programa.

			limpar_tela(esperar=False)

		elif(opcao == 's'):
			limpar_tela(esperar=False)
			sys.exit(0)

		else:
			print('Escolha inválida!')
			limpar_tela()

def ler_argumentos():
	""" Lê os argumentos do terminal com sys.argv.
		Retorno: argumentos lidos.
	"""
	argumentos = sys.argv[1:]

	if '-h' or '-help' in argumentos:
		modo_ajuda(argumentos)

	return argumentos

def main():
	ler_argumentos()

if __name__ == "__main__":
    main()
