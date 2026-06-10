"""Analisador sintático (parser) da Endo-DSL — RF01, RF02, RF03.

Implementa um parser de descida recursiva que produz a AST de
:mod:`endo_dsl.dsl.ast`. Erros sintáticos são reportados via :class:`ParseError`
com linha, coluna, token encontrado, o que era esperado e — quando possível —
uma sugestão de correção (campo desconhecido, nível de Bloom mal grafado, etc.).

A gramática formal correspondente está documentada em ``endo_dsl/dsl/grammar.ebnf``.
"""

from __future__ import annotations

import difflib
from typing import Any, List, Optional

from endo_dsl.dsl.ast import (
    Branch,
    Choice,
    GameSpec,
    GameplayLoop,
    Mechanic,
    Metadata,
    Narrative,
    Objective,
    Params,
    Transition,
)
from endo_dsl.dsl.bloom import Bloom, parse_bloom, suggest_bloom
from endo_dsl.dsl.tokenizer import LexError, Token, tokenize


class ParseError(Exception):
    """Erro sintático/léxico descritivo (RF03)."""

    def __init__(
        self,
        message: str,
        line: int,
        col: int,
        token: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.message = message
        self.line = line
        self.col = col
        self.token = token
        self.suggestion = suggestion
        super().__init__(self.format())

    def format(self) -> str:
        parts = [f"Erro de sintaxe (linha {self.line}, coluna {self.col}): {self.message}"]
        if self.token is not None:
            parts.append(f"  token inválido: {self.token!r}")
        if self.suggestion:
            parts.append(f"  sugestão: {self.suggestion}")
        return "\n".join(parts)

    def to_dict(self) -> dict:
        return {
            "line": self.line,
            "col": self.col,
            "message": self.message,
            "token": self.token,
            "suggestion": self.suggestion,
            "kind": "syntactic",
        }


# Campos permitidos por bloco — usados para sugerir correções de digitação.
_MECHANIC_FIELDS = ["type", "bloom", "addresses", "params", "description"]
_OBJECTIVE_FIELDS = ["description", "bloom"]
_LOOP_FIELDS = ["bloom", "description", "steps"]
_BRANCH_FIELDS = ["bloom", "text", "description", "choice"]


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------------ #
    # Utilidades de fluxo
    # ------------------------------------------------------------------ #
    @property
    def cur(self) -> Token:
        return self.tokens[self.pos]

    def at_end(self) -> bool:
        return self.cur.kind == "EOF"

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.kind != "EOF":
            self.pos += 1
        return tok

    def check(self, kind: str) -> bool:
        return self.cur.kind == kind

    def _describe(self, tok: Token) -> str:
        if tok.kind == "EOF":
            return "fim do arquivo"
        return tok.raw or str(tok.value)

    def expect(self, kind: str, what: str, suggestion: Optional[str] = None) -> Token:
        if self.cur.kind != kind:
            raise ParseError(
                f"esperava {what}",
                self.cur.line,
                self.cur.col,
                token=self._describe(self.cur),
                suggestion=suggestion,
            )
        return self.advance()

    def expect_keyword(self, word: str) -> Token:
        if self.cur.kind != "IDENT" or self.cur.value != word:
            raise ParseError(
                f"esperava a palavra-chave '{word}'",
                self.cur.line,
                self.cur.col,
                token=self._describe(self.cur),
            )
        return self.advance()

    # ------------------------------------------------------------------ #
    # Regras da gramática
    # ------------------------------------------------------------------ #
    def parse_spec(self) -> GameSpec:
        # Permite comentários/linhas em branco antes do bloco game (já tratados no lexer).
        if not (self.check("IDENT") and self.cur.value == "game"):
            raise ParseError(
                "a especificação deve começar com a declaração 'game'",
                self.cur.line,
                self.cur.col,
                token=self._describe(self.cur),
                suggestion='comece com: game "Título do Jogo" { ... }',
            )
        game_tok = self.advance()
        title_tok = self.expect("STRING", 'um título entre aspas para o jogo',
                                suggestion='ex.: game "Comparando Frações" { ... }')
        spec = GameSpec(line=game_tok.line, col=game_tok.col, title=str(title_tok.value))
        self.expect("LBRACE", "'{' para abrir o corpo do jogo")

        while not self.check("RBRACE") and not self.at_end():
            if not self.check("IDENT"):
                raise ParseError(
                    "esperava uma declaração (metadata, objective, mechanic, loop, narrative)",
                    self.cur.line,
                    self.cur.col,
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
            else:
                suggestion = self._suggest(
                    kw, ["metadata", "objective", "mechanic", "loop", "narrative"]
                )
                raise ParseError(
                    "declaração desconhecida no corpo do jogo",
                    self.cur.line,
                    self.cur.col,
                    token=kw,
                    suggestion=suggestion,
                )

        self.expect("RBRACE", "'}' para fechar o corpo do jogo")
        return spec

    def parse_metadata(self) -> Metadata:
        tok = self.expect_keyword("metadata")
        meta = Metadata(line=tok.line, col=tok.col)
        self.expect("LBRACE", "'{' após 'metadata'")
        while not self.check("RBRACE") and not self.at_end():
            key = self.expect("IDENT", "um nome de campo de metadados").value
            self.expect("COLON", f"':' após o campo '{key}'")
            meta.values[key] = self.parse_value()
        self.expect("RBRACE", "'}' para fechar o bloco 'metadata'")
        return meta

    def parse_objective(self) -> Objective:
        tok = self.expect_keyword("objective")
        name = self.expect("IDENT", "um identificador para o objetivo",
                           suggestion='ex.: objective OBJ_comparar { ... }').value
        obj = Objective(line=tok.line, col=tok.col, name=name)
        self.expect("LBRACE", f"'{{' após 'objective {name}'")
        while not self.check("RBRACE") and not self.at_end():
            field = self.expect("IDENT", "um campo do objetivo").value
            self.expect("COLON", f"':' após '{field}'")
            if field == "description":
                obj.description = str(self.parse_value())
            elif field == "bloom":
                obj.bloom = self.parse_bloom_value()
            else:
                raise ParseError(
                    "campo desconhecido em 'objective'",
                    self.cur.line, self.cur.col, token=field,
                    suggestion=self._suggest(field, _OBJECTIVE_FIELDS),
                )
        self.expect("RBRACE", "'}' para fechar o objetivo")
        return obj

    def parse_mechanic(self) -> Mechanic:
        tok = self.expect_keyword("mechanic")
        name = self.expect("IDENT", "um identificador para a mecânica").value
        mech = Mechanic(line=tok.line, col=tok.col, name=name)
        self.expect("LBRACE", f"'{{' após 'mechanic {name}'")
        while not self.check("RBRACE") and not self.at_end():
            field_tok = self.expect("IDENT", "um campo da mecânica")
            field = field_tok.value
            if field == "params":
                # bloco aninhado (sem ':')
                mech.params = self.parse_params()
                continue
            self.expect("COLON", f"':' após '{field}'")
            if field == "type":
                mech.type = str(self.parse_value())
            elif field == "bloom":
                mech.bloom = self.parse_bloom_value()
            elif field == "addresses":
                mech.addresses = self.parse_ident_list()
            elif field == "description":
                mech.description = str(self.parse_value())
            elif field == "source_component":
                mech.source_component = str(self.parse_value())
            else:
                raise ParseError(
                    "campo desconhecido em 'mechanic'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, _MECHANIC_FIELDS),
                )
        self.expect("RBRACE", "'}' para fechar a mecânica")
        return mech

    def parse_params(self) -> Params:
        # 'params' já consumido como IDENT pelo chamador
        tok = self.cur
        params = Params(line=tok.line, col=tok.col)
        self.expect("LBRACE", "'{' após 'params'")
        while not self.check("RBRACE") and not self.at_end():
            key = self.expect("IDENT", "um nome de parâmetro").value
            self.expect("COLON", f"':' após o parâmetro '{key}'")
            params.values[key] = self.parse_value()
        self.expect("RBRACE", "'}' para fechar o bloco 'params'")
        return params

    def parse_loop(self) -> GameplayLoop:
        tok = self.expect_keyword("loop")
        name = self.expect("IDENT", "um identificador para o loop").value
        loop = GameplayLoop(line=tok.line, col=tok.col, name=name)
        self.expect("LBRACE", f"'{{' após 'loop {name}'")
        while not self.check("RBRACE") and not self.at_end():
            field_tok = self.expect("IDENT", "um campo do loop")
            field = field_tok.value
            if field == "steps":
                loop.transitions = self.parse_steps()
                continue
            self.expect("COLON", f"':' após '{field}'")
            if field == "bloom":
                loop.bloom = self.parse_bloom_value()
            elif field == "description":
                loop.description = str(self.parse_value())
            else:
                raise ParseError(
                    "campo desconhecido em 'loop'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, _LOOP_FIELDS),
                )
        self.expect("RBRACE", "'}' para fechar o loop")
        return loop

    def parse_steps(self) -> List[Transition]:
        self.expect("LBRACE", "'{' após 'steps'")
        transitions: List[Transition] = []
        while not self.check("RBRACE") and not self.at_end():
            src_tok = self.expect("IDENT", "o estado de origem de uma transição")
            self.expect("ARROW", "'->' entre os estados da transição",
                        suggestion="use a forma: estado_origem -> estado_destino")
            dst_tok = self.expect("IDENT", "o estado de destino de uma transição")
            transitions.append(
                Transition(line=src_tok.line, col=src_tok.col,
                           src=str(src_tok.value), dst=str(dst_tok.value))
            )
        self.expect("RBRACE", "'}' para fechar o bloco 'steps'")
        return transitions

    def parse_narrative(self) -> Narrative:
        tok = self.expect_keyword("narrative")
        name = self.expect("IDENT", "um identificador para a narrativa").value
        narrative = Narrative(line=tok.line, col=tok.col, name=name)
        self.expect("LBRACE", f"'{{' após 'narrative {name}'")
        while not self.check("RBRACE") and not self.at_end():
            if self.check("IDENT") and self.cur.value == "branch":
                narrative.branches.append(self.parse_branch())
            else:
                raise ParseError(
                    "esperava uma declaração 'branch' dentro da narrativa",
                    self.cur.line, self.cur.col, token=self._describe(self.cur),
                    suggestion='ex.: branch inicio { text: "..." choice "Opção" -> outro_ramo }',
                )
        self.expect("RBRACE", "'}' para fechar a narrativa")
        return narrative

    def parse_branch(self) -> Branch:
        tok = self.expect_keyword("branch")
        name = self.expect("IDENT", "um identificador para o ramo").value
        branch = Branch(line=tok.line, col=tok.col, name=name)
        self.expect("LBRACE", f"'{{' após 'branch {name}'")
        while not self.check("RBRACE") and not self.at_end():
            field_tok = self.expect("IDENT", "um campo do ramo narrativo")
            field = field_tok.value
            if field == "choice":
                text_tok = self.expect("STRING", "o texto da escolha entre aspas")
                self.expect("ARROW", "'->' após o texto da escolha")
                target_tok = self.expect("IDENT", "o ramo de destino da escolha")
                branch.choices.append(
                    Choice(line=text_tok.line, col=text_tok.col,
                           text=str(text_tok.value), target=str(target_tok.value))
                )
                continue
            self.expect("COLON", f"':' após '{field}'")
            if field == "bloom":
                branch.bloom = self.parse_bloom_value()
            elif field == "text":
                branch.text = str(self.parse_value())
            elif field == "description":
                branch.description = str(self.parse_value())
            else:
                raise ParseError(
                    "campo desconhecido em 'branch'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, _BRANCH_FIELDS),
                )
        self.expect("RBRACE", "'}' para fechar o ramo")
        return branch

    # ------------------------------------------------------------------ #
    # Valores
    # ------------------------------------------------------------------ #
    def parse_value(self) -> Any:
        tok = self.cur
        if tok.kind in ("STRING", "NUMBER", "BOOL"):
            self.advance()
            return tok.value
        if tok.kind == "RANGE":
            self.advance()
            return list(tok.value)  # [start, end]
        if tok.kind == "IDENT":
            self.advance()
            return tok.value
        raise ParseError(
            "esperava um valor (texto, número, intervalo, booleano ou identificador)",
            tok.line, tok.col, token=self._describe(tok),
        )

    def parse_bloom_value(self) -> Bloom:
        tok = self.cur
        if tok.kind not in ("IDENT", "STRING"):
            raise ParseError(
                "esperava um nível da Taxonomia de Bloom",
                tok.line, tok.col, token=self._describe(tok),
                suggestion="níveis válidos: Lembrar, Compreender, Aplicar, Analisar, Avaliar, Criar",
            )
        self.advance()
        level = parse_bloom(str(tok.value))
        if level is None:
            sugg = suggest_bloom(str(tok.value))
            suggestion = (
                f"você quis dizer '{sugg[0]}'?"
                if sugg
                else "níveis válidos: Lembrar, Compreender, Aplicar, Analisar, Avaliar, Criar"
            )
            raise ParseError(
                "nível de Bloom inválido",
                tok.line, tok.col, token=str(tok.value), suggestion=suggestion,
            )
        return level

    def parse_ident_list(self) -> List[str]:
        idents = [str(self.expect("IDENT", "um identificador").value)]
        while self.check("COMMA"):
            self.advance()
            idents.append(str(self.expect("IDENT", "um identificador após ','").value))
        return idents

    # ------------------------------------------------------------------ #
    @staticmethod
    def _suggest(word: str, options: List[str]) -> Optional[str]:
        match = difflib.get_close_matches(word, options, n=1, cutoff=0.5)
        if match:
            return f"você quis dizer '{match[0]}'?"
        return f"campos válidos: {', '.join(options)}"


def parse(source: str) -> GameSpec:
    """Tokeniza e analisa ``source``, retornando a :class:`GameSpec`.

    Levanta :class:`ParseError` (com linha, coluna e sugestão) em caso de erro.
    """
    try:
        tokens = tokenize(source)
    except LexError as exc:
        raise ParseError(exc.message, exc.line, exc.col) from exc
    parser = Parser(tokens)
    spec = parser.parse_spec()
    if not parser.at_end():
        tok = parser.cur
        raise ParseError(
            "conteúdo inesperado após o fim da especificação",
            tok.line, tok.col, token=parser._describe(tok),
        )
    return spec
