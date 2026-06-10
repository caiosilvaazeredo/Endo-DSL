"""CLI mínima do compilador Endo-DSL — ``endo-dslc`` (sem banco de dados).

Expõe o caminho de compilação DSL/boardgame -> HTML5 (RF19–RF23). Nenhuma
dependência de SQLite, agentes LLM ou biblioteca web é importada aqui.

Uso::

    endo-dslc entrada.endo                     # compila DSL educativo -> HTML5
    endo-dslc entrada.endo -o jogo.html        # define o arquivo de saída
    cat entrada.endo | endo-dslc -             # lê da entrada padrão
    endo-dslc entrada.endo --trace             # também grava rastreabilidade (RF23)
    endo-dslc entrada.endo --check             # apenas valida, não escreve nada
    endo-dslc jogo.endo --boardgame            # compila jogo de tabuleiro boardgame{}
    endo-dslc - --boardgame --domain Ciências --topic ecossistemas
    endo-dslc --template trilha -o trilha.html # gera HTML5 a partir de arquétipo

Esta CLI é o ponto de entrada da distribuição "compiler-only" e da build nativa.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
    p.add_argument("input", nargs="?", default=None,
                   help="arquivo .endo de entrada (ou '-' para stdin). "
                        "Opcional se --template for usado.")
    p.add_argument("-o", "--output", help="arquivo HTML de saída "
                                          "(padrão: <base>.html ao lado da entrada)")
    p.add_argument("--trace", action="store_true",
                   help="também grava o documento de rastreabilidade HTML (RF23)")
    p.add_argument("--check", action="store_true",
                   help="apenas valida (parse + semântica), não escreve saída")
    p.add_argument("--no-strict", action="store_true",
                   help="não aborta em erros semânticos (gera mesmo com inconsistências)")
    # Board game flags
    p.add_argument("--boardgame", action="store_true",
                   help="compila entrada como jogo de tabuleiro (bloco boardgame{} da DSL)")
    p.add_argument("--template", metavar="ARQUÉTIPO",
                   help="gera HTML5 a partir de um arquétipo de tabuleiro sem arquivo de entrada. "
                        "Arquétipos: trilha, quiz_battle, memory_match, word_race, "
                        "strategy_grid, cooperative_quest, auction_economy, deduction_mystery")
    p.add_argument("--domain", default="generico",
                   help="domínio do conteúdo para --boardgame / --template (padrão: generico)")
    p.add_argument("--topic", default="",
                   help="tópico do conteúdo para --boardgame / --template")
    p.add_argument("--players", type=int, default=2,
                   help="número de jogadores para --template (padrão: 2)")
    p.add_argument("--bloom", default="Analisar",
                   help="nível Bloom alvo para --template (padrão: Analisar)")
    p.add_argument("--title", default="",
                   help="título do jogo para --template")
    p.add_argument("--version", action="version",
                   version=f"endo-dslc (Endo-DSL {__version__})")
    return p


def _compile_template(args) -> tuple[str, str]:
    """Gera HTML5 a partir de um arquétipo de tabuleiro (sem arquivo .endo)."""
    from endo_dsl.boardgame.templates import generate_template
    title = args.title or f"Jogo {args.template.replace('_', ' ').title()}"
    ctx = {
        "title": title,
        "domain": args.domain,
        "topic": args.topic or args.domain,
        "bloom_target": args.bloom,
        "age_range": "10-14",
        "players": args.players,
        "duration": 20,
        "objective_text": f"Praticar {args.topic or args.domain} com {args.bloom}",
    }
    dsl_source = generate_template(args.template, ctx)
    return dsl_source, title


def _compile_boardgame(source: str, args) -> str:
    """Compila bloco boardgame{} da DSL para HTML5."""
    from endo_dsl.boardgame import compile_boardgame_source
    result = compile_boardgame_source(source, domain=args.domain or None,
                                      topic=args.topic or None)
    return result["html"]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # --template: gera DSL de arquétipo, depois compila como boardgame
    if args.template:
        try:
            dsl_source, title = _compile_template(args)
        except (ImportError, KeyError, ValueError) as exc:
            print(f"Erro ao gerar template '{args.template}': {exc}", file=sys.stderr)
            return 1
        out_name = args.output or f"{args.template}.html"
        out_path = Path(out_name)
        if args.check:
            print(f"OK — template '{args.template}' gerado ({len(dsl_source)} chars).",
                  file=sys.stderr)
            return 0
        try:
            html = _compile_boardgame(dsl_source, args)
        except Exception as exc:
            print(f"Erro ao compilar template: {exc}", file=sys.stderr)
            return 1
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        print(f"HTML5 gerado: {out_path}  ({len(html):,} bytes)", file=sys.stderr)
        return 0

    if args.input is None:
        print("endo-dslc: erro: forneça um arquivo de entrada ou use --template.",
              file=sys.stderr)
        return 2

    try:
        source = _read_source(args.input)
    except OSError as exc:
        print(f"Não foi possível ler a entrada: {exc}", file=sys.stderr)
        return 2

    # --boardgame: compila bloco boardgame{}
    if args.boardgame:
        if args.check:
            print("OK — verificação boardgame não implementada sem compilar.", file=sys.stderr)
            return 0
        try:
            html = _compile_boardgame(source, args)
        except Exception as exc:
            print(f"Erro ao compilar boardgame: {exc}", file=sys.stderr)
            return 1
        out_path = Path(args.output) if args.output else Path(
            args.input if args.input != "-" else "boardgame").with_suffix(".html")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding="utf-8")
        print(f"HTML5 gerado: {out_path}  ({len(html):,} bytes)", file=sys.stderr)
        return 0

    # Compilação padrão DSL educativo
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
