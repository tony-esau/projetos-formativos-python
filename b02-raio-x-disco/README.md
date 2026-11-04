# B02 · Raio-X do disco

Ferramenta de linha de comando que varre uma pasta e todas as suas subpastas e mostra **onde está o espaço ocupado**: o tamanho total, os maiores arquivos, as subpastas mais pesadas e quanto cada tipo de arquivo ocupa.

Escrito em **Python puro**.

## Funcionalidades

- **Resumo geral:** tamanho total, número de arquivos e número de pastas.
- **Maiores arquivos:** os 10 maiores (ou quantos você pedir com `-n`), com o caminho relativo à pasta analisada.
- **Subpastas mais pesadas:** as subpastas do primeiro nível ordenadas por tamanho, com barra proporcional e porcentagem do total. Arquivos soltos na pasta analisada aparecem agrupados como `(arquivos na raiz)`.
- **Tamanho por extensão:** quanto espaço ocupam os `.mp4`, os `.pdf`, os `.zip` e assim por diante. `.JPG` e `.jpg` são somados juntos, e arquivos sem extensão aparecem como `(sem extensão)`.
- **Espaço do disco:** total, usado e livre.
- **Histórico (`-s`):** salva um resumo da análise em JSON. Nas próximas análises da mesma pasta, mostra o que mudou: variação do total e as subpastas que mais cresceram e diminuíram.
- **Tamanhos legíveis:** os bytes aparecem convertidos para B, KB, MB, GB ou TB, com uma casa decimal.
- **Não quebra no meio:** pastas sem permissão, links quebrados e arquivos que não podem ser lidos são pulados, e o relatório informa no final quantos foram e quais pastas ficaram de fora.
- **Funciona no Windows e no Linux:** todos os caminhos são montados com `pathlib`.

## Como usar

Requisito: Python 3.10 ou superior. Nenhuma instalação extra é necessária para rodar o programa.

```
python raio_x.py [-h] [-n N] [-s] [CAMINHO]
```

| Argumento | O que faz |
|---|---|
| `CAMINHO` | Pasta a ser analisada. Se não for informada, o programa pergunta. Use aspas se tiver espaços. |
| `-n N`, `--top N` | Quantos itens mostrar em cada ranking (padrão: 10). |
| `-s`, `--salvar` | Salva um resumo da análise em `relatorios/`. Se já houver um relatório salvo da mesma pasta, a comparação aparece com ou sem esta opção. |
| `-h`, `--help` | Mostra a ajuda. |

### Exemplos

```bash
python raio_x.py C:\Users\tonye\Downloads
python raio_x.py "C:\Minha Pasta" -n 5
python raio_x.py C:\Users\tonye\Downloads -s     # salva para comparar depois
python raio_x.py .
```

## Exemplo de saída

Saída numa pasta de teste (o caminho foi adaptado para o Windows, e os trechos da comparação e dos ignorados são ilustrativos):

```
Raio-X de: C:\Users\tonye\Downloads

Total: 5.8 GB em 10 arquivo(s) e 5 pasta(s)

Maiores arquivos
   1.     3.2 GB  videos\aulas\aula_gravada.mp4
   2.     1.1 GB  instaladores\jogo_setup.exe
   3.   839.2 MB  backups\fotos_2025.zip
   4.   610.4 MB  videos\trailer.mkv
   5.    90.6 MB  instaladores\python-3.12.exe
   ...

Subpastas por tamanho
  videos              █████████████░░░░░░░     3.8 GB   64.9%
  instaladores        ████░░░░░░░░░░░░░░░░     1.2 GB   20.8%
  backups             ███░░░░░░░░░░░░░░░░░   839.2 MB   14.1%
  documentos          ░░░░░░░░░░░░░░░░░░░░     6.0 MB    0.1%
  (arquivos na raiz)  ░░░░░░░░░░░░░░░░░░░░   463.9 KB    0.0%

Tamanho por extensão
  .mp4            ███████████░░░░░░░░░     3.2 GB   54.6%
  .exe            ████░░░░░░░░░░░░░░░░     1.2 GB   20.8%
  .zip            ███░░░░░░░░░░░░░░░░░   839.2 MB   14.1%
  .mkv            ██░░░░░░░░░░░░░░░░░░   610.4 MB   10.3%
  .pdf            ░░░░░░░░░░░░░░░░░░░░     4.0 MB    0.1%
  ...

Disco: ... no total, ... usados, ... livres (...%)

Desde a última análise (2026-11-01 09:12:40)
  Total: 5.5 GB -> 5.8 GB (+300.0 MB)
  Arquivos: 9 -> 10
  Subpastas que mais cresceram:
    videos        +610.4 MB
  Subpastas que mais diminuíram:
    instaladores  -310.0 MB

Ignorados na contagem:
  - 1 pasta(s) sem permissão de leitura
  - 1 link(s) quebrado(s)
      C:\Users\tonye\Downloads\pasta_protegida
```

