# B05 · Jogo da velha com minimax

Jogo da velha no terminal, para duas pessoas ou contra o computador, com quatro níveis de dificuldade. No mais difícil, o computador usa o algoritmo **minimax** com poda alfa-beta e nunca perde.

Escrito em **Python puro**, apenas com a biblioteca padrão.

## Como jogar

Requisito: Python 3.10 ou superior, no Windows, no Linux ou no Mac.

```bash
python main.py
```

Os menus e o tabuleiro são controlados pelo teclado, sem precisar de Enter a cada tecla:

| Tecla | O que faz |
|---|---|
| Setas ou W A S D | movem a seleção |
| Enter ou espaço | confirma a opção ou joga na casa selecionada |
| 1 a 9 | escolhe a opção ou joga direto na casa com esse número |
| Q ou Esc | sai do menu ou abandona a partida |

Um exemplo de como a tela fica durante uma partida:

```
Jogo da velha · Impossível
Você 0  ·  Computador 1  ·  Empates 2

 X | O | 3 
---+---+---
 4 |[X]| 6 
---+---+---
 7 | 8 | O 

Sua vez (X).
Setas ou WASD para mover, Enter para jogar, 1 a 9 para jogar direto, Q para sair.
```

A casa selecionada fica entre colchetes, e as casas livres mostram o seu número. No começo, você escolhe o modo, o símbolo e a dificuldade. O X sempre começa, então escolher o O é deixar o computador abrir a partida. O placar vale para a sessão inteira.

### Dificuldades

| Nível | Como o computador joga |
|---|---|
| Fácil | Escolhe uma casa livre ao acaso. |
| Médio | Vence se puder, bloqueia se você for vencer, e senão joga ao acaso. |
| Difícil | Faz a melhor jogada do minimax em 3 de cada 4 vezes; na outra, joga ao acaso. |
| Impossível | Sempre a melhor jogada do minimax. Nunca perde. |

## Como o minimax funciona

O computador não segue regras como "jogue no centro". Ele **imagina todas as partidas possíveis** a partir do tabuleiro atual, até o fim, e escolhe a jogada que leva ao melhor resultado, supondo que o adversário também sempre faz a melhor jogada para si.

Cada partida imaginada termina com uma nota, do ponto de vista do computador:

- vitória do computador: `10 - profundidade`;
- derrota: `profundidade - 10`;
- empate: `0`.

A profundidade é quantas jogadas foram imaginadas até ali. Ela faz uma vitória rápida valer mais que uma demorada, e uma derrota demorada valer mais que uma rápida. Sem ela, o computador poderia adiar uma vitória que já estava na mão.

As notas sobem a árvore de baixo para cima. Na vez do computador, ele fica com a **maior** nota entre as jogadas possíveis. Na vez do adversário, o computador supõe que ele fica com a **menor**, a pior para o computador. Por isso o nome: o computador maximiza, o adversário minimiza.

### Um exemplo pequeno

O computador joga de O, é a vez dele, e sobram três casas:

```
 O | X | 3
---+---+---
 X | X | 6
---+---+---
 O | 8 | O
```

A árvore com todas as continuações, e a nota de cada uma:

```
vez do O (maior nota)
├── O na casa 3 ─── vez do X (menor nota) ─── vale -8
│   ├── X na casa 6 → X fecha a linha do meio ........ -8
│   └── X na casa 8 → X fecha a coluna do meio ....... -8
│
├── O na casa 6 ─── vez do X (menor nota) ─── vale -8
│   ├── X na casa 3 ─── vez do O (maior nota) ─── vale 7
│   │   └── O na casa 8 → O fecha a linha de baixo ..  7
│   └── X na casa 8 → X fecha a coluna do meio ....... -8
│
└── O na casa 8 → O fecha a linha de baixo ........... 9

O escolhe a casa 8 (nota 9).
```

Repare na casa 6. Ela tem um caminho em que o O vence (nota 7), mas esse caminho depende de o X errar e jogar na casa 3. Como o minimax supõe que o X vai escolher a menor nota, a casa 6 vale -8. O computador nunca conta com um erro do adversário. É isso que o torna impossível de vencer.

A casa 8 vence na hora e vale 9, a maior das três. Se não houvesse vitória imediata, a mesma conta mostraria qual casa bloqueia o X.

### Poda alfa-beta

O minimax testa tudo, mas muitas continuações não podem mudar a decisão. A poda alfa-beta percebe isso e deixa de explorá-las.

No exemplo acima, suponha que o computador testou primeiro a casa 8 e já tem garantida a nota 9. Ao testar a casa 3, a primeira resposta do X já dá -8. Como o X escolhe a menor nota, a casa 3 vale **no máximo** -8, que é pior que o 9 garantido. A segunda resposta do X não precisa ser testada: não importa o que ela dê, o computador não vai escolher a casa 3.

O algoritmo carrega duas notas pelo caminho para fazer esse corte: **alfa**, o melhor que o computador já tem garantido, e **beta**, o melhor que o adversário já tem garantido. Quando alfa fica maior ou igual a beta, o resto daquele ramo é cortado. A escolha final é exatamente a mesma do minimax, só que com muito menos trabalho.

### Quantos tabuleiros cada versão visita

O `desafio.py` mede as três versões calculando a primeira jogada num tabuleiro vazio:

```
Primeira jogada do X num tabuleiro vazio

Versão                 Tabuleiros     Tempo
Minimax                   549.945     1.12s
Com poda alfa-beta         34.202     0.06s
Com memoização             43.653     0.05s

As três versões deram as mesmas notas: sim
Notas das 9 casas: [0, 0, 0, 0, 0, 0, 0, 0, 0]
```

- A **poda alfa-beta** visita 16 vezes menos tabuleiros.
- A **memoização** guarda num dicionário a nota de cada tabuleiro já calculado. O mesmo tabuleiro aparece por vários caminhos (X na casa 1 e depois na 2 é igual a X na 2 e depois na 1), e da segunda vez a nota já está guardada. O jogo da velha tem só alguns milhares de tabuleiros diferentes.
- As notas são todas 0: com os dois jogando perfeitamente, toda primeira jogada termina em empate.

Os tempos variam de computador para computador; os números de tabuleiros, não.

## Testes

```bash
pip install pytest
python -m pytest
```

São 109 testes, entre eles os critérios de aceite:

- `vencedor` detecta as 8 linhas, para o X e para o O;
- num tabuleiro com vitória imediata, `melhor_jogada` escolhe a casa que vence;
- o computador no Impossível **nunca perde**: o teste joga todas as sequências de jogadas possíveis do adversário, com o computador de X e de O, e confere que nenhuma termina em derrota;
- casa ocupada, tecla inválida e número fora de 1 a 9 não fazem a jogada;
- as três versões do minimax dão as mesmas notas.

## Estrutura

```
b05-jogo-da-velha/
├── main.py            menus, partidas e placar
├── tabuleiro.py       regras: criar, jogadas_validas, jogar, vencedor
├── ia.py              as quatro dificuldades, minimax, alfa-beta e memoização
├── teclado.py         lê uma tecla por vez no Windows, no Linux e no Mac
├── tela.py            desenha o tabuleiro, o cursor, os menus e o placar
├── desafio.py         compara quantos tabuleiros cada versão do minimax visita
└── test_*.py          testes com pytest
```

O `tabuleiro.py` e o `ia.py` não têm nenhum `print` nem `input`: só calculam e devolvem valores. Isso permite que o minimax simule milhares de partidas sem mexer na tela, e que tudo seja testado com pytest.