# MINIP-33: desempenho e execução distribuída do fork/join

Este documento mostra duas coisas:

1. o `fork`/`join` deixa os testes 8, 9 e 10 mais rápidos (sequencial x paralelo);
2. o `fork ... on canal` (MINIP-30) roda partes do trabalho em outro computador e dá o mesmo resultado.

## 1. Como medir

O MiniPar não tem cronômetro. O script `benchmarks/medir_fork_join.py` mede de fora, sem mexer no compilador:

1. compila cada programa com o `main.py`;
2. roda o executável e anota a hora em que aparece cada linha "marco" que o programa já imprime;
3. tempo de uma fase = hora do marco seguinte − hora do marco da fase;
4. repete 5 vezes (mais 1 aquecimento, descartado) e usa a **mediana**;
5. só aceita a rodada se a saída estiver certa: igual ao `expected.txt` (testes 8 a 10) ou com `RESULTADO: OK` (carga distribuída).

| Programa | Marcos usados |
|---|---|
| Testes 8, 9 e 10 | `--- 1. Executando Modo Sequencial` → `--- 2. Executando Modo Paralelo` → `RESULTADO DA AVALIACAO` |
| `benchmarks/carga_distribuida.minipar` | `--- 1. Sequencial` → `--- 2. Paralelo local` → `--- 3. Distribuido` → `--- FIM` |

**Speedup** = tempo sequencial / tempo paralelo (medianas). Com N tarefas, o teto é N, e ele também é limitado pelo número de núcleos do computador.

### Comandos

Da raiz do repositório:

```bash
# tudo (testes 8, 9, 10 e a carga), com o worker no mesmo computador
python benchmarks/medir_fork_join.py

# só alguns programas, ou menos rodadas
python benchmarks/medir_fork_join.py --programas t8,t9 --repeticoes 3
```

O resultado fica em `output/bench/<data-hora>/resultado.md` (tabela) e `resultado.json` (cada rodada, mínimo, máximo, ambiente).

### A carga distribuída

`benchmarks/carga_distribuida.minipar` faz a mesma conta (somar de 1 a 1.200.000.000, em 4 partes) de três jeitos:

1. **sequencial**: uma parte por vez;
2. **paralelo local**: 4 `fork` neste computador;
3. **distribuído**: 2 `fork` aqui e 2 `fork ... on canal` no outro computador.

Os três modos fazem as mesmas 4 chamadas e somam na mesma ordem, então os totais têm de sair iguais.

> **Por que o modo sequencial também usa `fork` (uma tarefa por vez)?** Achamos que o g++ otimiza pior um laço chamado direto no `seq` (o código vai para dentro do `main`) do que o mesmo laço numa tarefa. Num teste à parte, a mesma função levou 0,25 s no `main` e 0,06 s numa thread. Se o sequencial chamasse a função direto, o speedup sairia inflado (passava de 10 com 4 núcleos). Com `fork` + `join` logo em seguida, os três modos rodam o mesmo código C++. No Teste 8 esse efeito não aparece (conferimos: o speedup fica igual), porque o trabalho dele já é chamado por outras funções.

## 2. Resultados (computador de desenvolvimento)

- Data: 14/11/2026
- Sistema: Linux 6.18
- CPU: Intel Xeon @ 2.10GHz, **4 núcleos lógicos**
- Compilador: g++ 13.3.0 (`-std=c++20 -O3 -pthread`)
- Commit: `18485c8` (main)
- Medida: mediana de 5 rodadas (1 aquecimento descartado)

| Programa | Tarefas | Sequencial (s) | Paralelo (s) | Speedup paralelo | Distribuído (s) | Speedup distribuído |
|---|---|---|---|---|---|---|
| Teste 8 (4 núcleos) | 4 | 0,152 | 0,046 | **3,33** | - | - |
| Teste 9 (5 núcleos + Mandelbrot) | 5 | 0,152 | 0,045 | **3,39** | - | - |
| Teste 10 (6 núcleos + 2 fractais) | 6 | 0,153 | 0,048 | **3,20** | - | - |
| Carga distribuída | 4 | 0,767 | 0,201 | **3,81** | 0,198 | **3,88** (worker em 127.0.0.1) |

