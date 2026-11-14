# Roteiro: Teste 1 (calculadora cliente-servidor) em dois computadores

O enunciado pede o Teste 1 primeiro em localhost e depois em dois computadores:
o cliente (computador_1) pede a operação e o servidor (computador_2) calcula e
devolve o resultado.

- `tests/teste1_calculadora_cliente_servidor.minipar`: os dois lados no mesmo
  programa (blocos `par`), só em localhost.
- `tests/distribuido/teste1_servidor_calculadora.minipar` e
  `tests/distribuido/teste1_cliente_calculadora.minipar`: servidor e cliente em
  executáveis separados, para rodar em computadores diferentes.

## Canais usados

| Canal | Sentido | Porta |
|---|---|---|
| `requisicao` | cliente → servidor | 5101 (aberta no servidor) |
| `resposta` | servidor → cliente | 5102 (aberta no cliente) |

## 1. Compilar

Nos dois computadores, com o repositório na mesma versão:

```bash
python main.py tests/distribuido/teste1_servidor_calculadora.minipar
python main.py tests/distribuido/teste1_cliente_calculadora.minipar
```

Cada comando termina com `[SUCESSO] Executavel: ...` (no Windows, com `.exe`).

## 2. Testar num computador só (localhost)

Terminal 1 (servidor), **abra primeiro**:

```
.../teste1_servidor_calculadora
IP do computador cliente (computador_1): 127.0.0.1
```

Terminal 2 (cliente):

```
.../teste1_cliente_calculadora
IP do computador servidor (computador_2): 127.0.0.1
Operacao (+,-,*,/): *
Operando 1: 4
Operando 2: 6
Resultado: 24.000000
```

## 3. Em dois computadores

1. Descubra o IP de cada computador (`ipconfig` no Windows, `ip addr` no Linux/Mac).
2. Libere no firewall a porta **5101** no computador 2 e a porta **5102** no computador 1.
3. **Computador 2**: rode o servidor e digite o IP do computador 1.
4. **Computador 1**: em até 5 segundos, rode o cliente e digite o IP do computador 2.
5. Tire print dos dois terminais para o relatório.

## 4. Erros tratados

| Situação | O que aparece |
|---|---|
| Operando que não é número (ex.: `abc`) | Cliente: `[ERRO EXECUCAO] valor invalido para to_number: 'abc'` |
| Divisão por zero | Cliente: `Resultado: ERRO: divisao por zero` |
| Operação desconhecida (ex.: `%`) | Cliente: `Resultado: ERRO: operacao invalida (use +, -, * ou /)` |
| Servidor não está aberto | Cliente, depois de 5 s: `[ERRO EXECUCAO] Nao foi possivel conectar ao canal de comunicacao.` |

Os testes automáticos estão em `tests/test_teste1_dois_computadores.py`.
