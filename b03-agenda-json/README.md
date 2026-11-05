# B03 · Agenda de contatos com JSON

Agenda de contatos no terminal, com menu interativo. Os contatos ficam salvos num arquivo **JSON**, então continuam persistentes mesmo que o programa feche.

Escrita em **Python puro**, apenas com bibliotecas padrão.

## Funcionalidades

- **Adicionar:** nome e telefone obrigatórios; e-mail e aniversário (DD/MM) opcionais. Cada contato recebe um `id` único, que nunca é reaproveitado depois de uma remoção.
- **Listar:** todos os contatos em ordem alfabética, em colunas alinhadas. A ordem ignora acentos e maiúsculas, então `Álvaro` e `ana` ficam junto dos outros nomes com A.
- **Buscar:** por um pedaço do nome, sem ligar para acentos nem maiúsculas. `jose` encontra `José da Silva` e `Maria José Souza`.
- **Editar:** o contato é escolhido pelo nome ou pelo id. Se o nome bater com mais de um contato, eles aparecem numa tabela e você escolhe pelo id de um dos mostrados. Cada campo mostra o valor atual, e Enter vazio mantém o valor.
- **Remover:** escolhe o contato do mesmo jeito da edição e pede confirmação antes de apagar.
- **Aniversariantes do mês:** quem faz aniversário no mês atual, em ordem de dia, marcando quem faz hoje e de quem já passou.
- **Exportar CSV:** gera `dados/contatos_AAAA-MM-DD.csv`, que abre no Excel e no LibreOffice com as colunas separadas e os acentos certos.
- **Validação:** nome vazio, e-mail ou telefone inválido e datas que não existem, como `31/04`, são recusados, e o programa pergunta de novo.
- **Telefone padronizado:** o mesmo número digitado de jeitos diferentes é guardado de uma única forma e aparece sempre formatado na tela.
- **Acentos preservados:** o JSON é salvo com `ensure_ascii=False`, então o arquivo mostra `José`, e não `Jos\u00e9`.
- **Não perde dados:** se o JSON estiver corrompido, ele é copiado para um `.bak` e a agenda abre vazia, em vez de o programa quebrar.
- **Telas limpas:** a tela é limpa a cada troca, cada opção abre com o seu título, e o programa espera o Enter antes de voltar ao menu.

## Como usar

Requisito: Python 3.10 ou superior. Nenhuma instalação extra é necessária para rodar o programa.

```bash
python agenda.py
```

Os contatos ficam em `dados/contatos.json`, criado automaticamente no primeiro contato salvo.

Para testar com contatos fictícios, copie o arquivo de exemplo antes de rodar:

```bash
copy dados\contatos_exemplo.json dados\contatos.json     # Windows
cp dados/contatos_exemplo.json dados/contatos.json       # Linux
```

## Exemplo de saída

Saída real do programa com os contatos de exemplo, rodado em 5 de novembro.

O menu:

```
┌──────────────────────────────────────┐
│          AGENDA DE CONTATOS          │
│        9 contato(s) salvo(s)         │
├──────────────────────────────────────┤
│  1  Adicionar contato                │
│  2  Listar contatos                  │
│  3  Buscar                           │
│  4  Editar                           │
│  5  Remover                          │
│  6  Aniversariantes do mês           │
│  7  Exportar CSV                     │
├──────────────────────────────────────┤
│  0  Sair                             │
└──────────────────────────────────────┘
Escolha: 2
```

A listagem:

```
LISTAR CONTATOS
───────────────

 Id  Nome                  Telefone              Aniv.  E-mail
  3  Álvaro Bezerra        +55 (85) 98888-7777   22/11  -
  4  ana lima              +55 (11) 91234-5678   02/11  ana.lima+trabalho@exemplo.com.br
  5  Conceição Araújo      +55 (88) 98111-2222   -      conceicao@exemplo.com
  8  Émile Durand          +33612345678          14/07  emile.durand@exemplo.fr
  7  João Pedro Gonçalves  +55 (83) 99999-0000   29/02  joao_pedro@exemplo.com
  1  José da Silva         +55 (88) 99999-1234   15/03  jose.silva@exemplo.com
  2  Maria José Souza      +55 (88) 3521-1234    08/11  maria.souza@exemplo.com
  9  Michael Brown         +14155552671          31/12  -
 10  Zuleide Ferreira      +55 (88) 3511-0000    01/01  zuleide.ferreira@exemplo.com

9 contato(s).

Pressione Enter para voltar ao menu...
```

