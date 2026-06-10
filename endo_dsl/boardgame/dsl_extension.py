"""Parser estendido da DSL para jogos de tabuleiro — endo_dsl.boardgame.dsl_extension.

Adiciona a declaração ``boardgame "<nome>" { ... }`` à gramática Endo-DSL.
Reutiliza o tokenizer e a infraestrutura de erros do parser base.

Gramática extendida (EBNF):
    boardgame_decl   = "boardgame", string, "{", { boardgame_member }, "}" ;
    boardgame_member = metadata_block | objective_decl | mechanic_decl
                     | loop_decl | narrative_decl
                     | board_block | pieces_block | deck_block
                     | rules_block | gdc_block ;

    board_block  = "board", "{", { board_field | space_decl }, "}" ;
    board_field  = ("type" | "rows" | "cols" | "spaces"), ":", value ;
    space_decl   = "space", ident, "{", { space_field }, "}" ;
    space_field  = ("position" | "type" | "label" | "color" | "trigger"), ":", value ;

    pieces_block = "pieces", "{", { piece_decl }, "}" ;
    piece_decl   = "piece", ident, "{", { piece_field }, "}" ;
    piece_field  = ("name" | "per_player" | "shared" | "visual"), ":", value
                 | move_decl ;
    move_decl    = "move", "{", { ("direction"|"steps"|"condition"), ":", value }, "}" ;

    deck_block   = "deck", ident, "{", { deck_field | card_decl }, "}" ;
    deck_field   = "name", ":", string ;
    card_decl    = "card", ident, "{", { card_field }, "}" ;
    card_field   = ("text"|"effect"|"bloom"|"category"), ":", value ;

    rules_block  = "rules", "{", { rules_field }, "}" ;
    rules_field  = "turn_order"    , ":", ident
                 | "win_condition" , ":", string
                 | "dice"          , ":", dice_expr
                 | "players"       , ":", range
                 | "duration"      , ":", number
                 | phase_decl ;
    phase_decl   = "phase", ident, "{", { ("action"|"required"), ":", value }, "}" ;
    dice_expr    = number, "d", number ;  (* ex: 1d6 *)

    gdc_block    = "gdc", "{", { entry }, "}" ;
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from endo_dsl.dsl.ast import (
    Branch, Choice, GameplayLoop, Mechanic, Metadata, Narrative, Objective, Params, Transition,
)
from endo_dsl.dsl.bloom import Bloom, parse_bloom, suggest_bloom
from endo_dsl.dsl.parser import ParseError, Parser
from endo_dsl.dsl.tokenizer import LexError, Token, tokenize

from endo_dsl.boardgame.ast_nodes import (
    BoardGameSpec, BoardSpec, CardDeckSpec, CardSpec, DiceSpec,
    MoveRule, PhaseSpec, PieceSpec, SpaceSpec, TurnStructure, WinCondition,
)


# ---------------------------------------------------------------------------
# BoardGameParser — estende Parser com os novos construtos
# ---------------------------------------------------------------------------

class BoardGameParser(Parser):
    """Parser de descida recursiva para o dialeto boardgame da Endo-DSL."""

    def parse_boardgame_spec(self) -> BoardGameSpec:
        """Ponto de entrada: analisa uma declaração ``boardgame "..." { }``."""
        if not (self.check("IDENT") and self.cur.value == "boardgame"):
            raise ParseError(
                "a especificação boardgame deve começar com 'boardgame'",
                self.cur.line,
                self.cur.col,
                token=self._describe(self.cur),
                suggestion='comece com: boardgame "Título do Jogo" { ... }',
            )
        bg_tok = self.advance()
        title_tok = self.expect(
            "STRING", 'um título entre aspas para o boardgame',
            suggestion='ex.: boardgame "Trilha das Frações" { ... }',
        )
        spec = BoardGameSpec(title=str(title_tok.value))
        self.expect("LBRACE", "'{' para abrir o corpo do boardgame")

        while not self.check("RBRACE") and not self.at_end():
            if not self.check("IDENT"):
                raise ParseError(
                    "esperava uma declaração dentro do boardgame",
                    self.cur.line, self.cur.col,
                    token=self._describe(self.cur),
                )
            kw = self.cur.value
            if kw == "metadata":
                spec.metadata = self.parse_metadata()
            elif kw == "objective":
                spec.objectives.append(self.parse_objective())
            elif kw == "mechanic":
                spec.mechanics.append(self.parse_mechanic())
            elif kw == "loop":
                spec.loops.append(self.parse_loop())
            elif kw == "narrative":
                spec.narratives.append(self.parse_narrative())
            elif kw == "board":
                spec.board = self.parse_board()
            elif kw == "pieces":
                spec.pieces = self.parse_pieces()
            elif kw == "deck":
                spec.decks.append(self.parse_deck())
            elif kw == "rules":
                self._parse_rules_into(spec)
            elif kw == "gdc":
                spec.gdc_data = self.parse_gdc()
            else:
                _VALID = [
                    "metadata", "objective", "mechanic", "loop", "narrative",
                    "board", "pieces", "deck", "rules", "gdc",
                ]
                suggestion = self._suggest(kw, _VALID)
                raise ParseError(
                    "declaração desconhecida no corpo do boardgame",
                    self.cur.line, self.cur.col,
                    token=kw, suggestion=suggestion,
                )

        self.expect("RBRACE", "'}' para fechar o corpo do boardgame")
        return spec

    # ------------------------------------------------------------------ #
    # board { ... }
    # ------------------------------------------------------------------ #

    def parse_board(self) -> BoardSpec:
        self.expect_keyword("board")
        self.expect("LBRACE", "'{' após 'board'")
        board = BoardSpec()
        while not self.check("RBRACE") and not self.at_end():
            if self.check("IDENT") and self.cur.value == "space":
                board.spaces.append(self.parse_space())
                continue
            field_tok = self.expect("IDENT", "um campo do board")
            field = field_tok.value
            self.expect("COLON", f"':' após '{field}'")
            val = self.parse_value()
            if field == "type":
                board.type = str(val)
            elif field == "rows":
                board.rows = int(val)
            elif field == "cols":
                board.cols = int(val)
            elif field == "spaces":
                pass  # número informativo — espaços definidos como space decls
            else:
                raise ParseError(
                    "campo desconhecido em 'board'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, ["type", "rows", "cols", "spaces", "space"]),
                )
        self.expect("RBRACE", "'}' para fechar 'board'")
        return board

    def parse_space(self) -> SpaceSpec:
        self.expect_keyword("space")
        id_tok = self.expect("IDENT", "identificador da casa")
        space = SpaceSpec(id=str(id_tok.value))
        self.expect("LBRACE", f"'{{' após 'space {id_tok.value}'")
        while not self.check("RBRACE") and not self.at_end():
            field_tok = self.expect("IDENT", "um campo da casa")
            field = field_tok.value
            self.expect("COLON", f"':' após '{field}'")
            val = self.parse_value()
            if field == "position":
                space.position = val
            elif field == "type":
                space.type = str(val)
            elif field == "label":
                space.label = str(val)
            elif field == "color":
                space.color = str(val)
            elif field == "trigger":
                space.trigger = str(val)
            else:
                raise ParseError(
                    "campo desconhecido em 'space'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, ["position", "type", "label", "color", "trigger"]),
                )
        self.expect("RBRACE", "'}' para fechar 'space'")
        return space

    # ------------------------------------------------------------------ #
    # pieces { piece id { } ... }
    # ------------------------------------------------------------------ #

    def parse_pieces(self) -> List[PieceSpec]:
        self.expect_keyword("pieces")
        self.expect("LBRACE", "'{' após 'pieces'")
        pieces: List[PieceSpec] = []
        while not self.check("RBRACE") and not self.at_end():
            if self.check("IDENT") and self.cur.value == "piece":
                pieces.append(self.parse_piece())
            else:
                raise ParseError(
                    "esperava declaração 'piece' dentro de 'pieces'",
                    self.cur.line, self.cur.col, token=self._describe(self.cur),
                )
        self.expect("RBRACE", "'}' para fechar 'pieces'")
        return pieces

    def parse_piece(self) -> PieceSpec:
        self.expect_keyword("piece")
        id_tok = self.expect("IDENT", "identificador da peça")
        piece = PieceSpec(id=str(id_tok.value), name=str(id_tok.value))
        self.expect("LBRACE", f"'{{' após 'piece {id_tok.value}'")
        while not self.check("RBRACE") and not self.at_end():
            if self.check("IDENT") and self.cur.value == "move":
                piece.moves.append(self.parse_move_rule())
                continue
            field_tok = self.expect("IDENT", "campo da peça")
            field = field_tok.value
            self.expect("COLON", f"':' após '{field}'")
            val = self.parse_value()
            if field == "name":
                piece.name = str(val)
            elif field == "per_player":
                piece.per_player = int(val)
            elif field == "shared":
                piece.shared = bool(val)
            elif field == "visual":
                piece.visual = str(val)
            else:
                raise ParseError(
                    "campo desconhecido em 'piece'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, ["name", "per_player", "shared", "visual", "move"]),
                )
        self.expect("RBRACE", "'}' para fechar 'piece'")
        return piece

    def parse_move_rule(self) -> MoveRule:
        self.expect_keyword("move")
        self.expect("LBRACE", "'{' após 'move'")
        rule = MoveRule()
        while not self.check("RBRACE") and not self.at_end():
            field_tok = self.expect("IDENT", "campo da regra de movimento")
            field = field_tok.value
            self.expect("COLON", f"':' após '{field}'")
            val = self.parse_value()
            if field == "direction":
                rule.direction = str(val)
            elif field == "steps":
                rule.steps = int(val)
            elif field == "condition":
                rule.condition = str(val)
            else:
                raise ParseError(
                    "campo desconhecido em 'move'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, ["direction", "steps", "condition"]),
                )
        self.expect("RBRACE", "'}' para fechar 'move'")
        return rule

    # ------------------------------------------------------------------ #
    # deck id { card id { } ... }
    # ------------------------------------------------------------------ #

    def parse_deck(self) -> CardDeckSpec:
        self.expect_keyword("deck")
        id_tok = self.expect("IDENT", "identificador do baralho")
        deck = CardDeckSpec(id=str(id_tok.value), name=str(id_tok.value))
        self.expect("LBRACE", f"'{{' após 'deck {id_tok.value}'")
        while not self.check("RBRACE") and not self.at_end():
            if self.check("IDENT") and self.cur.value == "card":
                deck.cards.append(self.parse_card())
                continue
            field_tok = self.expect("IDENT", "campo do baralho")
            field = field_tok.value
            self.expect("COLON", f"':' após '{field}'")
            val = self.parse_value()
            if field == "name":
                deck.name = str(val)
            else:
                raise ParseError(
                    "campo desconhecido em 'deck'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, ["name", "card"]),
                )
        self.expect("RBRACE", "'}' para fechar 'deck'")
        return deck

    def parse_card(self) -> CardSpec:
        self.expect_keyword("card")
        id_tok = self.expect("IDENT", "identificador da carta")
        card = CardSpec(id=str(id_tok.value), text="")
        self.expect("LBRACE", f"'{{' após 'card {id_tok.value}'")
        while not self.check("RBRACE") and not self.at_end():
            field_tok = self.expect("IDENT", "campo da carta")
            field = field_tok.value
            self.expect("COLON", f"':' após '{field}'")
            if field == "bloom":
                card.bloom_level = self.parse_bloom_value()
            else:
                val = self.parse_value()
                if field == "text":
                    card.text = str(val)
                elif field == "effect":
                    card.effect = str(val)
                elif field == "category":
                    card.category = str(val)
                else:
                    raise ParseError(
                        "campo desconhecido em 'card'",
                        field_tok.line, field_tok.col, token=field,
                        suggestion=self._suggest(field, ["text", "effect", "bloom", "category"]),
                    )
        self.expect("RBRACE", "'}' para fechar 'card'")
        return card

    # ------------------------------------------------------------------ #
    # rules { ... }
    # ------------------------------------------------------------------ #

    def _parse_rules_into(self, spec: BoardGameSpec) -> None:
        """Lê o bloco rules e popula turn_structure, dice e win_conditions em spec."""
        self.expect_keyword("rules")
        self.expect("LBRACE", "'{' após 'rules'")

        turn = TurnStructure()
        dice = None
        win_conditions: List[WinCondition] = []

        while not self.check("RBRACE") and not self.at_end():
            if self.check("IDENT") and self.cur.value == "phase":
                turn.phases.append(self.parse_phase())
                continue
            field_tok = self.expect("IDENT", "campo das regras")
            field = field_tok.value
            self.expect("COLON", f"':' após '{field}'")
            if field == "turn_order":
                turn.order = str(self.parse_value())
            elif field == "win_condition":
                desc = str(self.parse_value())
                win_conditions.append(WinCondition(type="score", description=desc))
            elif field == "dice":
                # Espera "NdS" como string ou "N" como número
                dice = self._parse_dice_expr()
            elif field in ("players", "duration"):
                self.parse_value()  # consome e ignora (vai para metadata)
            else:
                raise ParseError(
                    "campo desconhecido em 'rules'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(
                        field,
                        ["turn_order", "win_condition", "dice", "players", "duration", "phase"],
                    ),
                )

        self.expect("RBRACE", "'}' para fechar 'rules'")
        spec.turn_structure = turn
        if dice:
            spec.dice = dice
        spec.win_conditions.extend(win_conditions)

    def _parse_dice_expr(self) -> DiceSpec:
        """Analisa expressão de dados: string "2d6" ou número simples."""
        tok = self.cur
        if tok.kind == "STRING":
            self.advance()
            raw = str(tok.value)
            if "d" in raw:
                parts = raw.lower().split("d", 1)
                try:
                    return DiceSpec(count=int(parts[0]), sides=int(parts[1]))
                except ValueError:
                    pass
            return DiceSpec()
        if tok.kind == "NUMBER":
            self.advance()
            return DiceSpec(count=1, sides=int(tok.value))
        if tok.kind == "IDENT":
            # Interpreta ident como "NdS"
            raw = str(tok.value)
            self.advance()
            if "d" in raw:
                parts = raw.lower().split("d", 1)
                try:
                    return DiceSpec(count=int(parts[0]), sides=int(parts[1]))
                except ValueError:
                    pass
            return DiceSpec()
        raise ParseError(
            "esperava expressão de dados (ex.: '2d6')",
            tok.line, tok.col, token=self._describe(tok),
        )

    def parse_phase(self) -> PhaseSpec:
        self.expect_keyword("phase")
        id_tok = self.expect("IDENT", "identificador da fase")
        phase = PhaseSpec(name=str(id_tok.value))
        self.expect("LBRACE", f"'{{' após 'phase {id_tok.value}'")
        while not self.check("RBRACE") and not self.at_end():
            field_tok = self.expect("IDENT", "campo da fase")
            field = field_tok.value
            self.expect("COLON", f"':' após '{field}'")
            val = self.parse_value()
            if field == "action":
                phase.action = str(val)
            elif field == "required":
                phase.required = bool(val)
            else:
                raise ParseError(
                    "campo desconhecido em 'phase'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, ["action", "required"]),
                )
        self.expect("RBRACE", "'}' para fechar 'phase'")
        return phase

    # ------------------------------------------------------------------ #
    # gdc { ... }  — armazena dados brutos do canvas GDC
    # ------------------------------------------------------------------ #

    def parse_gdc(self) -> Dict[str, Any]:
        self.expect_keyword("gdc")
        self.expect("LBRACE", "'{' após 'gdc'")
        data: Dict[str, Any] = {}
        while not self.check("RBRACE") and not self.at_end():
            key = self.expect("IDENT", "chave de dado GDC").value
            self.expect("COLON", f"':' após '{key}'")
            data[str(key)] = self.parse_value()
        self.expect("RBRACE", "'}' para fechar 'gdc'")
        return data


# ---------------------------------------------------------------------------
# Função pública de parse
# ---------------------------------------------------------------------------

def parse_boardgame_dsl(source: str) -> BoardGameSpec:
    """Tokeniza e analisa ``source`` como declaração boardgame.

    Retorna :class:`BoardGameSpec`. Levanta :class:`ParseError` em caso de erro.
    """
    try:
        tokens = tokenize(source)
    except LexError as exc:
        raise ParseError(exc.message, exc.line, exc.col) from exc

    parser = BoardGameParser(tokens)
    spec = parser.parse_boardgame_spec()

    if not parser.at_end():
        tok = parser.cur
        raise ParseError(
            "conteúdo inesperado após o fim da especificação boardgame",
            tok.line, tok.col, token=parser._describe(tok),
        )
    return spec


# ---------------------------------------------------------------------------
# compile_boardgame — valida semanticamente e retorna spec + issues
# ---------------------------------------------------------------------------

def compile_boardgame(source: str):
    """Analisa e valida semanticamente um boardgame DSL.

    Retorna tupla (BoardGameSpec, List[SemanticIssue]).
    """
    from endo_dsl.dsl.semantic import validate_semantics

    spec = parse_boardgame_dsl(source)
    game_spec = spec.to_game_spec()
    issues = validate_semantics(game_spec)
    return spec, issues
