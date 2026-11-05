# B03 · Agenda de contatos com JSON

Agenda de contatos no terminal, com menu interativo. Os contatos ficam salvos num arquivo **JSON**, então continuam lá depois que o programa fecha.

Escrita em **Python puro**, apenas com a biblioteca padrão.

> **Status:** em andamento. A validação de e-mail e de telefone (`validacao.py`) está pronta; o restante está sendo construído.

## Funcionalidades

- **Adicionar contato:** nome, telefone, e-mail e aniversário (DD/MM). Cada contato recebe um `id` único.
- **Listar:** mostra todos os contatos em ordem alfabética.
- **Buscar:** procura pelo nome, sem diferenciar maiúsculas de minúsculas e sem ligar para acentos. Buscar `jose` encontra `José`.
- **Editar:** altera um ou mais campos de um contato. Apertar Enter mantém o valor atual.
- **Remover:** apaga um contato, pedindo confirmação antes.
- **Aniversariantes do mês:** lista quem faz aniversário no mês atual, em ordem de dia.
- **Exportar CSV:** gera um `.csv` que abre no Excel ou no LibreOffice.
- **Validação:** e-mails e telefones inválidos são recusados, e o programa pede de novo.
- **Acentos preservados:** o JSON é salvo com `ensure_ascii=False`, então `José` aparece como `José` no arquivo, e não como `José`.
- **Não perde dados:** se o arquivo JSON estiver corrompido, ele é copiado para um `.bak` e a agenda abre vazia, em vez de o programa quebrar.

## Como usar

Requisito: Python 3.10 ou superior. Nenhuma instalação extra é necessária para rodar o programa.

```bash
python agenda.py
```

O programa abre um menu:

```
=== Agenda de contatos ===
1. Adicionar contato
2. Listar contatos
3. Buscar
4. Editar
5. Remover
6. Aniversariantes do mês
7. Exportar CSV
0. Sair
```

Os contatos ficam em `dados/contatos.json`. Esse arquivo é criado automaticamente na primeira vez que um contato é salvo.

## Formato dos dados

Cada contato é um dicionário, e o arquivo guarda uma lista deles:

```json
[
  {
    "id": 1,
    "nome": "José da Silva",
    "telefone": "(88) 99999-1234",
    "email": "jose.silva@email.com",
    "aniversario": "15/03"
  }
]
```

O arquivo `dados/contatos_exemplo.json` tem contatos fictícios, que servem para testar o programa sem digitar tudo.

## O que é aceito na validação

**E-mail:** uma parte local com letras, números, `.`, `_`, `+` ou `-`, depois um `@` e um domínio com pelo menos um ponto, terminando em duas ou mais letras.

| Aceito | Recusado |
|---|---|
| `ana@gmail.com` | `ana@gmail` (sem ponto no domínio) |
| `ana.souza+trabalho@mail.com` | `ana gmail.com` (sem `@`) |
| `ana@mail.meu-site.com.br` | `ana@@gmail.com` (dois `@`) |

**Telefone:** espaços e hífens são ignorados. Os parênteses só valem quando envolvem o código de área inteiro.

| Aceito | Recusado |
|---|---|
| `(88) 99999-1234` | `(88 99999-1234` (parêntese sem par) |
| `88999991234` | `99999-1234` (sem DDD) |
| `+55 (88) 99999-1234` | `88.99999.1234` (pontos) |
| `+1 (415) 555-2671` | `1 415 555 2671` (internacional sem `+`) |
| `+44 7911 123456` | `8899a-1234` (letras) |

Números internacionais precisam começar com `+` e ter de 8 a 15 dígitos, que é o limite do padrão internacional E.164. O programa confere o formato, mas não se o código do país existe.

## Como funciona

O código fica dividido em três arquivos, cada um com uma responsabilidade:

1. **Validação** (`validacao.py`): funções puras que recebem um texto e devolvem `True` ou `False`. Usam expressões regulares com `fullmatch`, que exige que o texto **inteiro** siga o padrão, e não só um pedaço dele. No telefone, a limpeza tira só os espaços e os hífens; os parênteses ficam no texto, para o próprio padrão conferir se estão no lugar certo. A função `remover_acentos` usa `unicodedata.normalize("NFD")`, que separa cada letra acentuada na letra e no acento, e depois descarta os acentos.
2. **Armazenamento** (`armazenamento.py`): `carregar` lê o JSON e devolve a lista de contatos, e `salvar` grava a lista de volta. Se a leitura falhar com `json.JSONDecodeError`, o arquivo vai para um `.bak` e a agenda começa vazia.
3. **Menu** (`agenda.py`): o laço `while True` que mostra as opções, lê a escolha e chama a função de cada operação. Toda alteração é salva logo em seguida, para não perder nada se o programa for fechado de repente.

## Testes

```bash
pip install pytest
python -m pytest
```

- `test_validacao.py`: listas de e-mails e telefones válidos e inválidos com `pytest.mark.parametrize`, e a remoção de acentos.
- `test_armazenamento.py`: salvar e carregar numa pasta temporária, acentos preservados no arquivo, arquivo que ainda não existe e arquivo corrompido gerando o `.bak`.

## Estrutura

```
b03-agenda-json/
├── README.md
├── agenda.py               ← menu e operações
├── armazenamento.py        ← carregar e salvar o JSON
├── validacao.py            ← e-mail, telefone e remover_acentos
├── test_validacao.py       ← testes da validação
├── test_armazenamento.py   ← testes do salvamento e da leitura
├── dados/
│   ├── .gitkeep            ← mantém a pasta no Git
│   └── contatos_exemplo.json
└── .gitignore              ← ignora dados/contatos.json, que tem contatos reais
```

## O que aprendi

...

## Próximos passos

...
