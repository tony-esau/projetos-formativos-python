# B01 · Organizador de pastas

Ferramenta de linha de comando que organiza uma pasta bagunçada (como Downloads), movendo cada arquivo para uma subpasta de acordo com a extensão: imagens para `Imagens`, PDFs para `Documentos`, e assim por diante.

Escrito em **Python puro**, apenas com a biblioteca padrão.

## Funcionalidades

- **Regras editáveis:** as extensões de cada pasta ficam no `regras.json`, e mudar as regras não exige mexer no código.
- **Modo simulação (`-s`):** mostra em formato de árvore como a pasta ficaria, sem mover nada.
- **Nada é sobrescrito:** se já existir um arquivo com o mesmo nome no destino, o novo recebe um número, como `foto (1).jpg`.
- **Desfazer (`-d`):** cada organização gera um histórico, e a última pode ser desfeita, devolvendo os arquivos aos lugares originais.
- **Extensões sem regra** vão para a pasta `Outros`. Extensões em maiúsculas (`.JPG`) são tratadas como minúsculas.
- **Subpastas são ignoradas:** só os arquivos do primeiro nível são organizados.
- **Funciona no Windows e no Linux:** todos os caminhos são montados com `pathlib`.

## Como usar

Requisito: Python 3.10 ou superior. Nenhuma instalação extra é necessária.

```
python organizador.py [-h] [-s] [-d] [CAMINHO]
```

| Argumento | O que faz |
|---|---|
| `CAMINHO` | Pasta a ser organizada. Se não for informada, o programa pergunta. Use aspas se tiver espaços. |
| `-s`, `--simular` | Mostra o que seria feito, sem mover nenhum arquivo. |
| `-d`, `--desfazer` | Desfaz a última organização. Com `CAMINHO`, desfaz a última daquela pasta. Pode ser combinada com `-s`. |
| `-h`, `--help` | Mostra a ajuda. |

### Exemplos

```bash
python organizador.py C:\Users\tonye\Downloads -s     # simula
python organizador.py C:\Users\tonye\Downloads        # organiza
python organizador.py --desfazer                      # desfaz a última organização
python organizador.py "C:\Minha Pasta" -d -s          # mostra o que seria desfeito
```

### Testando com segurança

O script `gerar_exemplo.py` cria uma pasta `exemplo/` com 34 arquivos vazios de tipos variados, incluindo os casos difíceis: extensões em maiúsculas, arquivos sem extensão, nomes com espaços e acentos, subpastas que devem ser ignoradas e um nome repetido.

```bash
python gerar_exemplo.py
python organizador.py exemplo -s
python organizador.py exemplo
python organizador.py exemplo -d
```

## Exemplo de saída

```
[SIMULAÇÃO] Nenhum arquivo será movido.

C:\Users\tonye\exemplo/
├── Imagens/
│   ├── foto_praia.jpg
│   ├── FOTO_FESTA.JPG
│   └── logo.png
├── Documentos/
│   ├── curriculo.pdf
│   ├── relatório final.pdf
│   └── anotacoes.txt
├── Compactados/
│   ├── projeto.tar.gz
│   └── backup.zip
└── Outros/
    ├── LEIA-ME
    └── arquivo_estranho.xyz

Total: 10 arquivo(s) em 4 pasta(s) distintas.
```

## Como funciona

O programa segue um fluxo linear, em que cada etapa é uma função:

```
argumentos ──► pasta ──► regras ──► plano ──► simular ou executar
```

1. **`separar_argumentos`** separa as opções (que começam com `-`) dos caminhos e recusa opções desconhecidas, para que um erro de digitação como `--simulr` não mova arquivos sem querer.
2. **`obter_pasta`** valida a pasta: pergunta se nenhuma foi informada e recusa caminhos inexistentes ou mais de um caminho.
3. **`carregar_regras`** lê o `regras.json` da pasta do script, com mensagens claras se o arquivo faltar ou estiver malformado.
4. **`montar_plano`** decide, **sem mover nada**, para qual subpasta vai cada arquivo. O resultado é uma lista de pares (arquivo, subpasta).
5. O mesmo plano é usado por **`imprimir_simulacao`** e por **`executar_plano`**. Assim, a simulação mostra exatamente o que a execução faria.

Na execução, cada movimento é registrado e salvo em `historicos/` dentro de um `try/finally`, para que o histórico seja gravado mesmo se algo falhar no meio. O desfazer percorre os movimentos em ordem inversa e move o histórico usado para `historicos/desfeitos/`, para não desfazer a mesma operação duas vezes.

## Estrutura

```
b01-organizador-pastas/
├── README.md
├── organizador.py      ← programa principal
├── regras.json         ← mapeamento pasta → extensões
├── gerar_exemplo.py    ← cria a pasta de testes
└── .gitignore          ← ignora exemplo/, historicos/ e __pycache__/
```