A busca:

```
BUSCAR
──────
Buscar por nome: jose

 Id  Nome              Telefone              Aniv.  E-mail
  1  José da Silva     +55 (88) 99999-1234   15/03  jose.silva@exemplo.com
  2  Maria José Souza  +55 (88) 3521-1234    08/11  maria.souza@exemplo.com

2 contato(s) encontrado(s).

Pressione Enter para voltar ao menu...
```

Os aniversariantes:

```
ANIVERSARIANTES DO MÊS
──────────────────────

Aniversariantes de novembro:
  02/11  ana lima          +55 (11) 91234-5678   (já passou)
  08/11  Maria José Souza  +55 (88) 3521-1234
  22/11  Álvaro Bezerra    +55 (85) 98888-7777

Pressione Enter para voltar ao menu...
```

## Formato dos dados

O arquivo guarda uma lista de contatos, e cada contato é um dicionário:

```json
[
  {
    "id": 1,
    "nome": "José da Silva",
    "telefone": "+5588999991234",
    "email": "jose.silva@exemplo.com",
    "aniversario": "15/03"
  }
]
```

O telefone é guardado só com o `+` e os dígitos (padrão E.164) e aparece formatado na tela. Campos opcionais que não foram preenchidos ficam como `""`.

## O que é aceito na validação

**E-mail:** uma parte local com letras, números, `.`, `_`, `+` ou `-`, depois um `@` e um domínio com pelo menos um ponto, terminando em duas ou mais letras.

| Aceito | Recusado |
|---|---|
| `ana@gmail.com` | `ana@gmail` (sem ponto no domínio) |
| `ana.souza+trabalho@mail.com` | `ana gmail.com` (sem `@`) |
| `ana@mail.meu-site.com.br` | `ana@@gmail.com` (dois `@`) |

**Telefone:** espaços e hífens são ignorados. Os parênteses só valem quando envolvem o código de área inteiro. Números internacionais precisam começar com `+` e ter de 8 a 15 dígitos, o limite do padrão E.164. O programa confere o formato, mas não se o código do país existe.

| Aceito | Recusado |
|---|---|
| `(88) 99999-1234` | `(88 99999-1234` (parêntese sem par) |
| `88999991234` | `99999-1234` (sem DDD) |
| `+55 (88) 99999-1234` | `88.99999.1234` (pontos) |
| `+1 (415) 555-2671` | `1 415 555 2671` (internacional sem `+`) |
| `+44 7911 123456` | `8899a-1234` (letras) |

**Aniversário:** formato `DD/MM` e uma data que existe. `29/02` é aceito; `31/04`, `30/02` e `15-03` não.

## Como funciona

O código é dividido em quatro arquivos, cada um com uma responsabilidade.

### `validacao.py`: o texto está certo?

Funções que recebem um texto e devolvem `True` ou `False`.

- `validar_email` e `validar_telefone` usam expressões regulares com `fullmatch`, que exige que o texto **inteiro** siga o padrão, e não só um pedaço dele.
- No telefone, a limpeza tira só os espaços e os hífens. Os parênteses ficam no texto, e o próprio padrão confere se eles estão no lugar certo.
- `validar_aniversario` confere o formato com um regex e depois usa o `datetime.strptime` para recusar datas que não existem.

### `formatacao.py`: transformar o texto

- `normalizar_telefone` deixa o telefone num formato único antes de salvar: tira tudo o que não é dígito e coloca o `+55` quando o número é brasileiro e veio sem ele.
- `formatar_telefone` faz o caminho de volta, só para mostrar: `+5588999991234` vira `+55 (88) 99999-1234`.
- `remover_acentos` usa `unicodedata.normalize("NFD")`, que separa cada letra acentuada na letra e no acento, e depois descarta os acentos.

### `armazenamento.py`: ler e gravar arquivos

