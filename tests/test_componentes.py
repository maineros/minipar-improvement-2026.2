"""Testes de integracao dos componentes do Compilador MiniPar 2026.2.

Verificam que:
  * cada componente realiza (herda e implementa) a sua interface I_*;
  * as interfaces sao abstratas (nao podem ser instanciadas);
  * a Tabela de Simbolos funciona sozinha e e usada pelo Analisador Semantico;
  * o Orquestrador liga os componentes somente pelas interfaces
    (componentes trocados por outros que realizam a mesma interface).
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from interfaces import (  # noqa: E402
    I_GeradorCPP, I_GeradorTAC, I_Interface_Usuario, I_Lexico, I_Orquestrador,
    I_Semantico, I_Sintatico, I_TabelaSimbolos,
)
from codegen import CppCodeGenerator  # noqa: E402
from lexer import Lexer  # noqa: E402
from orquestrador import MainCompiler  # noqa: E402
from parser import Parser  # noqa: E402
from semantic import SemanticAnalyzer  # noqa: E402
from symbol_table import Symbol, TabelaSimbolos  # noqa: E402
from tac import TACGenerator  # noqa: E402

PROGRAMA = '''
func dobro(x) { return x * 2; }
class Conta {
    var saldo = 0;
    func depositar(v) { this.saldo = this.saldo + v; }
}
seq {
    var c = new Conta();
    c.depositar(dobro(5));
    print(c.saldo);
}
'''


class RealizacaoDasInterfaces(unittest.TestCase):
    def test_cada_componente_realiza_sua_interface(self):
        pares = [
            (Lexer, I_Lexico), (Parser, I_Sintatico), (TabelaSimbolos, I_TabelaSimbolos),
            (SemanticAnalyzer, I_Semantico), (TACGenerator, I_GeradorTAC),
            (CppCodeGenerator, I_GeradorCPP), (MainCompiler, I_Orquestrador),
        ]
        for componente, interface in pares:
            with self.subTest(componente=componente.__name__):
                self.assertTrue(issubclass(componente, interface))
                self.assertFalse(getattr(componente, "__abstractmethods__", set()),
                                 f"{componente.__name__} deixou metodos sem implementar")

    def test_interfaces_de_usuario(self):
        import app
        import menu
        self.assertTrue(issubclass(menu.MenuCLI, I_Interface_Usuario))
        self.assertTrue(issubclass(app.IDEWebApp, I_Interface_Usuario))

    def test_interfaces_sao_abstratas(self):
        for interface in (I_Lexico, I_Sintatico, I_TabelaSimbolos, I_Semantico,
                          I_GeradorTAC, I_GeradorCPP, I_Orquestrador, I_Interface_Usuario):
            with self.subTest(interface=interface.__name__):
                with self.assertRaises(TypeError):
                    interface()


class TabelaDeSimbolos(unittest.TestCase):
    def test_escopos(self):
        tabela: I_TabelaSimbolos = TabelaSimbolos()
        self.assertTrue(tabela.definir(Symbol("x", "number")))
        self.assertFalse(tabela.definir(Symbol("x", "string")))  # redeclaracao
        tabela.entrar_escopo()
        self.assertTrue(tabela.definir(Symbol("x", "string")))   # sombreamento
        self.assertEqual(tabela.buscar("x").type, "string")
        tabela.sair_escopo()
        self.assertEqual(tabela.buscar("x").type, "number")
        self.assertIsNone(tabela.buscar("y"))
        tabela.sair_escopo()  # o escopo global nunca e removido
        self.assertIsNotNone(tabela.buscar("x"))

    def test_semantico_preenche_a_tabela_recebida(self):
        tabela = TabelaSimbolos()
        programa = Parser(Lexer(PROGRAMA).tokenize()).parse()
        self.assertTrue(SemanticAnalyzer(tabela).analyze(programa))
        conteudo = tabela.listar()
        self.assertEqual(conteudo["funcoes"], [{"name": "dobro", "params": ["x"]}])
        self.assertEqual(conteudo["classes"][0]["name"], "Conta")
        self.assertIn("depositar", conteudo["classes"][0]["methods"])


class FluxoDoOrquestrador(unittest.TestCase):
    def test_fases_em_sequencia_pelas_interfaces(self):
        compilador: I_Orquestrador = MainCompiler()
        lexico = compilador.lexico(PROGRAMA)
        tokens = lexico.tokenize()
        self.assertFalse(lexico.has_errors)
        programa = compilador.sintatico(tokens).parse()
        self.assertTrue(compilador.semantico().analyze(programa))
        self.assertIn("call dobro", compilador.gerador_tac().generate_text(programa))
        self.assertIn("class Conta", compilador.gerador_cpp().generate_text(programa))

    def test_componentes_podem_ser_trocados(self):
        """O orquestrador so conhece as interfaces: aceita outro componente."""
        chamadas = []

        class TabelaQueRegistra(TabelaSimbolos):
            def definir(self, simbolo):
                chamadas.append(simbolo.name)
                return super().definir(simbolo)

        class GeradorCppFalso(I_GeradorCPP):
            def generate_text(self, program):
                return "// falso"

            def generate(self, program, output_name, output_dir="output"):
                chamadas.append("cpp")
                return True

        compilador = MainCompiler(criar_tabela=TabelaQueRegistra,
                                  criar_gerador_cpp=GeradorCppFalso)
        with tempfile.TemporaryDirectory() as pasta:
            fonte = os.path.join(pasta, "p.minipar")
            Path(fonte).write_text(PROGRAMA, encoding="utf-8")
            self.assertTrue(compilador.compile_file(fonte, "p", pasta))
            self.assertTrue(os.path.exists(os.path.join(pasta, "p.tac")))
        self.assertIn("c", chamadas)
        self.assertEqual(chamadas[-1], "cpp")

    def test_erro_semantico_interrompe_antes_da_geracao(self):
        gerou = []

        class GeradorTacEspiao(TACGenerator):
            def generate(self, *args, **kwargs):
                gerou.append(True)
                return super().generate(*args, **kwargs)

        compilador = MainCompiler(criar_gerador_tac=GeradorTacEspiao)
        with tempfile.TemporaryDirectory() as pasta:
            fonte = os.path.join(pasta, "erro.minipar")
            Path(fonte).write_text("seq { print(nao_existe); }", encoding="utf-8")
            self.assertFalse(compilador.compile_file(fonte, "erro", pasta))
        self.assertEqual(gerou, [])


if __name__ == "__main__":
    unittest.main()
