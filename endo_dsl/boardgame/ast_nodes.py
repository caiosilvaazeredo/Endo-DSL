"""Nós da AST específicos de jogos de tabuleiro — endo_dsl.boardgame.ast_nodes.

Estende a AST base (endo_dsl.dsl.ast) com construtos para especificação
de jogos de tabuleiro físicos: tabuleiros, peças, baralhos, turnos e
condições de vitória. Mantém compatibilidade com GameSpec.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from endo_dsl.dsl.ast import GameSpec, Metadata, Objective, Mechanic, GameplayLoop, Narrative
from endo_dsl.dsl.bloom import Bloom


# ---------------------------------------------------------------------------
# Tabuleiro
# ---------------------------------------------------------------------------

@dataclass
class SpaceSpec:
    """Descreve uma casa (espaço) do tabuleiro."""

    id: str
    # Posição: (row, col) para grade, índice inteiro para trilha
    position: Any = None                      # tuple(row,col) | int | None
    type: str = "normal"                      # normal|start|end|special|penalty|bonus
    label: str = ""
    color: str = ""
    trigger: Optional[str] = None            # mechanic id ou None


@dataclass
class BoardSpec:
    """Especificação do tabuleiro físico."""

    type: str = "track"                       # grid|track|map|cards_only
    rows: int = 0
    cols: int = 0
    spaces: List[SpaceSpec] = field(default_factory=list)

    @property
    def space_count(self) -> int:
        return len(self.spaces)


# ---------------------------------------------------------------------------
# Peças
# ---------------------------------------------------------------------------

@dataclass
class MoveRule:
    """Regra de movimento de uma peça."""

    direction: str = "any"                   # up|down|left|right|diagonal|any|L
    steps: int = 1
    condition: str = ""                      # expressão ou vazio


@dataclass
class PieceSpec:
    """Especificação de um tipo de peça do jogo."""

    id: str
    name: str
    per_player: int = 1
    shared: bool = False
    visual: str = "⬤"                        # emoji ou cor
    moves: List[MoveRule] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------------

@dataclass
class DiceSpec:
    """Configuração de dados usados no jogo."""

    count: int = 1
    sides: int = 6
    modifier: int = 0                        # +/- fixo ao resultado


# ---------------------------------------------------------------------------
# Baralhos e Cartas
# ---------------------------------------------------------------------------

@dataclass
class CardSpec:
    """Especificação de uma carta individual."""

    id: str
    text: str
    effect: str = ""
    bloom_level: Optional[Bloom] = None
    category: str = "general"


@dataclass
class CardDeckSpec:
    """Especificação de um baralho de cartas."""

    id: str
    name: str
    cards: List[CardSpec] = field(default_factory=list)

    @property
    def card_count(self) -> int:
        return len(self.cards)


# ---------------------------------------------------------------------------
# Estrutura de turno
# ---------------------------------------------------------------------------

@dataclass
class PhaseSpec:
    """Uma fase dentro de um turno."""

    name: str
    action: str = ""
    required: bool = True


@dataclass
class TurnStructure:
    """Define como os turnos do jogo se organizam."""

    order: str = "clockwise"                 # clockwise|counter|simultaneous|bidding
    phases: List[PhaseSpec] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Condições de vitória
# ---------------------------------------------------------------------------

@dataclass
class WinCondition:
    """Define quando e como um jogo termina com vitória."""

    type: str = "score"                      # score|elimination|collection|cooperative|race
    target: Any = None                       # valor alvo (pontos, peças etc.)
    description: str = ""


# ---------------------------------------------------------------------------
# Especificação raiz de jogo de tabuleiro
# ---------------------------------------------------------------------------

@dataclass
class BoardGameSpec:
    """Raiz da AST extendida para jogos de tabuleiro educacionais.

    Combina os campos de GameSpec com construtos físicos de tabuleiro.
    Pode ser serializado para o GDC canvas e compilado para regras jogáveis.
    """

    # Campos herdados de GameSpec (duplicados para independência)
    title: str = ""
    metadata: Metadata = field(default_factory=Metadata)
    objectives: List[Objective] = field(default_factory=list)
    mechanics: List[Mechanic] = field(default_factory=list)
    loops: List[GameplayLoop] = field(default_factory=list)
    narratives: List[Narrative] = field(default_factory=list)

    # Campos específicos de jogo de tabuleiro
    board: Optional[BoardSpec] = None
    pieces: List[PieceSpec] = field(default_factory=list)
    decks: List[CardDeckSpec] = field(default_factory=list)
    dice: Optional[DiceSpec] = None
    turn_structure: Optional[TurnStructure] = None
    win_conditions: List[WinCondition] = field(default_factory=list)

    # GDC canvas data (JSON blob armazenado como dict)
    gdc_data: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------ #
    # Conveniências
    # ------------------------------------------------------------------ #
    def objective(self, name: str) -> Optional[Objective]:
        return next((o for o in self.objectives if o.name == name), None)

    def mechanic(self, name: str) -> Optional[Mechanic]:
        return next((m for m in self.mechanics if m.name == name), None)

    def to_game_spec(self) -> GameSpec:
        """Converte para GameSpec base (para usar com validadores existentes)."""
        return GameSpec(
            title=self.title,
            metadata=self.metadata,
            objectives=list(self.objectives),
            mechanics=list(self.mechanics),
            loops=list(self.loops),
            narratives=list(self.narratives),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialização completa para JSON/GDC canvas."""
        def _bloom(b: Optional[Bloom]) -> Optional[str]:
            return b.pt if b else None

        return {
            "title": self.title,
            "metadata": dict(self.metadata.values),
            "objectives": [
                {"name": o.name, "description": o.description, "bloom": _bloom(o.bloom)}
                for o in self.objectives
            ],
            "mechanics": [
                {
                    "name": m.name,
                    "type": m.type,
                    "bloom": _bloom(m.bloom),
                    "addresses": list(m.addresses),
                    "params": dict(m.params.values),
                    "description": m.description,
                }
                for m in self.mechanics
            ],
            "board": {
                "type": self.board.type,
                "rows": self.board.rows,
                "cols": self.board.cols,
                "spaces": [
                    {
                        "id": s.id,
                        "position": s.position,
                        "type": s.type,
                        "label": s.label,
                        "color": s.color,
                        "trigger": s.trigger,
                    }
                    for s in self.board.spaces
                ],
            } if self.board else None,
            "pieces": [
                {
                    "id": p.id,
                    "name": p.name,
                    "per_player": p.per_player,
                    "shared": p.shared,
                    "visual": p.visual,
                }
                for p in self.pieces
            ],
            "dice": {
                "count": self.dice.count,
                "sides": self.dice.sides,
                "modifier": self.dice.modifier,
            } if self.dice else None,
            "decks": [
                {
                    "id": d.id,
                    "name": d.name,
                    "card_count": d.card_count,
                }
                for d in self.decks
            ],
            "turn_structure": {
                "order": self.turn_structure.order,
                "phases": [
                    {"name": ph.name, "action": ph.action, "required": ph.required}
                    for ph in self.turn_structure.phases
                ],
            } if self.turn_structure else None,
            "win_conditions": [
                {"type": wc.type, "target": wc.target, "description": wc.description}
                for wc in self.win_conditions
            ],
            "gdc_data": self.gdc_data,
        }
