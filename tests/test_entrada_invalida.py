"""Tratamento de erros em tempo de execucao: entrada invalida no to_number e no parse_ints.

Antes o executavel abortava com "terminate called ... std::invalid_argument (stod)".
Agora ele encerra com codigo 1 e uma mensagem [ERRO EXECUCAO] clara.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from run_artifacts import executable_path  # noqa: E402

PROGRAMA = '''
seq {
    var n = to_number(input("Numero: "));
    print("dobro:", n * 2);
    var xs = parse_ints(input("Lista: "));
    print("tamanho:", len(xs));
}
'''


@unittest.skipUnless(shutil.which("g++"), "Requires g++")
class EntradaInvalida(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        fonte = Path(cls.tmp.name) / "entrada.minipar"
        fonte.write_text(PROGRAMA, encoding="utf-8")
        build = subprocess.run([sys.executable, str(ROOT / "main.py"), str(fonte), "entrada",
                                "--output-dir", cls.tmp.name],
                               capture_output=True, text=True, cwd=ROOT, timeout=180)
        assert build.returncode == 0, build.stdout + build.stderr
        cls.exe = executable_path(cls.tmp.name, "entrada")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def rodar(self, *linhas):
        return subprocess.run([str(self.exe)], input="\n".join(linhas) + "\n",
                              capture_output=True, text=True, timeout=30)

    def test_entradas_validas(self):
        r = self.rodar(" 2.5 ", "10 -3 80")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("dobro: 5", r.stdout)
        self.assertIn("tamanho: 3", r.stdout)

    def test_numero_invalido(self):
        for valor in ("abc", "12x", ""):
            with self.subTest(valor=valor):
                r = self.rodar(valor, "1")
                self.assertEqual(r.returncode, 1)
                self.assertIn("[ERRO EXECUCAO]", r.stderr)
                self.assertNotIn("terminate called", r.stderr)

    def test_lista_invalida(self):
        r = self.rodar("1", "10 abc 5")
        self.assertEqual(r.returncode, 1)
        self.assertIn("parse_ints encontrou 'abc'", r.stderr)


if __name__ == "__main__":
    unittest.main()