## Como funciona

O programa segue um fluxo linear, dividido em quatro arquivos:

```
argumentos ──► pasta ──► varredura ──► relatório ──► comparação e salvamento
```

1. **Argumentos e pasta** (`raio_x.py`): separa as opções dos caminhos, recusa opções desconhecidas e valida a pasta, perguntando se nenhuma for informada. O `-n` é tratado à parte: a lista de argumentos é percorrida com um índice, porque o item seguinte ao `-n` é o número dele, e não um caminho.
2. **Varredura** (`raio_x.py`, função `varrer`): `os.walk` percorre a pasta e todas as subpastas **uma única vez**. Ele foi escolhido em vez do `Path.rglob` porque avisa, pelo parâmetro `onerror`, quando não consegue abrir uma pasta, enquanto o `rglob` pula em silêncio. Em cada arquivo, o tamanho vem de `stat().st_size` e é somado no total, na subpasta do primeiro nível (descoberta com `relative_to(...).parts[0]`) e na extensão, usando `defaultdict(int)`. Tudo fica num dicionário que o relatório usa.
3. **Relatório** (`relatorio.py`): cada seção é uma função `imprimir_*`. As seções de subpastas e de extensões compartilham a mesma função, `imprimir_ranking`, que ordena com `sorted` e `key`, alinha as colunas e desenha as barras.
4. **Formatação** (`utils.py`): `formatar_bytes` e `barra_proporcional` são funções puras, separadas para poderem ser testadas sem tocar no disco.
5. **Histórico** (`historico.py`): o resultado da varredura vira um resumo (totais e somas por subpasta e por extensão, sem a lista de arquivos) que é salvo em `relatorios/relatorio_AAAA-MM-DD_HHMMSS.json`. Antes de salvar, o programa carrega o relatório mais recente da mesma pasta e calcula, com a união dos nomes dos dois relatórios, quanto cada subpasta cresceu ou diminuiu. Pastas novas contam como crescimento e pastas apagadas como redução.
6. **Erros:** pastas que o `os.walk` não consegue abrir são registradas pelo `onerror`, links quebrados são detectados com `is_symlink()` e `exists()`, e a leitura de cada arquivo fica protegida por `try/except OSError`. Tudo isso é contado e informado no final.

## Testes

```bash
pip install pytest
python -m pytest
```

São 72 testes em três arquivos:

- `test_utils.py`: conversão de bytes (incluindo as fronteiras entre unidades), variações com sinal e barras proporcionais (incluindo arredondamento, valores fora da faixa e a garantia de que a barra tem sempre a mesma largura).
- `test_raio_x.py`: a varredura numa pasta temporária com arquivos de tamanho exato, conferindo total, contagens, soma por subpasta, soma por extensão e casos extremos, como pasta vazia. Também cobre links quebrados, pastas sem permissão (simuladas com `monkeypatch`), o rodapé e as opções `-n` e `-s`.
- `test_historico.py`: cálculo das variações, salvamento sem sobrescrever, escolha do relatório mais recente da mesma pasta, arquivos corrompidos e a impressão da comparação.

## Estrutura

```
b02-raio-x-disco/
├── README.md
├── raio_x.py         ← argumentos, pasta, varredura e main
├── relatorio.py      ← funções que imprimem cada seção
├── historico.py      ← salvar relatórios em JSON e comparar
├── utils.py          ← formatar_bytes, formatar_variacao e barra_proporcional
├── test_utils.py     ← testes das funções de utils.py
├── test_raio_x.py    ← testes da varredura, do rodapé e das opções
├── test_historico.py ← testes do salvamento e da comparação
└── .gitignore        ← ignora relatorios/, que tem caminhos do seu computador
```

## O que aprendi

- Percorrer pastas recursivamente com `rglob` e ler metadados de arquivos com `stat()`.
- Acumular valores por categoria com `defaultdict(int)`, numa única passada pelos dados.
- Ordenar listas de tuplas e dicionários com `sorted`, `key` e `reverse`, e entender como tuplas são comparadas elemento por elemento.
- Usar `relative_to` e `parts` para descobrir em qual subpasta um arquivo está.
- Separar o código em módulos por responsabilidade: varredura, relatório e funções utilitárias puras.
- Escrever testes com `pytest.mark.parametrize` e montar pastas de teste com arquivos de tamanho exato usando `write_bytes`.
- Tratar opções que recebem um valor (`-n 5`) percorrendo os argumentos com um índice.
- Trocar `rglob` por `os.walk` para conseguir saber quais pastas não puderam ser abertas, e simular erros nos testes com `monkeypatch`.
- Guardar resultados em JSON e compará-los entre execuções, usando a união de conjuntos para não perder pastas que surgiram ou sumiram.
