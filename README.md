# Compilador MiniPar 2026.2
Trabalho de Compiladores - UFAL

Compilador da linguagem **MiniPar 2026.2**, orientada a objetos, com paralelismo real
(`par`, `fork`/`join`) e execução em **computadores diferentes** (`fork ... on canal`).
O pipeline é: lexer → parser → AST → análise semântica → código de três endereços (TAC)
→ C++20 → executável gerado pelo `g++ -O3`. Uma **IDE Web didática** mostra cada fase.

Repositório: https://github.com/maineros/minipar-improvement-2026.2

## Integrantes

- João Felipe Jatobá
- Júlia Pereira
- Laura Mainero
- Yuri Barbosa

Este projeto parte do compilador MiniPar 2026.1, desenvolvido por
Emanuele Vitória de Jesus Lima ([Manu-Vii](https://github.com/Manu-Vii)),
José Lucas de Oliveira Quintela ([lucasqtl](https://github.com/lucasqtl)) e
Luiz Miguel de Melo Bomfim ([luizwhirl](https://github.com/luizwhirl)).

---

## Novidades da versão 2026.2

| O quê | Onde |
|---|---|
| Palavras reservadas `fork` e `join` (minúsculas) no lexer, parser, semântica e TAC | `src/` |
| `fork`/`join` traduzidos para tarefas paralelas no C++ (`std::async`) | `src/codegen.py`, `src/cpp_template.py` |
| `fork f(x) on canal`: a tarefa roda em **outro computador**; `join(t, ms)` com tempo limite | `src/`, `docs/ROTEIRO_FORK_JOIN_DOIS_COMPUTADORES.md` |
| Modo worker: o mesmo executável atende tarefas remotas com `--worker PORTA` | `src/cpp_template.py` |
| Códigos nos erros semânticos de fork/join (`SEM_FJ_01` a `SEM_FJ_06`) | `src/semantic.py`, `BNF-grammar.md` |
| Funções de texto: `to_string`, `substr`, `s[i]` e `s = s + "texto"` | `src/semantic.py`, `src/codegen.py` |
| O terminal aborta a compilação ao achar erro léxico | `main.py` |
| `-lws2_32` só é passado ao `g++` no Windows (compila também no Linux e no Mac) | `src/codegen.py` |
| Gramática (BNF) atualizada para a 2026.2 | `BNF-grammar.md` |
| IDE Web didática: abas Tokens, AST (árvore gráfica), Semântica, TAC, C++, Execução e ARMv7 | `app.py`, `templates/`, `static/` |
| Compilar e executar pela Web, com entradas do programa e download do executável | `app.py`, `web_execution.py` |
| Testes oficiais 8, 9 e 10 com `fork`/`join` | `tests/` |
| Teste 11: minicompilador de expressões escrito em MiniPar que gera Assembly ARMv7 (CPUlator) | `tests/teste11_minicompilador_expressoes_arm.minipar` |
| Teste 12: fork/join entre dois computadores | `tests/distribuido/` |
| Medição de desempenho sequencial x paralelo x distribuído | `benchmarks/`, `docs/MINIP33_DESEMPENHO_FORK_JOIN.md` |
| Testes de regressão do MiniPar 2026.1 | `tests/test_minipar_2026_1_regression.py` |
| Arquitetura de componentes: cada fase realiza uma interface `I_*` e o orquestrador liga as fases | `src/interfaces.py`, `src/orquestrador.py` |
| Tabela de Símbolos como componente próprio | `src/symbol_table.py` |
| `to_number` e `parse_ints` com entrada inválida mostram `[ERRO EXECUCAO]` com o motivo | `src/cpp_template.py` |
| Teste 1 (calculadora) com cliente e servidor em dois computadores | `tests/distribuido/`, `docs/ROTEIRO_TESTE1_DOIS_COMPUTADORES.md` |
| Diagramas UML (pacotes, componentes e classes) com a Tabela de Símbolos e as interfaces `I_*`, e o texto Mermaid de cada um | `diagramas/`, `diagramas/fontes/` |

---

## Estrutura do Projeto

```text
minipar-improvement-2026.2/
├── src/                      # Componentes do compilador
│   ├── interfaces.py         # Interfaces dos componentes (I_Lexico, I_Sintatico, ...)
│   ├── orquestrador.py       # Componente Orquestrador (MainCompiler)
│   ├── ast_nodes.py          # Nós da AST (dataclasses)
│   ├── lexer.py              # Componente Analisador Léxico
│   ├── parser.py             # Componente Analisador Sintático
│   ├── symbol_table.py       # Componente Tabela de Símbolos
│   ├── semantic.py           # Componente Analisador Semântico
│   ├── tac.py                # Componente Gerador de Código Intermediário (TAC)
│   ├── codegen.py            # Componente Gerador de Código C++ (e chamada ao g++)
│   └── cpp_template.py       # Runtime C++ (threads, fork/join, canais, worker)
├── templates/                # HTML da IDE Web (index.html didática, legacy.html 2026.1)
├── static/
│   ├── css/                  # Estilos das duas interfaces
│   ├── js/                   # Fases, árvore da AST, execução, aba ARMv7, monitor
│   └── vendor/               # D3.js 7.9.0 (cópia local) e licença
├── tests/
│   ├── *.minipar             # Programas de teste (1 a 11 e adicionais)
│   ├── distribuido/          # Teste 1 em dois computadores e Teste 12 (precisa de um worker)
│   ├── expected_results/     # Saídas esperadas (.txt, .tac, .arm)
│   ├── test_*.py             # Testes automáticos (unittest)
│   └── *.test.cjs            # Testes do JavaScript da Web (Node.js)
├── benchmarks/
│   ├── medir_fork_join.py    # Mede sequencial x paralelo x distribuído
│   └── carga_distribuida.minipar
├── docs/
│   ├── ROTEIRO_FORK_JOIN_DOIS_COMPUTADORES.md
│   ├── ROTEIRO_TESTE1_DOIS_COMPUTADORES.md
│   └── MINIP33_DESEMPENHO_FORK_JOIN.md
├── diagramas/                # Diagramas UML (PNG e PDF)
│   └── fontes/               # Texto Mermaid (.mmd) de cada diagrama
├── app.py                    # Servidor Flask da IDE Web (componente IDEWebApp)
├── web_execution.py          # Compilação e execução isoladas para a Web
├── analysis_worker.py        # Análise de uma fase em processo isolado (Web)
├── run_artifacts.py          # Pasta exclusiva para cada compilação
├── main.py                   # Ponto de entrada (CLI e menu), usa o orquestrador
├── menu.py                   # Menu interativo do terminal (componente MenuCLI)
├── program_analyzer.py       # Detecta entradas e multi-terminal de cada programa
├── test_orchestrator.py      # Coordena execuções em vários terminais
├── BNF-grammar.md            # Gramática MiniPar 2026.2
├── requirements.txt          # Dependências Python
└── README.md
```

As pastas `output/` (arquivos gerados: `.cpp`, `.tac`, executáveis e medições) e
`temp_code/` são criadas durante o uso e não vão para o Git.

---

## Requisitos

- Python 3.8 ou superior
- `g++` com suporte a C++20 no PATH (para compilar o código C++ gerado)
- Flask (para a IDE Web e para parte dos testes automáticos)
- Node.js (opcional, só para os testes do JavaScript)

Instalação das dependências:

```bash
pip install -r requirements.txt
```

---

## Como Usar

O compilador oferece múltiplas formas de interação.

### 1. Menu Interativo (Terminal ou IDE Web)

Execute o programa sem argumentos:

```bash
python main.py
```

Opções disponíveis:

- **[1] Modo Terminal**: navegação pelos testes através de um menu textual.
- **[2] Modo Web Interface**: inicia o servidor Flask.

Se houver uma sessão de teste ativa, aparece antes um aviso com outras opções.
Nesse aviso, **[1] Executar de forma independente** permite chegar ao menu acima;
**[2] Continuar e participar** abre o monitor da execução existente. Para abrir a
Web independentemente de um teste, escolha **1 no aviso e 2 no menu principal**.

Após iniciar o servidor, as duas interfaces Web ficam disponíveis:

- **Interface didática (2026.2):** http://127.0.0.1:5000/
- **Interface anterior (2026.1):** http://127.0.0.1:5000/legacy

A interface anterior mantém o editor, as abas C++/TAC e a ação **Compile & Run**.
O modo Terminal continua disponível pelo menu, independentemente da interface Web.

A IDE permite:

- Editar código MiniPar
- Compilar o programa
- Visualizar o código TAC gerado
- Visualizar o código C++ gerado
- Executar o programa e ver a saída

Na interface didática, cada opção da barra analisa o código atual do editor:

- **Tokens:** tipo, texto, linha e coluna dos tokens reconhecidos pelo lexer.
- **AST:** árvore gráfica dos nós produzidos pelo parser, com zoom, navegação,
  expansão de ramos e detalhes dos nós; o JSON completo também fica disponível.
- **Semântica:** resultado da validação e os diagnósticos encontrados.
- **TAC** e **Código C++:** código gerado sem compilar ou executar o programa.
- **ARMv7:** mostra o Assembly ARMv7 impresso pelo Teste 11 (entre
  `=== INICIO ARM ===` e `=== FIM ARM ===`) e permite baixá-lo como arquivo `.arm`
  para rodar no simulador CPUlator (sistema ARMv7).

As análises não solicitam entradas de `input()` nem iniciam sessões de execução.
Se uma fase anterior falhar, o painel informa onde a análise parou. Alterar o
código invalida os resultados anteriores; selecionar uma fase novamente analisa
a nova versão.

Na AST, selecione um nó para consultar seu tipo, a linha do código e seus
atributos. Os ramos podem ser expandidos ou recolhidos, e os controles de zoom e
ajuste ajudam a navegar em árvores maiores. A visualização pode ser ampliada em
uma janela própria; o JSON original permanece acessível para consulta.

A árvore utiliza uma cópia local do [D3.js 7.9.0](https://github.com/d3/d3/releases/tag/v7.9.0),
em `static/vendor/`, sem carregar essa biblioteca de um CDN. Sua licença ISC está
em `static/vendor/d3-LICENSE.txt`.

**Compilar e baixar** compila o código atual e inicia o download do executável,
sem executar o programa nem solicitar entradas. O painel mantém um link para
baixar o mesmo arquivo novamente. Alterar o código ou iniciar uma nova compilação
remove o link anterior. O binário é gerado para o sistema do servidor (no Windows,
um arquivo `.exe`).
Os links ficam disponíveis enquanto esta instância do servidor está em execução;
após reiniciá-la, compile novamente para obter um novo link.

**Executar** compila o código atual, executa o binário no servidor e apresenta as
mensagens e a saída à medida que são produzidas. Para programas com `input()`,
abra **Entradas do programa** na aba Execução e preencha uma linha por leitura,
antes de executar. As linhas são enviadas na ordem informada, preservando espaços
e linhas vazias; esse campo também funciona para código escrito diretamente no
editor. As entradas são fechadas após o envio, e a execução tem limite de tempo.
Erros de compilação, término com código diferente de zero e estouro do tempo
limite são apresentados no painel. Os logs técnicos ficam em **Mensagens da
compilação**, que se abre automaticamente quando a compilação falha.

Os doze exemplos interativos abaixo recebem seus dados por `input()`. Na Web, preencha as
linhas na ordem indicada e selecione **Executar**; no Terminal, responda aos
prompts do próprio programa. O Teste 2 mantém fatorial e Fibonacci em paralelo,
agora com duas entradas: número do fatorial e quantidade de termos. Por exemplo,
as linhas `5` e `8` produzem fatorial `120` e a sequência
`0, 1, 1, 2, 3, 5, 8, 13`. Há apenas uma versão desse teste.

| Programa | Entradas, em ordem (uma por linha) |
|---|---|
| Calculadora cliente-servidor | Operação (`+`, `-`, `*`, `/`), primeiro operando, segundo operando |
| Fatorial e Fibonacci em paralelo | Número inteiro para o fatorial (0–12), quantidade de termos (0–45) |
| Neurônio | Valor de entrada (-100–100), saída desejada (0 ou 1), taxa de aprendizado (0.001–1) |
| Rede XOR | Primeiro bit, segundo bit, épocas (1–50000), taxa de aprendizado (0.001–1) |
| Recomendação | 16 valores de histórico de compras (0 ou 1), um por linha, na ordem do catálogo |
| Quicksort com classes | Vetor de números separados por espaços, em uma linha |
| Quicksort iterativo | Vetor de números separados por espaços, em uma linha |
| Paralelismo com três computadores | Vetor a ordenar; duas linhas da matriz A (2 números em cada); duas linhas da matriz B (2 números em cada); número do fatorial (0–12) |
| Tapete de Sierpinski | Tamanho: 3, 9, 27 ou 81 |
| Fractal ASCII | Quantidade inteira de linhas do desenho (1–64) |
| Teste 11: minicompilador de expressões → ARMv7 | Uma expressão inteira com `+ - * /`, parênteses e menos unário (ex.: `2 + 3 * (4 - 1)`) |
| Controles da BNF | Nome, limite do laço (0–1000), quantidade de tentativas (1–1000) |

Os testes oficiais 8, 9 e 10 usam `fork`/`join` e mantêm os valores de referência
definidos em seus fontes, sem leitura por `input()`. O mesmo vale para
`teste_funcoes_texto.minipar`, que exercita as funções de texto. Os resultados
esperados estão em `tests/expected_results/`.

| Programa | O que faz |
|---|---|
| Teste 8 | Avaliação de 160 atividades por 4 avaliadores, sequencial e paralela |
| Teste 9 | Teste 8 com um 5º núcleo que desenha o conjunto de Mandelbrot em ASCII |
| Teste 10 | Teste 9 com um 6º núcleo que desenha o triângulo de Sierpinski |

O Teste 12 (`tests/distribuido/teste12_fork_join_dois_computadores.minipar`) precisa
de um worker aberto e por isso não aparece na lista da Web. Veja a seção
[Fork e Join entre computadores](#fork-e-join-entre-computadores).

O Teste 1 também tem uma versão com cliente e servidor em executáveis separados,
para rodar em dois computadores: `tests/distribuido/teste1_servidor_calculadora.minipar`
(computador 2, porta 5101) e `tests/distribuido/teste1_cliente_calculadora.minipar`
(computador 1, porta 5102). Abra primeiro o servidor e digite o IP do cliente; depois
abra o cliente e digite o IP do servidor. Para testar num computador só, use
`127.0.0.1` nos dois. O passo a passo está em
[`docs/ROTEIRO_TESTE1_DOIS_COMPUTADORES.md`](docs/ROTEIRO_TESTE1_DOIS_COMPUTADORES.md).

Se o programa receber um texto que não é número em `to_number` (ex.: `abc`) ou em
`parse_ints` (ex.: `10 abc 5`), ele para com `[ERRO EXECUCAO]` e o motivo, em vez
de quebrar.

As entradas dos algoritmos são configuráveis; a tabela-verdade do XOR, o
catálogo de produtos e os valores de inicialização continuam definindo os
respectivos modelos. Alterar os dados de execução não exige editar os fontes.
Código escrito no editor também pode usar valores fixos: se houver entradas
preenchidas e nenhuma chamada real a `input()`, a interface pede a correção antes
de executar. Menções a `input()` em textos e comentários não são leituras.

As ações usam pastas de artefatos exclusivas por pedido, assim como a CLI. A
interface anterior em `/legacy` continua usando sua API e seu fluxo existentes.
As duas rotas de execução Web atualizam somente a sessão do mesmo programa,
código-fonte e terminal iniciador. Falhas encerram a sessão correspondente para
que os participantes não fiquem presos no monitor. O monitor do terminal mantém
o vínculo com a execução original mesmo que outra sessão seja iniciada.

`POST /api/build` recebe `{"code": "seq { print(1); }", "filename": "exemplo.minipar"}`
e retorna o resultado da compilação, TAC, C++ e `download_url` em caso de sucesso.
O link dá acesso apenas ao executável daquela compilação.

`POST /api/execute` recebe os mesmos campos e `inputs` (lista de textos). A resposta
é um fluxo `application/x-ndjson`: eventos `phase`, `output` (com `stream` e `text`),
eventuais `error` e um evento final `complete` com `success`, `exit_code`, TAC e C++.
Os limites padrão são 15 segundos para compilar, 30 segundos para executar e
2 MiB de saída por processo. Tempo limite ou encerramento da conexão durante a
execução interrompem os processos envolvidos.

A API de fases usa `POST /api/analyze` com JSON no formato
`{"code": "seq { print(1); }", "phase": "tokens"}`. As fases aceitas são `tokens`,
`ast`, `semantic`, `tac` e `cpp`. A resposta contém `success`, `phase`,
`failed_phase`, `result` e `diagnostics`. Cada análise é executada em um processo
isolado, com limite de 15 segundos, sem gerar arquivos ou invocar `g++`.

### Fork e Join

O gerador C++ traduz `fork`/`join` para tarefas paralelas (`std::async`). O
`fork` devolve um número (o "handle" da tarefa), que pode ser guardado em variáveis
e listas; o `join` espera a tarefa e devolve o resultado.

```minipar
var t1 = fork calcular_parte(0, 50);
var t2 = fork calcular_parte(51, 100);
var total = join(t1) + join(t2);
```

Limites atuais: o `join` devolve só números (tarefas sem retorno dão zero) e
cada tarefa recebe uma cópia das variáveis, sem compartilhar memória.

### Fork e Join entre computadores

Com `on canal`, o `fork` manda a tarefa para outro computador. O `canal` é um
`c_channel(ip, porta)`. O `join(t, ms)` espera no máximo `ms` milissegundos.

```minipar
var outro_computador = c_channel("192.168.0.20", 7000);
var t1 = fork soma_quadrados(1, 10000);                          # roda aqui
var t2 = fork soma_quadrados(10001, 20000) on outro_computador;  # roda no outro computador
var p1 = join(t1);
var p2 = join(t2, 10000);                                        # espera no máximo 10 s
```

No outro computador roda **o mesmo executável** em modo worker:

```bash
# computador 2 (worker)
output/runs/run-XXXX/teste12_fork_join_dois_computadores --worker 7000
# computador 1 (coordenador): rode o executável e digite o IP do computador 2
output/runs/run-XXXX/teste12_fork_join_dois_computadores
```

Pela rede vão o nome da função e os argumentos (só números), e volta o resultado.
Os dois lados conferem um id do programa; se os executáveis vierem de códigos
diferentes, o erro é `programa diferente`. A função usada em `fork ... on` precisa
ser uma `func` do programa. Para testar num computador só, use o IP `127.0.0.1`.

O passo a passo completo, com os erros mais comuns, está em
[`docs/ROTEIRO_FORK_JOIN_DOIS_COMPUTADORES.md`](docs/ROTEIRO_FORK_JOIN_DOIS_COMPUTADORES.md).

| Código | Erro semântico |
|---|---|
| `SEM_FJ_01` | `fork` precisa de uma chamada de função ou método |
| `SEM_FJ_02` | `join` precisa de uma tarefa criada por `fork` |
| `SEM_FJ_03` | o destino de `fork ... on` precisa ser um `c_channel` |
| `SEM_FJ_04` | o tempo limite do `join` precisa ser um número |
| `SEM_FJ_05` | `fork ... on` só chama função declarada com `func` |
| `SEM_FJ_06` | `fork ... on` só envia números como argumento |

### Medição de desempenho

O script `benchmarks/medir_fork_join.py` compila e roda os testes 8, 9 e 10 e a
carga `benchmarks/carga_distribuida.minipar`, mede o tempo de cada fase (mediana de
5 rodadas) e calcula o speedup (tempo sequencial / tempo paralelo). Só aceita a
rodada se a saída estiver certa.

```bash
# tudo, com o worker no mesmo computador
python benchmarks/medir_fork_join.py
# só alguns programas, ou menos rodadas
python benchmarks/medir_fork_join.py --programas t8,t9 --repeticoes 3
# carga distribuída com o worker em outro computador
python benchmarks/medir_fork_join.py --programas carga --ip IP_DO_COMPUTADOR_2
```

O resultado fica em `output/bench/<data-hora>/resultado.md` e `resultado.json`.
No computador de desenvolvimento (Linux, 4 núcleos) o paralelo foi de 3,2 a 3,4
vezes mais rápido nos testes 8 a 10 e 3,8 vezes na carga. Num Windows de 14 núcleos,
o ganho foi de cerca de 2,5 vezes nos testes 8 a 10 e 3,1 na carga. Detalhes, tabela
e roteiro de medição em dois computadores em
[`docs/MINIP33_DESEMPENHO_FORK_JOIN.md`](docs/MINIP33_DESEMPENHO_FORK_JOIN.md).

### 2. Execução Direta (CLI)

Para compilar um arquivo específico:

```bash
python main.py tests/teste3_neuronio.minipar
```

O nome do arquivo de saída é opcional. Por padrão, será utilizado o mesmo nome do arquivo `.minipar`.

Cada compilação cria uma pasta exclusiva em `output/runs/run-.../`, contendo
os arquivos `.cpp`, `.tac` e o executável. O terminal informa essa pasta na linha
`[OUTPUT]`. Assim, execuções simultâneas do mesmo programa no terminal e na IDE
Web mantêm seus próprios arquivos. Na IDE, o código-fonte enviado também fica
na subpasta `source/` dessa execução.

O menu do terminal e a IDE executam o binário da respectiva pasta. Na CLI direta,
o comando acima compila; para executar, use o caminho do executável informado
em `[SUCESSO] Executavel:`. As pastas são mantidas para inspeção posterior.

Para ferramentas que precisam escolher a pasta explicitamente:

```bash
python main.py tests/teste3_neuronio.minipar --output-dir output/minha_execucao
```

Ao usar `--output-dir`, escolha uma pasta diferente para cada execução simultânea.

### Testes automáticos

Da raiz do repositório (precisa de Flask e de `g++` no PATH):

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

A suíte cobre, entre outros: as fases do compilador, os componentes e suas
interfaces, a saída de todos os exemplos, os testes oficiais 8 a 10, o Teste 1 com
cliente e servidor separados, o Teste 11 (ARMv7), as funções de texto, a entrada
inválida em `to_number` e `parse_ints`, o fork/join local e distribuído (com worker
em `127.0.0.1`), a regressão do MiniPar 2026.1, a medição de desempenho e o
isolamento das execuções Web e terminal.

Os testes do JavaScript da IDE usam o executor de testes do Node.js:

```bash
node --test tests/ast_tree_model.test.cjs
node --test tests/execution_stream.test.cjs
node --test tests/arm_extract.test.cjs
```

O teste de isolamento compila simultaneamente dois pedidos Web e uma execução CLI
com o mesmo nome de arquivo e conteúdos diferentes.

---

## Fases do Compilador

| Fase | Arquivos | Descrição |
|------|----------|------------|
| 1 | `lexer.py` | Tokenização do código-fonte (erros léxicos abortam a compilação) |
| 2 | `parser.py` / `ast_nodes.py` | Análise sintática e construção da AST |
| 3 | `semantic.py` / `symbol_table.py` | Declarações, escopo, tipos e regras de `fork`/`join` (códigos `SEM_FJ`), com a Tabela de Símbolos |
| 4 | `tac.py` | Geração de Código Intermediário (TAC) de três endereços |
| 5 | `codegen.py` / `cpp_template.py` | Geração de código C++20 e compilação via `g++ -O3` |

A gramática completa da linguagem está em [`BNF-grammar.md`](BNF-grammar.md).
Os diagramas UML estão na seção [Diagramas UML](#diagramas-uml).

---

## Arquitetura de Componentes

Cada parte do compilador é um componente de software. A interface do componente
é uma classe abstrata com prefixo `I_` (`src/interfaces.py`) e o componente é a
classe concreta que herda dela e implementa seus métodos. Os componentes são
usados sempre pela interface: o orquestrador (`MainCompiler`) guarda cada um num
atributo do tipo da interface e liga as fases na ordem
Lexer → Parser → SemanticAnalyzer (+ TabelaSimbolos) → TACGenerator → CppCodeGenerator → g++.
O terminal (`main.py`) e a Web (`analysis_worker.py`) falam com o compilador pelo
orquestrador.

| Interface | Componente | Arquivo |
|-----------|------------|---------|
| `I_Lexico` | `Lexer` | `src/lexer.py` |
| `I_Sintatico` | `Parser` | `src/parser.py` |
| `I_TabelaSimbolos` | `TabelaSimbolos` | `src/symbol_table.py` |
| `I_Semantico` | `SemanticAnalyzer` | `src/semantic.py` |
| `I_GeradorTAC` | `TACGenerator` | `src/tac.py` |
| `I_GeradorCPP` | `CppCodeGenerator` | `src/codegen.py` |
| `I_Orquestrador` | `MainCompiler` | `src/orquestrador.py` |
| `I_Interface_Usuario` | `MenuCLI` / `IDEWebApp` | `menu.py` / `app.py` |

Os testes de integração dos componentes estão em `tests/test_componentes.py`.

---

## Diagramas UML

Os diagramas ficam em `diagramas/` e seguem o código atual (componentes, interfaces
`I_*` e Tabela de Símbolos usada só pelo Analisador Semântico).

| Diagrama | O que mostra | Arquivo |
|---|---|---|
| Arquitetura (pacotes) | Pacotes Interface, Orquestração, Contratos, Front-end, Back-end e Ambiente de Execução, com os arquivos de cada um | [Arquitetura do Compilador Utilizando UML (Notação de Pacotes).png](diagramas/Arquitetura%20do%20Compilador%20Utilizando%20UML%20%28Nota%C3%A7%C3%A3o%20de%20Pacotes%29.png) |
| Componentes no contexto da linguagem | Cada fase como componente, a interface usada em cada ligação e o caminho tokens → AST → TAC e C++ → g++ | [Diagrama de componentes Interface.png](diagramas/Diagrama%20de%20componentes%20Interface.png) (também em [MiniPar Compiler Architecture-2026-11-11-022701.pdf](diagramas/MiniPar%20Compiler%20Architecture-2026-11-11-022701.pdf)) |
| Componentes (classes UML) | Interfaces `I_*`, os componentes que as realizam, seus atributos e métodos, e as dependências | [Diagrama de Componentes (classes UML).png](diagramas/Diagrama%20de%20Componentes%20%28classes%20UML%29.png) |

O texto de cada diagrama, em [Mermaid](https://mermaid.js.org/), está em
`diagramas/fontes/` (`arquitetura_pacotes.mmd`, `diagrama_componentes_interface.mmd`
e `diagrama_componentes_classes_uml.mmd`). Para alterar um diagrama, edite o `.mmd`,
cole em https://mermaid.live e exporte o PNG novo.

---

## Sintaxe MiniPar

Exemplo:

```minipar
func dobro(x) {
    return x * 2;
}

seq {
    var x = 42;

    print("Valor:", x);

    par {
        print("Thread A");
        print("Thread B");
    }

    var t = fork dobro(x);
    print("Dobro:", join(t));
}
```

### Comandos Disponíveis

| Sintaxe | Descrição |
|----------|------------|
| `seq { ... }` | Bloco sequencial |
| `par { ... }` | Bloco paralelo (cada instrução gera uma thread C++) |
| `var nome = expr;` | Declaração de variável |
| `nome = expr;` | Atribuição |
| `print(expr, ...);` | Impressão na saída padrão |
| `input("texto")` | Leitura de uma linha da entrada |
| `func nome(args) { ... }` | Declaração de função |
| `fork f(args)` | Dispara `f` em paralelo e devolve o handle da tarefa |
| `fork f(args) on canal` | Dispara `f` em outro computador (`canal = c_channel(ip, porta)`) |
| `join(t)` / `join(t, ms)` | Espera a tarefa `t` (com tempo limite opcional, em ms) e devolve o resultado |
| `to_string(x)`, `substr(s, i, n)`, `s[i]` | Funções de texto |
| `# comentário` | Comentário de linha |

A lista completa (classes, `if`/`while`/`for`, canais `send`/`receive`, listas e
matrizes) está na BNF.
