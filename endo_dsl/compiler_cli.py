"""CLI mínima do compilador Endo-DSL — ``endo-dslc`` (sem banco de dados).

Expõe APENAS o caminho de compilação DSL -> HTML5 (RF19–RF23). Nenhuma
dependência de SQLite, agentes LLM ou biblioteca web é importada aqui — toda a
cadeia (:mod:`endo_dsl.compiler.compiler`) é livre de banco de dados.

Uso::

    endo-dslc entrada.endo                 # compila, escreve ./<base>.html
    endo-dslc entrada.endo -o jogo.html    # define o arquivo de saída
    cat entrada.endo | endo-dslc -         # lê da entrada padrão
    endo-dslc entrada.endo --trace         # também grava rastreabilidade (RF23)
    endo-dslc entrada.endo --check         # apenas valida, não escreve nada

Esta CLI é o ponto de entrada da distribuição "compiler-only" e da build nativa.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Importa SOMENTE o compilador (caminho livre de banco de dados).
from endo_dsl import __version__
from endo_dsl.compiler.compiler import CompileError, compile_source
from endo_dsl.compiler import traceability


def _read_source(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _format_errors(exc: CompileError) -> str:
    lines = ["Falha de compilação Endo-DSL:"]
    for m in exc.messages:
        loc = ""
        if m.get("line"):
            loc = f" (linha {m['line']}, coluna {m.get('col', 0)})"
        lines.append(f"  - [{m.get('code', m.get('kind', 'erro'))}]{loc} {m.get('message', '')}")
        if m.get("suggestion"):
            lines.append(f"    sugestão: {m['suggestion']}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="endo-dslc",
        description="Compilador Endo-DSL: .endo -> protótipo HTML5 jogável "
                    "(sem banco de dados, sem servidor).",
    )
    p.add_argument("input", help="arquivo .endo de entrada (ou '-' para stdin)")
    p.add_argument("-o", "--output", help="arquivo HTML de saída "
                                          "(padrão: <base>.html ao lado da entrada)")
    p.add_argument("--trace", action="store_true",
                   help="também grava o documento de rastreabilidade HTML (RF23)")
    p.add_argument("--check", action="store_true",
                   help="apenas valida (parse + semântica), não escreve saída")
    p.add_argument("--no-strict", action="store_true",
                   help="não aborta em erros semânticos (gera mesmo com inconsistências)")
    p.add_argument("--version", action="version",
                   version=f"endo-dslc (Endo-DSL {__version__})")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        source = _read_source(args.input)
    except OSError as exc:
        print(f"Não foi possível ler a entrada: {exc}", file=sys.stderr)
        return 2

    try:
        result = compile_source(source, strict=not args.no_strict)
    except CompileError as exc:
        print(_format_errors(exc), file=sys.stderr)
        return 1

    for w in result.warnings:
        print(f"aviso [{w.get('code')}]: {w.get('message')}", file=sys.stderr)

    if args.check:
        print(f"OK — especificação válida ({len(result.bloom_levels)} níveis de Bloom, "
              f"{len(result.content_pack.get('stages', []))} mecânicas).", file=sys.stderr)
        return 0

    if args.output:
        out_path = Path(args.output)
    elif args.input == "-":
        out_path = Path("prototype.html")
    else:
        out_path = Path(args.input).with_suffix(".html")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result.html, encoding="utf-8")
    print(f"HTML5 gerado: {out_path}", file=sys.stderr)

    if args.trace and result.spec is not None:
        trace_path = out_path.with_suffix(".traceability.html")
        trace_path.write_text(traceability.as_html(result.spec), encoding="utf-8")
        print(f"Rastreabilidade gerada: {trace_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
