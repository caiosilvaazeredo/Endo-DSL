"""Interface de linha de comando da plataforma Endo-DSL.

Uso: ``python -m endo_dsl <comando> [opções]`` (ou ``endo-dsl`` se instalado).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from endo_dsl import __version__
from endo_dsl.compiler.compiler import CompileError


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _print_issues(issues: List[Dict[str, Any]], stream=sys.stderr) -> None:
    for i in issues:
        loc = ""
        if i.get("line"):
            loc = f" (linha {i['line']}, col {i.get('col', 0)})"
        sev = i.get("severity", "error").upper()
        print(f"  [{sev}] {i.get('message','')}{loc}", file=stream)
        if i.get("suggestion"):
            print(f"         → {i['suggestion']}", file=stream)


# --------------------------------------------------------------------------- #
# Comandos
# --------------------------------------------------------------------------- #
def cmd_validate(args) -> int:
    from endo_dsl.platform import Platform
    p = Platform(args.db, seed=False)
    report = p.validate(_read(args.file))
    if report["syntactic_ok"] and report["semantic_ok"]:
        print(f"✓ Especificação válida: '{report.get('title','')}' "
              f"(Bloom: {', '.join(report.get('bloom_levels', []))})")
        if report["warnings"]:
            print(f"  {len(report['warnings'])} aviso(s):")
            _print_issues(report["warnings"], sys.stdout)
        return 0
    print("✗ Especificação inválida:", file=sys.stderr)
    _print_issues(report["errors"])
    return 1


def cmd_compile(args) -> int:
    from endo_dsl.platform import Platform
    p = Platform(args.db)
    try:
        result = p.compile(_read(args.file), origin=args.origin)
    except CompileError as exc:
        print("✗ Falha de compilação:", file=sys.stderr)
        _print_issues(exc.messages)
        return 1
    print(f"✓ Protótipo #{result['prototype_id']} compilado: {result['title']}")
    for label, path in result["paths"].items():
        print(f"  {label:>18}: {path}")
    if result["warnings"]:
        print(f"  {len(result['warnings'])} aviso(s) pedagógico(s):")
        _print_issues(result["warnings"], sys.stdout)
    print(f"\n  Abra no navegador: file://{result['paths']['html']}")
    return 0


def cmd_generate(args) -> int:
    from endo_dsl.platform import Platform
    p = Platform(args.db)
    context = {
        "learning_objective": args.objective,
        "domain": args.domain,
        "bloom_target": args.bloom,
        "topic": args.topic or args.domain,
        "age_range": args.age,
        "education_level": args.level,
        "duration": args.duration,
        "platform": "web",
    }
    sid = p.create_session(args.name or f"Sessão: {args.domain}", context)
    print(f"Sessão #{sid} criada. Backend LLM: {p.backend.name}")
    res = p.generate(sid, from_scratch=args.from_scratch,
                     selected_keys=args.components.split(",") if args.components else None)
    print(f"Geração {'✓ válida' if res.success else '✗ inválida'} "
          f"em {len(res.attempts)} tentativa(s) — {res.report.summary()}")
    if res.selected_components:
        print("Componentes usados:", ", ".join(rc.component.key for rc in res.selected_components))
    print("\n--- Especificação DSL gerada ---")
    print(res.dsl)
    if args.out:
        Path(args.out).write_text(res.dsl, encoding="utf-8")
        print(f"\nSalvo em {args.out}")
    if args.compile and res.success:
        result = p.compile(res.dsl, session_id=sid, origin="auto")
        print(f"\n✓ Compilado: {result['paths']['html']}")
    print("\nMétricas de geração:", json.dumps(p.generation_metrics(sid), ensure_ascii=False))
    return 0 if res.success else 1


def cmd_library(args) -> int:
    from endo_dsl.platform import Platform
    from endo_dsl.library.models import SearchFilters
    p = Platform(args.db)
    if args.action == "seed":
        from endo_dsl.library.seed import seed_canonical
        created = seed_canonical(p.repo, force=args.force)
        print(f"{len(created)} componente(s) canônico(s) cadastrado(s).")
        return 0
    if args.action == "show":
        comp = p.get_component(args.key)
        if not comp:
            print(f"componente '{args.key}' não encontrado", file=sys.stderr)
            return 1
        print(json.dumps(comp.to_dict(), ensure_ascii=False, indent=2))
        return 0
    # list / search
    filters = SearchFilters(text=args.text, bloom_level=args.bloom,
                            mechanic_type=args.type, domain=args.domain,
                            status=args.status)
    comps = p.search_components(filters)
    print(f"{len(comps)} componente(s):")
    for c in comps:
        star = "★" if c.is_canonical else "○"
        rating = f" ⟨{c.metrics.avg_rating:.1f}⟩" if c.metrics.avg_rating else ""
        print(f"  {star} {c.key:<32} {c.bloom_level:<12} {c.mechanic_type:<14}{rating}")
    print("\n  ★ canônico · ○ experimental")
    return 0


def cmd_curate(args) -> int:
    from endo_dsl.platform import Platform
    p = Platform(args.db)
    if args.action == "list":
        queue = p.curation_queue()
        print(f"{len(queue)} componente(s) na fila de curadoria:")
        for c in queue:
            print(f"  #{c.id} {c.key:<30} {c.bloom_level:<12} {c.mechanic_type:<14} "
                  f"(instâncias: {c.metrics.instantiations})")
        return 0
    if args.action == "approve":
        p.approve_component(int(args.id), curator=args.curator, justification=args.note or "")
        print(f"✓ componente #{args.id} promovido a canônico.")
        return 0
    if args.action == "reject":
        p.reject_component(int(args.id), curator=args.curator, justification=args.note or "")
        print(f"✗ componente #{args.id} rejeitado.")
        return 0
    return 2


def cmd_reparametrize(args) -> int:
    from endo_dsl.platform import Platform
    p = Platform(args.db)
    try:
        res = p.reparametrize(int(args.prototype), domain=args.domain, topic=args.topic)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"✓ Protótipo #{args.prototype} reparametrizado para '{args.domain}'.")
    print(f"  {res['path']}")
    return 0


def cmd_report(args) -> int:
    from endo_dsl.platform import Platform
    p = Platform(args.db)
    if args.csv:
        print(p.evaluations.export_csv())
        return 0
    print(p.comparison_report(as_text=True))
    return 0


def cmd_grammar(args) -> int:
    path = Path(__file__).parent / "dsl" / "grammar.ebnf"
    print(path.read_text(encoding="utf-8"))
    return 0


def cmd_limits(args) -> int:
    from endo_dsl.dsl import limits
    print(limits.as_markdown())
    return 0


def cmd_serve(args) -> int:
    from endo_dsl.web.server import serve
    serve(host=args.host, port=args.port, db_path=args.db)
    return 0


def cmd_demo(args) -> int:
    from endo_dsl.demo import run_demo
    run_demo(db_path=args.db)
    return 0


# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="endo-dsl",
        description="Endo-DSL — design e geração automática de jogos educacionais endógenos.")
    parser.add_argument("--version", action="version", version=f"Endo-DSL {__version__}")
    parser.add_argument("--db", default=None, help="caminho do banco SQLite (padrão: data/endo_dsl.sqlite3)")
    sub = parser.add_subparsers(dest="command", required=True)

    v = sub.add_parser("validate", help="valida sintática e semanticamente um arquivo .endo (RF03/RF04)")
    v.add_argument("file")
    v.set_defaults(func=cmd_validate)

    c = sub.add_parser("compile", help="compila DSL -> protótipo HTML5 (RF19-RF23)")
    c.add_argument("file")
    c.add_argument("--origin", default="manual", choices=["manual", "auto", "hybrid"])
    c.set_defaults(func=cmd_compile)

    g = sub.add_parser("generate", help="pipeline multi-agente: gera DSL a partir do contexto (RF13-RF18)")
    g.add_argument("--objective", required=True, help="objetivo de aprendizagem")
    g.add_argument("--domain", required=True, help="área de conhecimento")
    g.add_argument("--bloom", required=True, help="nível de Bloom alvo")
    g.add_argument("--topic", default=None)
    g.add_argument("--age", default=None, help="faixa etária")
    g.add_argument("--level", default=None, help="nível de escolaridade")
    g.add_argument("--duration", type=int, default=None)
    g.add_argument("--name", default=None, help="nome da sessão")
    g.add_argument("--components", default=None, help="chaves de componentes (separadas por vírgula)")
    g.add_argument("--from-scratch", action="store_true", help="gerar sem componentes")
    g.add_argument("--compile", action="store_true", help="compila o resultado se válido")
    g.add_argument("--out", default=None, help="salva a DSL gerada em arquivo")
    g.set_defaults(func=cmd_generate)

    lib = sub.add_parser("library", help="biblioteca de componentes (RF07-RF12)")
    lib.add_argument("action", choices=["list", "search", "seed", "show"])
    lib.add_argument("key", nargs="?", help="chave do componente (para 'show')")
    lib.add_argument("--text", default=None)
    lib.add_argument("--bloom", default=None)
    lib.add_argument("--type", default=None)
    lib.add_argument("--domain", default=None)
    lib.add_argument("--status", default=None, choices=["canonical", "experimental"])
    lib.add_argument("--force", action="store_true")
    lib.set_defaults(func=cmd_library)

    cur = sub.add_parser("curate", help="curadoria de componentes (jornada do curador, RF12)")
    cur.add_argument("action", choices=["list", "approve", "reject"])
    cur.add_argument("id", nargs="?")
    cur.add_argument("--curator", default=None)
    cur.add_argument("--note", default=None, help="justificativa")
    cur.set_defaults(func=cmd_curate)

    rp = sub.add_parser("reparametrize", help="troca o domínio de um protótipo sem recompilar (RF22)")
    rp.add_argument("prototype")
    rp.add_argument("--domain", required=True)
    rp.add_argument("--topic", default=None)
    rp.set_defaults(func=cmd_reparametrize)

    rep = sub.add_parser("report", help="relatório comparativo auto x manual (RF26)")
    rep.add_argument("--csv", action="store_true", help="exporta avaliações em CSV (RF25)")
    rep.set_defaults(func=cmd_report)

    sub.add_parser("grammar", help="imprime a gramática formal (EBNF)").set_defaults(func=cmd_grammar)
    sub.add_parser("limits", help="imprime os limites da gramática (RF06)").set_defaults(func=cmd_limits)

    s = sub.add_parser("serve", help="inicia a interface web (jornada completa)")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.set_defaults(func=cmd_serve)

    d = sub.add_parser("demo", help="executa uma demonstração completa da plataforma")
    d.set_defaults(func=cmd_demo)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
