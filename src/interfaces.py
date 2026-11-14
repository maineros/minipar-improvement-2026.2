"""Interfaces dos componentes de software do Compilador MiniPar 2026.2.

Python nao tem a palavra-chave ``interface`` do Java. Por isso, como pede o
material "Elementos de Implementacao Utilizando Componentes", cada interface e
uma classe abstrata (prefixo ``I_``) e cada componente e uma classe concreta que
herda dela e implementa todos os metodos abstratos.

Os componentes sao sempre usados atraves da interface. Exemplo:

    ilexico: I_Lexico = Lexer(codigo)   # o componente Lexer realiza I_Lexico
    tokens = ilexico.tokenize()

Componentes que realizam cada interface:

    I_Lexico            -> Lexer                (src/lexer.py)
    I_Sintatico         -> Parser               (src/parser.py)
    I_TabelaSimbolos    -> TabelaSimbolos       (src/symbol_table.py)
    I_Semantico         -> SemanticAnalyzer     (src/semantic.py)
    I_GeradorTAC        -> TACGenerator         (src/tac.py)
    I_GeradorCPP        -> CppCodeGenerator     (src/codegen.py)
    I_Orquestrador      -> MainCompiler         (src/orquestrador.py)
    I_Interface_Usuario -> MenuCLI (menu.py) e IDEWebApp (app.py)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class I_Lexico(ABC):
    """Analisador Lexico: transforma o codigo-fonte em uma lista de tokens."""

    @abstractmethod
    def tokenize(self) -> List[Any]:
        """Devolve a lista de tokens (o ultimo e sempre EOF)."""

    @property
    @abstractmethod
    def has_errors(self) -> bool:
        """True se algum erro lexico foi encontrado."""


class I_Sintatico(ABC):
    """Analisador Sintatico: transforma os tokens na arvore sintatica (AST)."""

    @abstractmethod
    def parse(self) -> Any:
        """Devolve o no raiz da AST (Program)."""


class I_TabelaSimbolos(ABC):
    """Tabela de Simbolos: guarda variaveis, funcoes e classes por escopo."""

    @abstractmethod
    def entrar_escopo(self) -> None:
        """Abre um escopo novo (bloco, funcao, classe, for)."""

    @abstractmethod
    def sair_escopo(self) -> None:
        """Fecha o escopo atual (o escopo global nunca e fechado)."""

    @abstractmethod
    def definir(self, simbolo: Any) -> bool:
        """Insere o simbolo no escopo atual. Devolve False se ja existia nele."""

    @abstractmethod
    def buscar(self, nome: str) -> Optional[Any]:
        """Procura o nome do escopo mais interno para o mais externo."""

    @abstractmethod
    def registrar_funcao(self, simbolo: Any) -> None:
        """Guarda a assinatura de uma funcao global (func)."""

    @abstractmethod
    def buscar_funcao(self, nome: str) -> Optional[Any]:
        """Devolve o simbolo da funcao global, ou None."""

    @abstractmethod
    def registrar_classe(self, simbolo: Any) -> None:
        """Guarda atributos e metodos de uma classe."""

    @abstractmethod
    def buscar_classe(self, nome: str) -> Optional[Any]:
        """Devolve o simbolo da classe, ou None."""

    @abstractmethod
    def listar(self) -> Dict[str, List[Dict[str, Any]]]:
        """Conteudo da tabela (para exibir na interface e no relatorio)."""


class I_Semantico(ABC):
    """Analisador Semantico: verifica declaracoes, escopo, tipos e uso de fork/join."""

    @abstractmethod
    def analyze(self, program: Any) -> bool:
        """Devolve True se o programa nao tem erros semanticos."""


class I_GeradorTAC(ABC):
    """Gerador de Codigo Intermediario de Tres Enderecos."""

    @abstractmethod
    def generate_text(self, program: Any) -> str:
        """Devolve o codigo de tres enderecos como texto."""

    @abstractmethod
    def generate(self, program: Any, output_name: str, output_dir: str = "output") -> str:
        """Grava o arquivo .tac e devolve o caminho dele."""


class I_GeradorCPP(ABC):
    """Gerador de Codigo C++ e chamada ao g++ (-O3) para gerar o executavel."""

    @abstractmethod
    def generate_text(self, program: Any) -> str:
        """Devolve o codigo C++ como texto."""

    @abstractmethod
    def generate(self, program: Any, output_name: str, output_dir: str = "output") -> bool:
        """Grava o .cpp, compila com g++ e devolve True se gerou o executavel."""


class I_Orquestrador(ABC):
    """Controle do compilador: liga os componentes na ordem das fases."""

    @abstractmethod
    def compile_file(self, source_path: str, output_name: str, output_dir: Optional[str] = None) -> bool:
        """Roda todas as fases sobre um arquivo .minipar e gera o executavel."""


class I_Interface_Usuario(ABC):
    """Interface com o usuario (terminal ou web)."""

    @abstractmethod
    def iniciar_interacao(self) -> None:
        """Abre a interface e fica atendendo o usuario."""

    @abstractmethod
    def exibir_resultados(self, texto: str) -> None:
        """Mostra um resultado ao usuario."""
