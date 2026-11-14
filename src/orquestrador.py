"""Componente Orquestrador (Controle) do Compilador MiniPar 2026.2.

Realiza a interface I_Orquestrador. Liga os componentes na ordem das fases:

    Lexer -> Parser -> SemanticAnalyzer (+ TabelaSimbolos) -> TACGenerator -> CppCodeGenerator -> g++

Cada componente e criado por uma "fabrica" e guardado num atributo do tipo da
interface que ele realiza. Assim o orquestrador so conhece as interfaces: para
trocar um componente basta passar outra fabrica no construtor.
"""
from __future__ import annotations

import os
import sys
from typing import Callable, List, Optional

from interfaces import (
    I_GeradorCPP, I_GeradorTAC, I_Lexico, I_Orquestrador, I_Semantico, I_Sintatico,
    I_TabelaSimbolos,
)
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from symbol_table import TabelaSimbolos
from tac import TACGenerator
from codegen import CppCodeGenerator


class MainCompiler(I_Orquestrador):
    """Componente Orquestrador: realiza a interface I_Orquestrador."""

    def __init__(
        self,
        criar_lexico: Callable[[str], I_Lexico] = Lexer,
        criar_sintatico: Callable[[List], I_Sintatico] = Parser,
        criar_tabela: Callable[[], I_TabelaSimbolos] = TabelaSimbolos,
        criar_semantico: Callable[[I_TabelaSimbolos], I_Semantico] = SemanticAnalyzer,
        criar_gerador_tac: Callable[[], I_GeradorTAC] = TACGenerator,
        criar_gerador_cpp: Callable[[], I_GeradorCPP] = CppCodeGenerator,
    ) -> None:
        self.criar_lexico = criar_lexico
        self.criar_sintatico = criar_sintatico
        self.criar_tabela = criar_tabela
        self.criar_semantico = criar_semantico
        self.criar_gerador_tac = criar_gerador_tac
        self.criar_gerador_cpp = criar_gerador_cpp

    # ---- Uma fase de cada vez (usado pela interface web) ------------------
    def lexico(self, codigo: str) -> I_Lexico:
        return self.criar_lexico(codigo)

    def sintatico(self, tokens: List) -> I_Sintatico:
        return self.criar_sintatico(tokens)

    def semantico(self) -> I_Semantico:
        return self.criar_semantico(self.criar_tabela())

    def gerador_tac(self) -> I_GeradorTAC:
        return self.criar_gerador_tac()

    def gerador_cpp(self) -> I_GeradorCPP:
        return self.criar_gerador_cpp()

    # ---- Todas as fases (terminal e botao Compilar da web) ---------------
    def compile_file(self, source_path: str, output_name: str, output_dir: Optional[str] = None) -> bool:
        """Processa as fases do compilador em um arquivo alvo."""
        from run_artifacts import create_run_dir

        print(f"\n=== Compilando: {source_path} ===")
        output_dir = output_dir or create_run_dir()
        output_name = os.path.basename(output_name)
        print(f"[OUTPUT] {os.path.abspath(output_dir)}")
        try:
            with open(source_path, encoding="utf-8") as f:
                source_code = f.read()
        except FileNotFoundError:
            print(f"[ERRO] Arquivo nao encontrado: {source_path}", file=sys.stderr)
            return False

        print("[Fase 1] Analise Lexica e Sintatica...")
        ilexico = self.lexico(source_code)
        tokens = ilexico.tokenize()

        # Para a compilacao se o lexer achou erros (caractere invalido, texto sem fechar...).
        if ilexico.has_errors:
            for error in ilexico.errors:
                print(error, file=sys.stderr)
            print("[ERRO] Falha na Analise Lexica. Compilacao abortada.", file=sys.stderr)
            return False

        isintatico = self.sintatico(tokens)
        program = isintatico.parse()

        print("[Fase 2] Analise Semantica e Tabela de Simbolos...")
        isemantico = self.semantico()
        if not isemantico.analyze(program):
            print("[ERRO] Falha na Analise Semantica. Compilacao abortada.", file=sys.stderr)
            return False

        print("[Fase 3] Geracao de Codigo Intermediario (TAC - 3 enderecos)...")
        tac_path = self.gerador_tac().generate(program, output_name, output_dir)
        print(f"[TAC] Arquivo gerado: {tac_path}")

        print("[Fase 4] Transpilacao e Chamada do GCC (-O3)...")
        return self.gerador_cpp().generate(program, output_name, output_dir)
