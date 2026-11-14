"""MINIP-33: o script de medição benchmarks/medir_fork_join.py."""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

import medir_fork_join as bench  # noqa: E402


class TemposDasFasesTests(unittest.TestCase):
    FASES = [("sequencial", "--- 1.", "--- 2."), ("paralelo", "--- 2.", "RESULTADO")]

    def test_calcula_o_tempo_entre_os_marcos(self):
        linhas = [(0.0, "inicio\n"), (1.0, "--- 1. Seq\n"), (3.5, "--- 2. Par\n"), (4.0, "RESULTADO\n")]
        tempos = bench.tempos_das_fases(linhas, self.FASES)
        self.assertAlmostEqual(tempos["sequencial"], 2.5)
        self.assertAlmostEqual(tempos["paralelo"], 0.5)

    def test_para_com_erro_se_faltar_um_marco(self):
        linhas = [(1.0, "--- 1. Seq\n"), (2.0, "--- 2. Par\n")]
        with self.assertRaisesRegex(ValueError, "RESULTADO"):
            bench.tempos_das_fases(linhas, self.FASES)

    def test_saida_diferente_do_esperado_nao_conta(self):
        programa = bench.PROGRAMAS["t8"]
        certo, motivo = bench.saida_certa(programa, "outra coisa\n", 0)
        self.assertFalse(certo)
        self.assertIn("expected", motivo)

    def test_marcos_existem_nos_testes_8_9_10_e_na_carga(self):
        for chave, programa in bench.PROGRAMAS.items():
            fonte = (ROOT / programa["fonte"]).read_text(encoding="utf-8")
            for _, inicio, fim in programa["fases"]:
                self.assertIn(inicio, fonte, chave)
                self.assertIn(fim, fonte, chave)


@unittest.skipIf(shutil.which("g++") is None, "g++ nao encontrado")
class MedicaoDeVerdadeTests(unittest.TestCase):
    def medir(self, programas):
        output = ROOT / "output"
        output.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="bench-", dir=output) as pasta:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as erros:
                codigo = bench.main(["--programas", programas, "--repeticoes", "1", "--saida", pasta])
            self.assertEqual(codigo, 0, erros.getvalue())
            dados = json.loads((Path(pasta) / "resultado.json").read_text(encoding="utf-8"))
            self.assertTrue((Path(pasta) / "resultado.md").exists())
        return dados

    def test_teste8_mede_sequencial_e_paralelo(self):
        dados = self.medir("t8")
        r = dados["resultados"][0]
        self.assertGreater(r["fases"]["sequencial"]["mediana"], 0)
        self.assertGreater(r["speedup"]["paralelo"], 0)

    def test_carga_mede_o_modo_distribuido_com_worker_local(self):
        if bench.porta_em_uso(bench.PORTA_WORKER):
            self.skipTest("porta 7000 ocupada")
        dados = self.medir("carga")
        r = dados["resultados"][0]
        self.assertIn("distribuido", r["fases"])
        self.assertIn("127.0.0.1", r["worker"])


if __name__ == "__main__":
    unittest.main()
