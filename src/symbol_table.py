"""Componente Tabela de Simbolos do Compilador MiniPar 2026.2.

Realiza a interface I_TabelaSimbolos. Guarda:
  * variaveis e parametros, numa pilha de escopos (global, funcao, classe, bloco, for);
  * funcoes globais (func) com seus parametros;
  * classes com seus atributos e metodos.

O Analisador Semantico usa este componente somente atraves da interface
I_TabelaSimbolos (ver SemanticAnalyzer.__init__).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from interfaces import I_TabelaSimbolos


@dataclass
class Symbol:
    """Uma entrada da tabela: nome, tipo e, se for funcao/classe, sua assinatura."""
    name: str
    type: str
    params: List[str] = field(default_factory=list)
    attributes: Dict[str, str] = field(default_factory=dict)
    methods: Dict[str, List[str]] = field(default_factory=dict)


class TabelaSimbolos(I_TabelaSimbolos):
    """Componente Tabela de Simbolos: realiza a interface I_TabelaSimbolos."""

    def __init__(self) -> None:
        self._escopos: List[Dict[str, Symbol]] = [{}]   # escopo 0 = global
        self._funcoes: Dict[str, Symbol] = {}
        self._classes: Dict[str, Symbol] = {}

    # ---- Escopos de variaveis -------------------------------------------
    def entrar_escopo(self) -> None:
        self._escopos.append({})

    def sair_escopo(self) -> None:
        # O escopo global fica ate o fim da analise.
        if len(self._escopos) > 1:
            self._escopos.pop()

    def definir(self, simbolo: Symbol) -> bool:
        escopo_atual = self._escopos[-1]
        if simbolo.name in escopo_atual:
            return False
        escopo_atual[simbolo.name] = simbolo
        return True

    def buscar(self, nome: str) -> Optional[Symbol]:
        # Do escopo mais interno para o global (regra de escopo estatico).
        for escopo in reversed(self._escopos):
            if nome in escopo:
                return escopo[nome]
        return None

    @property
    def profundidade(self) -> int:
        """Quantos escopos estao abertos (1 = so o global)."""
        return len(self._escopos)

    # ---- Funcoes e classes ----------------------------------------------
    def registrar_funcao(self, simbolo: Symbol) -> None:
        self._funcoes[simbolo.name] = simbolo

    def buscar_funcao(self, nome: str) -> Optional[Symbol]:
        return self._funcoes.get(nome)

    def registrar_classe(self, simbolo: Symbol) -> None:
        self._classes[simbolo.name] = simbolo

    def buscar_classe(self, nome: str) -> Optional[Symbol]:
        return self._classes.get(nome)

    # ---- Exibicao -------------------------------------------------------
    def listar(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "globais": [asdict(s) for s in self._escopos[0].values()],
            "funcoes": [{"name": s.name, "params": list(s.params)} for s in self._funcoes.values()],
            "classes": [{"name": s.name, "attributes": dict(s.attributes),
                         "methods": {m: list(p) for m, p in s.methods.items()}}
                        for s in self._classes.values()],
        }