As 20 rodadas medidas (e os 4 aquecimentos) deram a saída certa.

### Como ler

- **O paralelo ganha de 3,2 a 3,4 vezes nos testes 8 a 10.** O teto aqui é 4, porque o computador tem 4 núcleos lógicos. Os testes 9 e 10 abrem 5 e 6 tarefas, mas continuam com só 4 núcleos, por isso o ganho não passa de 4.
- **Não chega a 4** porque criar as threads custa um pouco, as partes não têm exatamente o mesmo tamanho e a medida inclui imprimir as linhas.
- **Tempos curtos variam.** Os testes 8 a 10 levam décimos de segundo; por isso usamos a mediana de 5 rodadas. Os valores de cada rodada estão no `resultado.json`.
- **O "distribuído" com worker em 127.0.0.1 não é ganho de rede.** O worker roda no mesmo computador e divide os mesmos 4 núcleos. Ele prova que o caminho pela rede (TCP) funciona e custa pouco. O ganho de usar **outro** processador só aparece no roteiro da seção 3.
- **Em outro computador os números mudam.** Rode o script na máquina da apresentação e cole a tabela nova aqui.

## 3. Roteiro: medir com dois computadores

Antes: os dois computadores na **mesma rede**, com o repositório na **mesma versão** e g++. Veja também `docs/ROTEIRO_FORK_JOIN_DOIS_COMPUTADORES.md` (Teste 12).

1. **Nos dois computadores**, compile a carga:
   ```bash
   python main.py benchmarks/carga_distribuida.minipar carga_distribuida
   ```
   O `main.py` mostra onde ficou o executável (`output/runs/run-XXXX/carga_distribuida`, com `.exe` no Windows).
2. **Computador 2** (worker): descubra o IP (`ipconfig` no Windows, `ip addr` no Linux) e abra o worker:
   ```bash
   output/runs/run-XXXX/carga_distribuida --worker 7000
   ```
   Na primeira vez, no Windows, aceite o aviso do firewall ("Permitir acesso").
3. **Computador 1** (coordenador): rode a medição apontando para o computador 2:
   ```bash
   python benchmarks/medir_fork_join.py --programas carga --ip IP_DO_COMPUTADOR_2
   ```
   O script compila a carga de novo no computador 1. Como o fonte é o mesmo, o id do programa bate com o do worker.
4. **Registre para o relatório:**
   - print do terminal do computador 2 (as linhas `[WORKER] trabalho(...) -> OK ...` provam que ele rodou as partes 3 e 4);
   - print do terminal do computador 1 com a tabela;
   - o `resultado.md` e o `resultado.json` do computador 1;
   - data, IPs, processador e número de núcleos dos dois computadores.
5. **Prova de falha (opcional):** feche o worker (Ctrl+C) e rode o passo 3 de novo. O esperado é o erro `fork remoto em IP:7000: Nao foi possivel conectar ... (o worker esta rodando?)` e o script terminando com código 1, sem travar.

### O que esperar

- O modo **distribuído** usa 2 núcleos do computador 1 e 2 do computador 2. Se os dois forem parecidos, o tempo fica perto do paralelo local, mais o tempo da rede (pouco, porque só vão 2 números e volta 1).
- Se o computador 2 for mais lento, o distribuído demora mais: o `join` espera a parte mais lenta.

### Se der errado

| Mensagem | O que fazer |
|---|---|
| `Nao foi possivel conectar ... (o worker esta rodando?)` | Confira se o worker está aberto, o IP e o firewall do computador 2. |
| `o worker em IP:7000 respondeu: programa diferente` | Os dois lados não compilaram o mesmo `.minipar`. Atualize o repo nos dois e compile de novo. |
| `a porta 7000 já está em uso` | Já tem um worker aberto neste computador. Feche e rode de novo. |
| `marco não encontrado na saída` | Alguém mudou um `print` de marco no `.minipar`. Ajuste a lista `PROGRAMAS` no script. |

## 4. Limites

- O script mede o tempo de parede de cada fase, incluindo imprimir as linhas.
- A porta 7000 é fixa no `.minipar` (`var porta = 7000`).
- Os testes 8 a 10 não usam rede: o `fork` deles é local (threads).