- `carregar` lê o JSON e devolve a lista de contatos. Se o arquivo não existe, devolve uma lista vazia. Se está corrompido, ou se o conteúdo não é uma lista, chama `fazer_backup`, que copia o arquivo para um `.bak` com data e hora no nome, e também devolve uma lista vazia.
- `salvar` grava a lista de volta, com `ensure_ascii=False` e `indent=2`.
- `gravar_csv` usa o `csv.DictWriter` com `;` como separador e a codificação `utf-8-sig`, que é o que o Excel em português precisa para abrir o arquivo direito.
- O caminho padrão é montado a partir de `Path(__file__).parent`, a pasta do próprio script, então o programa encontra os dados de onde quer que seja rodado.

### `agenda.py`: o menu

- O `main` repete o menu num `while True`. As opções ficam no dicionário `OPCOES`, que liga cada número ao título e à função da opção. O menu é desenhado a partir dele, e a escolha vira `funcao(contatos)`.
- `limpar_tela` usa `subprocess.run` com `cls` no Windows e `clear` no Linux, conforme o `os.name`. `pausar` espera o Enter antes de voltar ao menu.
- Funções auxiliares usadas por várias opções:
  - `perguntar` repete uma pergunta enquanto a resposta for inválida. Ela recebe a função de validação como parâmetro, então serve para todos os campos.
  - `chave_nome` devolve o nome sem acentos e em minúsculas. A listagem usa para ordenar, e a busca usa para comparar.
  - `escolher_contato` aceita um nome ou um id e é usada pela edição e pela remoção.
  - `mostrar_contatos` desenha a tabela usada pela listagem, pela busca e pela escolha de contatos.
- Toda alteração é salva logo em seguida, para não perder nada se o programa for fechado de repente.

## Testes

```bash
pip install pytest
python -m pytest
```

São 130 testes em quatro arquivos:

- `test_validacao.py`: e-mails, telefones e aniversários válidos e inválidos com `pytest.mark.parametrize`, incluindo parênteses fora do lugar e datas que não existem.
- `test_formatacao.py`: formas diferentes de digitar o mesmo número virando um só formato guardado, normalizar duas vezes sem mudar nada, a formatação para a tela e a remoção de acentos.
- `test_armazenamento.py`: salvar e carregar numa pasta temporária, acentos legíveis no arquivo, arquivo que ainda não existe, quatro tipos de arquivo corrompido gerando o `.bak` e o CSV com o separador e a codificação certos.
- `test_agenda.py`: o próximo id depois de remoções, a ordem alfabética com acentos, a busca por pedaço do nome e a procura por id.

## Estrutura

```
b03-agenda-json/
├── README.md
├── agenda.py               ← menu e operações
├── armazenamento.py        ← ler e gravar o JSON, exportar CSV
├── formatacao.py           ← normalizar e formatar telefone, remover acentos
├── validacao.py            ← validar e-mail, telefone e aniversário
├── test_agenda.py          ← testes das funções auxiliares do menu
├── test_armazenamento.py   ← testes da leitura, da gravação e do CSV
├── test_formatacao.py      ← testes da formatação
├── test_validacao.py       ← testes da validação
├── dados/
│   ├── .gitkeep            ← mantém a pasta no Git
│   └── contatos_exemplo.json
└── .gitignore              ← ignora contatos.json, backups e CSVs
```

## O que aprendi

- Escrever expressões regulares com classes de caracteres, quantificadores, grupos e o `|`, e entender por que a validação precisa do `fullmatch` e não do `search`.
- Que strings são imutáveis: o `re.sub` devolve uma string nova, que precisa ser guardada numa variável.
- Separar três trabalhos diferentes: validar (sim ou não), normalizar (guardar num formato único) e formatar (mostrar de um jeito legível).
- Ler e gravar JSON mantendo os acentos, e tratar arquivos corrompidos sem perder os dados originais.
- Remover acentos com `unicodedata` e usar a mesma função como `key` do `sorted` e na comparação da busca.
- Passar uma função como parâmetro de outra, guardar funções como valores de um dicionário e escrever funções curtas com `lambda`.
- Que dicionários dentro de uma lista são passados por referência: editar o contato escolhido já altera a lista.
- Gerar CSV que o Excel em português abre corretamente.
