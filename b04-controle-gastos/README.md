# B04 · Controle de gastos com CSV e relatório

Controle de receitas e despesas no terminal. Os lançamentos ficam num arquivo **CSV**, e o programa gera um relatório mensal com totais, gráfico de despesas por categoria e comparação com o orçamento, mostrado na tela e salvo em arquivo de texto.

Escrito em **Python puro**, apenas com bibliotecas padrão.

## Funcionalidades

- **Lançamentos** com data (Enter usa a de hoje), tipo, valor, categoria e descrição. Valores aceitam vírgula ou ponto (`12,50` ou `12.50`).
- **Lançamentos do mês**, em ordem de data e com o saldo.
- **Relatório do mês**: receitas, despesas, saldo, despesas por categoria com porcentagem e gráfico de barras, maior despesa e orçamento. O mesmo texto é salvo em `relatorios/relatorio_AAAA-MM.txt`.
- **Importar CSV** de outro arquivo: as linhas válidas entram e as inválidas são puladas, com o número da linha e o motivo.
- **Categorias e orçamento** editáveis pelo menu, com um limite mensal opcional para cada categoria de despesa.
- **Validação com mensagem clara**: datas que não existem (31/02), valores com letras, negativos ou zero são recusados, e o programa pergunta de novo.
- **Contas exatas** com `Decimal`: a soma das despesas por categoria é sempre igual ao total.

## Como usar

Requisito: Python 3.10 ou superior.

```bash
python gastos.py
```

Para testar com dados fictícios de três meses, copie o exemplo antes de rodar:

```bash
copy dados\lancamentos_exemplo.csv dados\lancamentos.csv     # Windows
cp dados/lancamentos_exemplo.csv dados/lancamentos.csv       # Linux
```

```
┌──────────────────────────────────────┐
│          CONTROLE DE GASTOS          │
├──────────────────────────────────────┤
│  1  Novo lançamento                  │
│  2  Lançamentos do mês               │
│  3  Relatório do mês                 │
│  4  Importar CSV                     │
│  5  Categorias e orçamento           │
├──────────────────────────────────────┤
│  0  Sair                             │
└──────────────────────────────────────┘
```

Os meses são digitados como `MM-AAAA`, por exemplo `10-2026`.

## Relatório de exemplo

Gerado com os lançamentos de exemplo, para outubro de 2026:

```
Relatório de outubro de 2026
============================

  Receitas:        R$ 750,00
  Despesas:        R$ 918,10
  Saldo:          R$ -168,10

Despesas por categoria
  Moradia          ████████░░░░░░░░░░░░      R$ 350,00   38,1%
  Alimentação      ███░░░░░░░░░░░░░░░░░      R$ 149,10   16,2%
  Compras          ███░░░░░░░░░░░░░░░░░      R$ 129,00   14,1%
  Contas           ███░░░░░░░░░░░░░░░░░      R$ 118,00   12,9%
  Transporte       ██░░░░░░░░░░░░░░░░░░       R$ 90,00    9,8%
  Lazer            █░░░░░░░░░░░░░░░░░░░       R$ 40,00    4,4%
  Educação         █░░░░░░░░░░░░░░░░░░░       R$ 30,00    3,3%
  Outras despesas  ░░░░░░░░░░░░░░░░░░░░       R$ 12,00    1,3%

Maior despesa: R$ 350,00 em 02/10, Moradia (Aluguel)

Orçamento
  Compras         R$ 129,00 de    R$ 100,00  passou R$ 29,00
  Alimentação     R$ 149,10 de    R$ 150,00  sobram R$ 0,90
  Transporte       R$ 90,00 de    R$ 100,00  sobram R$ 10,00
  Lazer            R$ 40,00 de     R$ 50,00  sobram R$ 10,00
  Contas          R$ 118,00 de    R$ 130,00  sobram R$ 12,00
  1 categoria(s) passaram do limite.

14 lançamento(s) no mês.
```

## Formato do CSV

O mesmo formato vale para o arquivo de lançamentos e para os arquivos importados:

```
data,tipo,valor,categoria,descricao
2026-10-02,despesa,350.00,Moradia,Aluguel
2026-10-10,receita,50.00,Presente,Aniversário
```

- `data` no formato `AAAA-MM-DD`;
- `tipo` é `receita` ou `despesa`;
- `valor` positivo, com até duas casas;
- `categoria` precisa estar no `categorias.json` (na importação, maiúsculas e acentos são ignorados).

## Testes

```bash
pip install pytest
python -m pytest
```

São 119 testes, entre eles os dos critérios de aceite: datas e valores inválidos recusados, soma por categoria igual ao total, linhas inválidas na importação sem derrubar o programa e relatório salvo idêntico ao da tela.

## Estrutura

```
b04-controle-gastos/
├── gastos.py              menu e telas
├── lancamentos.py         ler, gravar, filtrar e importar o CSV; categorias e orçamento
├── relatorio.py           resumo do mês, gráfico de barras e relatório em texto
├── validacao.py           conversão e validação de data, valor, mês, tipo e categoria
├── categorias.json        categorias de receita e de despesa
├── orcamento.json         limite mensal por categoria de despesa
├── test_*.py              testes com pytest
├── dados/
│   └── lancamentos_exemplo.csv    40 lançamentos fictícios de três meses
└── relatorios/            relatórios gerados (fora do Git)
```

O arquivo com os lançamentos reais, `dados/lancamentos.csv`, e os relatórios gerados ficam no `.gitignore`.