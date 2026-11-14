# Roteiro: fork/join entre dois computadores (MINIP-30)

Programa usado: `tests/distribuido/teste12_fork_join_dois_computadores.minipar`.
Ele soma 1² + 2² + ... + 40000² em 4 partes: 2 rodam no computador 1 e 2 rodam no computador 2.

## 0. Antes de começar

- Os dois computadores na **mesma rede** (mesmo Wi-Fi ou cabo).
- Os dois com o repositório na **mesma versão** e com g++ instalado.
- Descubra o IP do computador 2:
  - Windows: `ipconfig` (linha "Endereço IPv4", ex.: `192.168.0.20`)
  - Linux/Mac: `ip addr` ou `ifconfig`
- No computador 2, libere a porta 7000 no firewall (no Windows, aceite o aviso "Permitir acesso" na primeira vez que o worker abrir).

## 1. Testar sozinho primeiro (localhost)

Num computador só, com dois terminais:

```bash
python main.py tests/distribuido/teste12_fork_join_dois_computadores.minipar
```

O `main.py` termina com `[SUCESSO] Executavel: ...` e mostra onde ficou o executável (`output/runs/run-XXXX/teste12_fork_join_dois_computadores`, com `.exe` no Windows).

Terminal 1 (worker):

```bash
output/runs/run-XXXX/teste12_fork_join_dois_computadores --worker 7000
```

Terminal 2 (coordenador):

```bash
output/runs/run-XXXX/teste12_fork_join_dois_computadores
IP do computador worker: 127.0.0.1
```

Esperado no terminal 2: as 4 partes, os dois totais iguais e `RESULTADO: OK, os dois totais batem.`
Esperado no terminal 1:

```
[WORKER] Esperando tarefas na porta 7000 (programa xxxxxxxxxxxx)
[WORKER] soma_quadrados(20001, 30000) -> OK 6333583335000
[WORKER] soma_quadrados(30001, 40000) -> OK 12333683335000
```

## 2. Em dois computadores

1. Nos **dois** computadores, compile o mesmo arquivo (comando do passo 1). O número `programa xxxxxxxxxxxx` que o worker mostra precisa ser o mesmo nos dois lados (se não for, o coordenador mostra `programa diferente`).
2. **Computador 2**: `.../teste12_fork_join_dois_computadores --worker 7000`
3. **Computador 1**: `.../teste12_fork_join_dois_computadores` e digite o IP do computador 2.
4. Tire print dos dois terminais para o relatório (o do computador 2 mostra as tarefas que ele rodou).

## 3. Se der errado

| Mensagem | O que fazer |
|---|---|
| `fork remoto em IP:7000: Nao foi possivel conectar ... (o worker esta rodando?)` | Confira se o worker está aberto, o IP e o firewall do computador 2. |
| `join: a tarefa N passou do tempo limite de 10000 ms.` | Mesma coisa: a rede não respondeu em 10 s. |
| `o worker em IP:7000 respondeu: programa diferente` | Os dois executáveis vieram de códigos diferentes; compile o mesmo `.minipar` nos dois. |
| `[ERRO WORKER] Nao foi possivel escutar na porta 7000.` | A porta já está em uso; feche o outro worker ou use outra porta (mude `var porta` no `.minipar` e compile de novo nos dois). |

## 4. Limites

- Pela rede só vão números (argumentos e resultado), igual ao `join` local.
- A função do `fork ... on` precisa ser uma `func` do programa (não método de objeto).
- O worker aceita pedidos de qualquer computador da rede e só executa as funções usadas em `fork ... on`. Feche o worker (Ctrl+C) ao terminar.
