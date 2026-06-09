"""Módulo de jogos de tabuleiro educativos — ENDO-GDC Board Game Engine.

Extensão da plataforma Endo-DSL para design e compilação de protótipos
de jogos de tabuleiro jogáveis a partir do canvas ENDO-GDC e da DSL estendida.
"""

from endo_dsl.boardgame.ast_nodes import BoardGameSpec
from endo_dsl.boardgame.compiler import compile_boardgame, compile_boardgame_source
from endo_dsl.boardgame.dsl_extension import parse_boardgame_dsl

__all__ = ["BoardGameSpec", "compile_boardgame", "compile_boardgame_source", "parse_boardgame_dsl"]
