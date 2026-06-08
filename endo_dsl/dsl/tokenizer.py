"""Analisador léxico (tokenizer) da Endo-DSL.

Produz uma sequência de ``Token`` com linha/coluna preservadas, base para
mensagens de erro descritivas (RF03). Suporta comentários ``//`` e ``/* */``,
strings entre aspas duplas com escapes, números inteiros/decimais, ranges
(``10..11``), o operador de transição ``->`` e a pontuação estrutural.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Token:
    kind: str  # IDENT, STRING, NUMBER, RANGE, BOOL, LBRACE, RBRACE, COLON, COMMA, ARROW, EOF
    value: object
    line: int
    col: int
    raw: str = ""

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Token({self.kind}, {self.value!r}, {self.line}:{self.col})"


class LexError(Exception):
    """Erro léxico com posição. Convertido em ParseError descritivo pelo parser."""

    def __init__(self, message: str, line: int, col: int):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col


_PUNCT = {
    "{": "LBRACE",
    "}": "RBRACE",
    ":": "COLON",
    ",": "COMMA",
}


def tokenize(source: str) -> List[Token]:
    """Converte ``source`` em lista de tokens, terminando com um token EOF."""
    tokens: List[Token] = []
    i = 0
    line = 1
    col = 1
    n = len(source)

    def advance(count: int = 1) -> None:
        nonlocal i, line, col
        for _ in range(count):
            if i < n and source[i] == "\n":
                line += 1
                col = 1
            else:
                col += 1
            i += 1

    while i < n:
        ch = source[i]

        # Espaços em branco
        if ch in " \t\r\n":
            advance()
            continue

        # Comentário de linha //
        if ch == "/" and i + 1 < n and source[i + 1] == "/":
            while i < n and source[i] != "\n":
                advance()
            continue

        # Comentário de bloco /* ... */
        if ch == "/" and i + 1 < n and source[i + 1] == "*":
            start_line, start_col = line, col
            advance(2)
            closed = False
            while i < n:
                if source[i] == "*" and i + 1 < n and source[i + 1] == "/":
                    advance(2)
                    closed = True
                    break
                advance()
            if not closed:
                raise LexError("comentário de bloco '/* */' não fechado", start_line, start_col)
            continue

        # Operador de transição ->
        if ch == "-" and i + 1 < n and source[i + 1] == ">":
            tokens.append(Token("ARROW", "->", line, col, "->"))
            advance(2)
            continue

        # Pontuação simples
        if ch in _PUNCT:
            tokens.append(Token(_PUNCT[ch], ch, line, col, ch))
            advance()
            continue

        # String
        if ch == '"':
            start_line, start_col = line, col
            advance()  # consome aspa inicial
            buf = []
            closed = False
            while i < n:
                c = source[i]
                if c == "\\" and i + 1 < n:
                    nxt = source[i + 1]
                    buf.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(nxt, nxt))
                    advance(2)
                    continue
                if c == '"':
                    advance()
                    closed = True
                    break
                if c == "\n":
                    raise LexError("string não fechada antes do fim da linha", start_line, start_col)
                buf.append(c)
                advance()
            if not closed:
                raise LexError("string não fechada", start_line, start_col)
            tokens.append(Token("STRING", "".join(buf), start_line, start_col, '"' + "".join(buf) + '"'))
            continue

        # Número ou range (123, 1.5, 10..11)
        if ch.isdigit() or (ch == "-" and i + 1 < n and source[i + 1].isdigit()):
            start_line, start_col = line, col
            start = i
            if ch == "-":
                advance()
            while i < n and source[i].isdigit():
                advance()
            # Range 10..11
            if i + 1 < n and source[i] == "." and source[i + 1] == ".":
                advance(2)
                range_start = source[start:i - 2]
                rs2 = i
                while i < n and source[i].isdigit():
                    advance()
                range_end = source[rs2:i]
                tokens.append(
                    Token("RANGE", (int(range_start), int(range_end)), start_line, start_col,
                          source[start:i])
                )
                continue
            # Decimal
            is_float = False
            if i < n and source[i] == ".":
                is_float = True
                advance()
                while i < n and source[i].isdigit():
                    advance()
            raw = source[start:i]
            value: object = float(raw) if is_float else int(raw)
            tokens.append(Token("NUMBER", value, start_line, start_col, raw))
            continue

        # Identificador / palavra-chave / booleano
        if ch.isalpha() or ch == "_":
            start_line, start_col = line, col
            start = i
            while i < n and (source[i].isalnum() or source[i] in "_."):
                advance()
            raw = source[start:i]
            if raw in ("true", "false"):
                tokens.append(Token("BOOL", raw == "true", start_line, start_col, raw))
            else:
                tokens.append(Token("IDENT", raw, start_line, start_col, raw))
            continue

        # Caractere inesperado
        raise LexError(f"caractere inesperado {ch!r}", line, col)

    tokens.append(Token("EOF", None, line, col, ""))
    return tokens
