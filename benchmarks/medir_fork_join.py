"""MINIP-33: mede o tempo do modo sequencial x paralelo do fork/join.

O MiniPar não tem cronômetro, então este script mede de fora:
1. compila cada programa com o main.py (o caminho normal do compilador);
2. roda o executável e anota a hora em que cada linha "marco" aparece
   (os programas já imprimem, por exemplo, "--- 1. Executando Modo Sequencial");
3. tempo de uma fase = hora do marco seguinte - hora do marco da fase;
4. repete N vezes (mais 1 de aquecimento, descartada) e usa a mediana;
5. só aceita a medição se a saída estiver certa (igual ao expected.txt,
   ou com a linha "RESULTADO: OK" na carga distribuída).

Programas medidos:
  t8, t9, t10  testes 8, 9 e 10 (sequencial x paralelo com threads)
  carga        benchmarks/carga_distribuida.minipar (sequencial x paralelo x
               distribuído, com 2 partes rodando num worker)

Uso (da raiz do repositório):
  python benchmarks/medir_fork_join.py                    # tudo, 5 repetições, worker local (127.0.0.1)
  python benchmarks/medir_fork_join.py --repeticoes 3 --programas t8,t9
  python benchmarks/medir_fork_join.py --programas carga --ip 192.168.0.20
      (usa o worker que já está rodando no outro computador:
       ./carga_distribuida --worker 7000, compilado do MESMO .minipar)

Saída: tabela no terminal e output/bench/<data-hora>/resultado.md e resultado.json.
Código de saída: 0 = todas as medições certas; 1 = algum erro (saída errada,
marco não encontrado, falha de compilação ou worker fora do ar).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import platform
import socket
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from run_artifacts import executable_path  # noqa: E402

PORTA_WORKER = 7000  # a mesma de "var porta" em carga_distribuida.minipar

MARCOS_TESTES = [
    ("sequencial", "--- 1. Executando Modo Sequencial", "--- 2. Executando Modo Paralelo"),
    ("paralelo", "--- 2. Executando Modo Paralelo", "RESULTADO DA AVALIACAO"),
]

PROGRAMAS = {
    "t8": {
        "titulo": "Teste 8 (4 núcleos)",
        "fonte": "tests/teste8_avaliacao_4_nucleos.minipar",
        "fases": MARCOS_TESTES,
        "esperado": "tests/expected_results/teste8_avaliacao_4_nucleos.expected.txt",
    },
    "t9": {
        "titulo": "Teste 9 (5 núcleos + Mandelbrot)",
        "fonte": "tests/teste9_avaliacao_5_nucleos_mandelbrot.minipar",
        "fases": MARCOS_TESTES,
        "esperado": "tests/expected_results/teste9_avaliacao_5_nucleos_mandelbrot.expected.txt",
    },
    "t10": {
        "titulo": "Teste 10 (6 núcleos + 2 fractais)",
        "fonte": "tests/teste10_avaliacao_6_nucleos_2_fractais.minipar",
        "fases": MARCOS_TESTES,
        "esperado": "tests/expected_results/teste10_avaliacao_6_nucleos_2_fractais.expected.txt",
    },
    "carga": {
        "titulo": "Carga distribuída (4 partes)",
        "fonte": "benchmarks/carga_distribuida.minipar",
        "fases": [
            ("sequencial", "--- 1. Sequencial", "--- 2. Paralelo local"),
            ("paralelo", "--- 2. Paralelo local", "--- 3. Distribuido"),
            ("distribuido", "--- 3. Distribuido", "--- FIM"),
        ],
        "linha_ok": "RESULTADO: OK",
        "usa_worker": True,
    },
}


# ---------------------------------------------------------------- medição


def tempos_das_fases(linhas_com_hora, fases):
    """Recebe [(hora, linha)] e devolve {fase: segundos}.

    Erro (ValueError) se algum marco não aparecer: melhor parar do que inventar número.
    """
    horas = {}
    for hora, linha in linhas_com_hora:
        for _, inicio, fim in fases:
            for marco in (inicio, fim):
                if marco in linha and marco not in horas:
                    horas[marco] = hora
    tempos = {}
    for nome, inicio, fim in fases:
        for marco in (inicio, fim):
            if marco not in horas:
                raise ValueError(f'marco não encontrado na saída: "{marco}"')
        tempos[nome] = horas[fim] - horas[inicio]
    return tempos


def rodar_uma_vez(exe, entrada, timeout=300):
    """Roda o executável e devolve ([(hora, linha)], saída inteira, código de saída)."""
    processo = subprocess.Popen(
        [exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", cwd=ROOT,
    )
    processo.stdin.write(entrada)
    processo.stdin.close()
    linhas = []
    limite = time.perf_counter() + timeout
    while True:
        linha = processo.stdout.readline()
        agora = time.perf_counter()
        if not linha:
            break
        linhas.append((agora, linha))
        if agora > limite:
            processo.kill()
            break
    codigo = processo.wait()
    return linhas, "".join(l for _, l in linhas), codigo


def saida_certa(programa, saida, codigo):
    """Confere a saída. Devolve (certo, motivo)."""
    if codigo != 0:
        return False, f"o programa terminou com código {codigo}"
    if "esperado" in programa:
        esperado = (ROOT / programa["esperado"]).read_text(encoding="utf-8")
        if saida.replace("\r\n", "\n") != esperado.replace("\r\n", "\n"):
            return False, "a saída é diferente do expected.txt"
    if "linha_ok" in programa and programa["linha_ok"] not in saida:
        return False, f'faltou a linha "{programa["linha_ok"]}"'
    return True, ""


def resumo(valores):
    return {
        "mediana": statistics.median(valores),
        "minimo": min(valores),
        "maximo": max(valores),
        "medidas": valores,
    }


# ---------------------------------------------------------------- worker


def porta_em_uso(porta):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", porta)) == 0


def iniciar_worker_local(exe):
    """Abre o mesmo executável em modo worker (127.0.0.1:7000) e espera ele ficar pronto."""
    if porta_em_uso(PORTA_WORKER):
        raise RuntimeError(f"a porta {PORTA_WORKER} já está em uso; feche o outro worker e rode de novo")
    worker = subprocess.Popen(
        [exe, "--worker", str(PORTA_WORKER)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", cwd=ROOT,
    )
    primeira = worker.stdout.readline()
    if "Esperando tarefas" not in primeira:
        worker.kill()
        raise RuntimeError(f"o worker não abriu: {primeira.strip()}")
    return worker


# ---------------------------------------------------------------- ambiente


def ambiente():
    cpu = platform.processor() or platform.machine()
    try:
        for linha in Path("/proc/cpuinfo").read_text().splitlines():
            if linha.startswith("model name"):
                cpu = linha.split(":", 1)[1].strip()
                break
    except OSError:
        pass

    def comando(*args):
        try:
            return subprocess.run(args, capture_output=True, text=True, cwd=ROOT, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return "?"

    return {
        "data": dt.datetime.now().strftime("%d/%m/%Y %H:%M"),
        "sistema": f"{platform.system()} {platform.release()}",
        "cpu": cpu,
        "nucleos_logicos": os.cpu_count(),
        "gpp": (comando("g++", "--version").splitlines() or ["?"])[0],
        "python": platform.python_version(),
        "commit": comando("git", "rev-parse", "--short", "HEAD") or "?",
    }


# ---------------------------------------------------------------- programa


def compilar(chave, pasta):
    programa = PROGRAMAS[chave]
    nome = Path(programa["fonte"]).stem
    destino = pasta / chave
    feito = subprocess.run(
        [sys.executable, "-X", "utf8", "-B", str(ROOT / "main.py"), programa["fonte"], nome,
         "--output-dir", str(destino)],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
    )
    exe = executable_path(str(destino), nome)
    if feito.returncode != 0 or not Path(exe).exists():
        raise RuntimeError("falha ao compilar:\n" + feito.stdout + feito.stderr)
    return exe


def medir_programa(chave, repeticoes, pasta, ip):
    programa = PROGRAMAS[chave]
    resultado = {"programa": chave, "titulo": programa["titulo"], "fonte": programa["fonte"]}
    print(f"\n>> {programa['titulo']}: compilando...", flush=True)
    exe = compilar(chave, pasta)

    worker = None
    entrada = ""
    if programa.get("usa_worker"):
        if ip:
            resultado["worker"] = f"{ip}:{PORTA_WORKER} (outro computador)"
        else:
            worker = iniciar_worker_local(exe)
            ip = "127.0.0.1"
            resultado["worker"] = f"127.0.0.1:{PORTA_WORKER} (mesmo computador)"
        entrada = ip + "\n"

    try:
        tempos = {nome: [] for nome, _, _ in programa["fases"]}
        for rodada in range(repeticoes + 1):
            linhas, saida, codigo = rodar_uma_vez(exe, entrada)
            certo, motivo = saida_certa(programa, saida, codigo)
            if not certo:
                raise RuntimeError(f"rodada {rodada}: {motivo}\n--- saída ---\n{saida}")
            medidos = tempos_das_fases(linhas, programa["fases"])
            if rodada == 0:
                print("   aquecimento (descartado) ok", flush=True)
                continue
            texto = "  ".join(f"{n} {s:.3f}s" for n, s in medidos.items())
            print(f"   rodada {rodada}/{repeticoes}: {texto}", flush=True)
            for nome, segundos in medidos.items():
                tempos[nome].append(segundos)
    finally:
        if worker is not None:
            worker.kill()
            worker.wait()

    resultado["fases"] = {nome: resumo(v) for nome, v in tempos.items()}
    base = resultado["fases"]["sequencial"]["mediana"]
    resultado["speedup"] = {}
    for nome in resultado["fases"]:
        if nome != "sequencial":
            mediana = resultado["fases"][nome]["mediana"]
            resultado["speedup"][nome] = base / mediana if mediana > 0 else 0.0
    return resultado


def tabela_markdown(env, resultados, repeticoes):
    linhas = [
        "# MINIP-33: medição do fork/join",
        "",
        f"- Data: {env['data']}  ",
        f"- Sistema: {env['sistema']}  ",
        f"- CPU: {env['cpu']} ({env['nucleos_logicos']} núcleos lógicos)  ",
        f"- Compilador: {env['gpp']} (`-std=c++20 -O3 -pthread`)  ",
        f"- Commit: `{env['commit']}`  ",
        f"- Medida: mediana de {repeticoes} rodadas (1 aquecimento descartado), tempo de parede de cada fase",
        "",
        "| Programa | Sequencial (s) | Paralelo (s) | Speedup paralelo | Distribuído (s) | Speedup distribuído | Worker |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in resultados:
        f = r["fases"]
        dist = f.get("distribuido")
        linhas.append(
            "| {t} | {s:.3f} | {p:.3f} | {sp:.2f} | {d} | {sd} | {w} |".format(
                t=r["titulo"], s=f["sequencial"]["mediana"], p=f["paralelo"]["mediana"],
                sp=r["speedup"]["paralelo"],
                d=f"{dist['mediana']:.3f}" if dist else "-",
                sd=f"{r['speedup']['distribuido']:.2f}" if dist else "-",
                w=r.get("worker", "-"),
            )
        )
    linhas += ["", "Speedup = tempo sequencial / tempo paralelo (mediana). Mínimos, máximos e cada rodada estão no resultado.json.", ""]
    return "\n".join(linhas)


def main(argv=None):
    args = argparse.ArgumentParser(description="MINIP-33: mede sequencial x paralelo do fork/join")
    args.add_argument("--repeticoes", type=int, default=5, help="rodadas medidas por programa (padrão 5)")
    args.add_argument("--programas", default="t8,t9,t10,carga", help="lista separada por vírgula: t8,t9,t10,carga")
    args.add_argument("--ip", help="IP do worker em outro computador (sem isso, abre um worker local)")
    args.add_argument("--saida", help="pasta dos resultados (padrão output/bench/<data-hora>)")
    opcoes = args.parse_args(argv)

    escolhidos = [p.strip() for p in opcoes.programas.split(",") if p.strip()]
    for chave in escolhidos:
        if chave not in PROGRAMAS:
            print(f"[ERRO] programa desconhecido: {chave} (use {', '.join(PROGRAMAS)})", file=sys.stderr)
            return 1
    if opcoes.repeticoes < 1:
        print("[ERRO] --repeticoes precisa ser 1 ou mais", file=sys.stderr)
        return 1

    pasta = Path(opcoes.saida) if opcoes.saida else ROOT / "output" / "bench" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    pasta.mkdir(parents=True, exist_ok=True)
    env = ambiente()
    print(f"[BENCH] {env['cpu']} | {env['nucleos_logicos']} núcleos lógicos | {env['sistema']} | commit {env['commit']}")

    resultados, erros = [], []
    for chave in escolhidos:
        try:
            resultados.append(medir_programa(chave, opcoes.repeticoes, pasta, opcoes.ip))
        except (RuntimeError, ValueError, subprocess.SubprocessError) as erro:
            erros.append({"programa": chave, "erro": str(erro)})
            print(f"[ERRO] {chave}: {erro}", file=sys.stderr)

    dados = {"ambiente": env, "repeticoes": opcoes.repeticoes, "resultados": resultados, "erros": erros}
    (pasta / "resultado.json").write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    if resultados:
        tabela = tabela_markdown(env, resultados, opcoes.repeticoes)
        (pasta / "resultado.md").write_text(tabela, encoding="utf-8")
        print("\n" + tabela)
    print(f"[BENCH] Resultados em {pasta}")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
