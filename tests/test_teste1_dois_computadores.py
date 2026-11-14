"""Teste 1 com cliente e servidor em executaveis separados (localhost).

Simula os dois computadores do enunciado (computador_1 = cliente,
computador_2 = servidor) rodando os dois executaveis com o IP 127.0.0.1.
"""
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from run_artifacts import executable_path  # noqa: E402

DIST = ROOT / "tests" / "distribuido"


@unittest.skipUnless(shutil.which("g++"), "Requires g++")
class Teste1DoisComputadores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.exe = {}
        for lado in ("servidor", "cliente"):
            nome = f"teste1_{lado}_calculadora"
            build = subprocess.run(
                [sys.executable, str(ROOT / "main.py"), str(DIST / f"{nome}.minipar"), nome,
                 "--output-dir", cls.tmp.name],
                capture_output=True, text=True, cwd=ROOT, timeout=180)
            assert build.returncode == 0, build.stdout + build.stderr
            cls.exe[lado] = executable_path(cls.tmp.name, nome)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def conversar(self, operacao, v1, v2):
        servidor = subprocess.Popen([self.exe["servidor"]], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            servidor.stdin.write("127.0.0.1\n")
            servidor.stdin.flush()
            time.sleep(0.3)
            cliente = subprocess.run([self.exe["cliente"]],
                                     input=f"127.0.0.1\n{operacao}\n{v1}\n{v2}\n",
                                     capture_output=True, text=True, timeout=20)
            saida_servidor, _ = servidor.communicate(timeout=20)
        finally:
            if servidor.poll() is None:
                servidor.kill()
        return cliente, saida_servidor

    def test_operacoes(self):
        for operacao, v1, v2, esperado in (("+", 2, 3, 5), ("*", 4, 6, 24), ("/", 9, 2, 4.5)):
            with self.subTest(operacao=operacao):
                cliente, servidor = self.conversar(operacao, v1, v2)
                self.assertEqual(cliente.returncode, 0, cliente.stderr)
                resultado = cliente.stdout.split("Resultado:")[1].split()[0]
                self.assertAlmostEqual(float(resultado), esperado)
                self.assertIn(f"Servidor recebeu: {operacao} {v1} {v2}", servidor)

    def test_divisao_por_zero(self):
        cliente, servidor = self.conversar("/", 1, 0)
        self.assertIn("ERRO: divisao por zero", cliente.stdout)
        self.assertIn("Divisao por zero recusada", servidor)

    def test_servidor_ausente(self):
        cliente = subprocess.run([self.exe["cliente"]], input="127.0.0.1\n+\n1\n2\n",
                                 capture_output=True, text=True, timeout=30)
        self.assertEqual(cliente.returncode, 1)
        self.assertIn("[ERRO EXECUCAO] Nao foi possivel conectar", cliente.stderr)
        self.assertNotIn("terminate called", cliente.stderr)


if __name__ == "__main__":
    unittest.main()
