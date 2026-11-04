# B02 · Raio-X do disco

Ferramenta de linha de comando que varre uma pasta e todas as suas subpastas e mostra **onde está o espaço ocupado**: o tamanho total, os maiores arquivos, as subpastas mais pesadas e quanto cada tipo de arquivo ocupa.

Escrito em **Python puro**, apenas com a biblioteca padrão.

> **Status:** em desenvolvimento.

## Funcionalidades

- **Resumo geral:** tamanho total, número de arquivos e número de pastas.
- **Maiores arquivos:** os 10 maiores, com o caminho relativo à pasta analisada.
- **Subpastas mais pesadas:** as subpastas do primeiro nível ordenadas por tamanho, cada uma com uma barra proporcional, como `████████░░ 42%`.
- **Tamanho por extensão:** quanto espaço ocupam os `.mp4`, os `.pdf`, os `.zip` e assim por diante.
- **Espaço do disco:** total, usado e livre.
- **Tamanhos legíveis:** os bytes aparecem convertidos para B, KB, MB ou GB, com uma casa decimal.
- **Não quebra no meio:** pastas sem permissão e links quebrados são pulados e contados no final.
- **Funciona no Windows e no Linux:** todos os caminhos são montados com `pathlib`.

## Como usar

Requisito: Python 3.10 ou superior. Nenhuma instalação extra é necessária.

```
python raio_x.py [-h] [-n N] [CAMINHO]
```

| Argumento | O que faz |
|---|---|
| `CAMINHO` | Pasta a ser analisada. Se não for informada, o programa pergunta. Use aspas se tiver espaços. |
| `-n N`, `--top N` | Quantos itens mostrar nos rankings (padrão: 10). |
| `-h`, `--help` | Mostra a ajuda. |

### Exemplos

```bash
python raio_x.py C:\Users\tonye\Downloads
python raio_x.py "C:\Minha Pasta" -n 5
python raio_x.py .
```

## Exemplo de saída

```
Raio-X de: C:\Users\tonye\Downloads

Total: 12.4 GB em 1.832 arquivos e 147 pastas

Maiores arquivos
   1.  3.2 GB  videos\aula_gravada.mp4
   2.  1.1 GB  instaladores\jogo_setup.exe
   3.  842.0 MB  backups\fotos_2025.zip
   ...

Subpastas por tamanho
  videos        ████████████░░░░░░░░  6.1 GB   49%
  instaladores  ████░░░░░░░░░░░░░░░░  2.3 GB   19%
  backups       ███░░░░░░░░░░░░░░░░░  1.6 GB   13%
  ...

Tamanho por extensão
  .mp4    6.4 GB
  .exe    2.5 GB
  .zip    1.9 GB
  ...

Disco: 238.5 GB no total, 71.2 GB livres (30%)

Itens ignorados: 3 (sem permissão ou links quebrados)
```

## Como funciona

1. **Varredura:** `Path.rglob("*")` percorre a pasta e todas as subpastas. O tamanho de cada arquivo vem de `stat().st_size`.
2. **Acúmulo:** durante a varredura, os tamanhos são somados no total, por subpasta do primeiro nível e por extensão, usando dicionários.
3. **Rankings:** `sorted` com `key` ordena os arquivos, as subpastas e as extensões pelo tamanho.
4. **Formatação:** as funções de `utils.py` convertem bytes em texto legível e desenham as barras. Elas são separadas da varredura para poderem ser testadas sem tocar no disco.
5. **Disco:** `shutil.disk_usage` informa o espaço total, usado e livre.
6. **Erros:** cada acesso a arquivo fica protegido por `try/except`, e os itens que não puderam ser lidos são contados e informados no final.

## Testes

```bash
pip install pytest
python -m pytest
```

Os testes cobrem as funções de `utils.py` (conversão de bytes e barras proporcionais) e a varredura numa pasta temporária criada pelo próprio pytest.

## Estrutura

```
b02-raio-x-disco/
├── README.md
├── raio_x.py         ← varredura e relatório
├── utils.py          ← formatar_bytes e barra_proporcional
├── test_utils.py     ← testes das funções de utils.py
└── .gitignore
```

## O que aprendi

- ...

## Próximos passos

- Salvar o relatório em `relatorios/relatorio_AAAA-MM-DD.json`.
- Na próxima execução, comparar com o último relatório e mostrar quais pastas mais cresceram.