# B01 · Organizador de pastas

Organiza uma pasta movendo cada arquivo para uma subpasta conforme a extensão.

**Status**: em andamento ⏳.

**Objetivo**: Organizar uma pasta bagunçada (como Downloads) movendo cada arquivo para uma subpasta de acordo com a extensão: imagens para Imagens, PDFs para Documentos, e assim por diante.

**Conceitos praticados**: `pathlib.Path`, `shutil.move`, `sys.argv`, dicionários, leitura de JSON, modo simulação antes de qualquer operação que altera arquivos.

**Especificações:**
- Receber o caminho da pasta pela linha de comando: *python* `organizador.py ~/Downloads`. Se o caminho não for informado, perguntar com `input`;
- Ler as regras de `regras.json`, que mapeia o nome da subpasta para uma lista de extensões, por exemplo `{"Imagens": [".jpg", ".png"], "Documentos": [".pdf", ".docx"]}`;
- Listar apenas os arquivos do primeiro nível da pasta, sem entrar nas subpastas;
- Para cada arquivo, descobrir a subpasta de destino. Extensões que não estão nas regras vão para *Outros*;
- Criar a subpasta se ela não existir e mover o arquivo;
- Se já existir um arquivo com o mesmo nome no destino, renomear para nome `(1).ext`, `nome (2).ext` e assim por diante, nunca sobrescrevendo;
- Implementar a opção `--simular`, que só imprime origem -> destino e não move nada;
- Ao final, imprimir um resumo com quantos arquivos foram para cada subpasta;
- Escrever gerar_exemplo.py, que cria uma pasta exemplo/ com uns 30 arquivos vazios de tipos variados;
- Registrar cada movimento em `historico.json` e criar a opção desfazer, que devolve os arquivos movidos na última execução para o lugar original.

