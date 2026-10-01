# Projetos formativos em Python

Repositório com os projetos que desenvolvi para consolidar os fundamentos de Python antes de me especializar em análise e ciência de dados.

Todos os projetos usam **apenas Python puro** (linguagem e biblioteca padrão). Cada um foi planejado com um objetivo, uma lista do que deve ser feito e **critérios de aceite** definidos antes da implementação: o projeto só é considerado pronto quando cumpre todos eles.

## Eixos

| Eixo | O que treina |
|---|---|
| 🖥️ Trabalhando com o computador | Automação de pastas e arquivos do sistema com `pathlib`, `os`, `shutil` e argumentos de linha de comando |
| 📁 Trabalhando com arquivos | Programas que salvam e recuperam dados em JSON e CSV sem perder informação quando algo dá errado |
| 🎮 Jogos | Jogos de tabuleiro no terminal com adversário controlado pelo algoritmo minimax |
| 🧱 Orientação a objetos | Sistemas modelados com classes, herança, encapsulamento e exceções próprias |

## Projetos

| Código | Projeto | Eixo | Conceitos principais | Status |
|---|---|---|---|---|
| B01 | [Organizador de pastas](b01-organizador-pastas/) | Computador | `pathlib`, `shutil`, modo simulação | ⏳ Em andamento |
| B02 | [Agenda de contatos](b02-agenda-json/) | Arquivos | JSON, validação, backup de arquivo corrompido | 🔲 A fazer |
| B03 | [Jogo da velha](b03-jogo-da-velha/) | Jogos | recursão, minimax | 🔲 A fazer |
| B04 | [Sistema bancário](b04-sistema-bancario/) | Orientação a objetos | herança, `@property`, exceções próprias | 🔲 A fazer |

> Legenda: ✅ Concluído · ⏳ Em andamento · 🔲 A fazer

## Estrutura do repositório

Cada projeto fica em sua própria pasta, com o código, um README próprio e os testes:

```
projetos-formativos-python/
├── README.md                  <- Este arquivo.
├── .gitignore
├── b01-organizador-pastas/
│   ├── README.md              <- O que faz, como rodar, o que aprendi.
│   ├── organizador.py
│   └── ...
├── b04-agenda-json/
└── ...
```

## Como executar

Requisito: Python 3.10 ou superior. Nenhuma biblioteca externa é necessária.

```bash
git clone https://github.com/tony-esau/projetos-formativos-python.git
cd projetos-formativos-python/b01-organizador-pastas
python organizador.py exemplo --simular
```

As instruções específicas de cada projeto estão no README da pasta dele.

## Padrões que sigo em todos os projetos

- Código organizado em funções pequenas, com nomes descritivos e docstring;
- Nenhuma entrada errada do usuário gera erro sem tratamento;
- Arquivos lidos e escritos com `encoding="utf-8"`;
- Dados pessoais e arquivos gerados ficam fora do repositório (`.gitignore`);
- Testes para as funções principais;
- Commits pequenos e descritivos.

## Autor

**Tony Esaú de Oliveira**, Cientista da Computação
[GitHub](https://github.com/tony-esau) · [Lattes](http://lattes.cnpq.br/4093025295653456)
