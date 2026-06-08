"""Módulo 4 — Compilador e Gerador de Protótipos (RF19–RF23)."""

from endo_dsl.compiler.compiler import (
    CompileResult,
    CompileError,
    compile_source,
    compile_spec,
    reparametrize_content,
)

__all__ = [
    "CompileResult",
    "CompileError",
    "compile_source",
    "compile_spec",
    "reparametrize_content",
]
