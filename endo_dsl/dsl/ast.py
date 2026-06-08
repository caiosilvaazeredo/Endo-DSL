"""Árvore de Sintaxe Abstrata (AST) da Endo-DSL.

Cada nó carrega informação de posição (linha/coluna) para que validadores e o
compilador possam reportar problemas com precisão (RF03, RF04, RF20).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from endo_dsl.dsl.bloom import Bloom


@dataclass
class Node:
    """Nó base com posição no código-fonte."""

    line: int = 0
    col: int = 0


@dataclass
class Params(Node):
    """Bloco ``params { ... }`` — parâmetros configuráveis (conteúdo, dificuldade, domínio)."""

    values: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)


@dataclass
class Metadata(Node):
    """Bloco ``metadata { ... }`` — contexto educacional do jogo."""

    values: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)


@dataclass
class Objective(Node):
    """Objetivo pedagógico declarado (RF01)."""

    name: str = ""
    description: str = ""
    bloom: Optional[Bloom] = None


@dataclass
class Mechanic(Node):
    """Mecânica de jogo endógena (RF01) vinculada a um nível de Bloom (RF02)."""

    name: str = ""
    type: str = ""
    bloom: Optional[Bloom] = None
    addresses: List[str] = field(default_factory=list)  # nomes de objetivos
    params: Params = field(default_factory=Params)
    description: str = ""
    # Referência opcional ao componente da biblioteca que originou a mecânica
    # (preenchida pelo pipeline de geração — RF15 / jornada Fase 3).
    source_component: Optional[str] = None


@dataclass
class Transition(Node):
    """Transição ``origem -> destino`` dentro de um loop de jogabilidade."""

    src: str = ""
    dst: str = ""


@dataclass
class GameplayLoop(Node):
    """Loop de jogabilidade (RF01)."""

    name: str = ""
    bloom: Optional[Bloom] = None
    description: str = ""
    transitions: List[Transition] = field(default_factory=list)


@dataclass
class Choice(Node):
    """Escolha do jogador em uma ramificação narrativa."""

    text: str = ""
    target: str = ""


@dataclass
class Branch(Node):
    """Ramo de uma narrativa (RF01)."""

    name: str = ""
    bloom: Optional[Bloom] = None
    text: str = ""
    description: str = ""
    choices: List[Choice] = field(default_factory=list)


@dataclass
class Narrative(Node):
    """Narrativa ramificada (RF01)."""

    name: str = ""
    branches: List[Branch] = field(default_factory=list)


@dataclass
class GameSpec(Node):
    """Raiz da AST: a especificação completa de um jogo educacional endógeno."""

    title: str = ""
    metadata: Metadata = field(default_factory=Metadata)
    objectives: List[Objective] = field(default_factory=list)
    mechanics: List[Mechanic] = field(default_factory=list)
    loops: List[GameplayLoop] = field(default_factory=list)
    narratives: List[Narrative] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # Conveniências de consulta usadas por validadores / compilador.
    # ------------------------------------------------------------------ #
    def objective(self, name: str) -> Optional[Objective]:
        return next((o for o in self.objectives if o.name == name), None)

    def mechanic(self, name: str) -> Optional[Mechanic]:
        return next((m for m in self.mechanics if m.name == name), None)

    @property
    def bloom_levels(self) -> List[Bloom]:
        """Conjunto ordenado de níveis de Bloom presentes na especificação."""
        levels = set()
        for o in self.objectives:
            if o.bloom is not None:
                levels.add(o.bloom)
        for m in self.mechanics:
            if m.bloom is not None:
                levels.add(m.bloom)
        return sorted(levels)

    def to_dict(self) -> Dict[str, Any]:
        """Serialização leve da AST (usada em metadados/rastreabilidade — RF21, RF23)."""
        return {
            "title": self.title,
            "metadata": dict(self.metadata.values),
            "objectives": [
                {
                    "name": o.name,
                    "description": o.description,
                    "bloom": o.bloom.pt if o.bloom else None,
                }
                for o in self.objectives
            ],
            "mechanics": [
                {
                    "name": m.name,
                    "type": m.type,
                    "bloom": m.bloom.pt if m.bloom else None,
                    "addresses": list(m.addresses),
                    "params": dict(m.params.values),
                    "description": m.description,
                    "source_component": m.source_component,
                }
                for m in self.mechanics
            ],
            "loops": [
                {
                    "name": l.name,
                    "bloom": l.bloom.pt if l.bloom else None,
                    "description": l.description,
                    "transitions": [
                        {"src": t.src, "dst": t.dst} for t in l.transitions
                    ],
                }
                for l in self.loops
            ],
            "narratives": [
                {
                    "name": n.name,
                    "branches": [
                        {
                            "name": b.name,
                            "bloom": b.bloom.pt if b.bloom else None,
                            "text": b.text,
                            "description": b.description,
                            "choices": [
                                {"text": c.text, "target": c.target} for c in b.choices
                            ],
                        }
                        for b in n.branches
                    ],
                }
                for n in self.narratives
            ],
        }
