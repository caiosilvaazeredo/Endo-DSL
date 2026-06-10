"""Interface de linha de comando da plataforma Endo-DSL.

Uso: ``python -m endo_dsl <comando> [opções]`` (ou ``endo-dsl`` se instalado).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from endo_dsl import __version__, config
from endo_dsl.compiler.compiler import CompileError


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _resolve_db(args) -> Optional[str]:
    """Resolve o caminho do banco: --db > ENDO_DSL_DB > config.db_path > padrão."""
    if getattr(args, "db", None):
        return args.db
    env = os.environ.get("ENDO_DSL_DB")
    if env:
        return env
    return config.get("db_path") or None


def _emit_json(args, payload: Any) -> bool:
    """Imprime ``payload`` como JSON se --json estiver ativo. Retorna True nesse caso."""
    if getattr(args, "json", False):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return True
    return False


def _say(args, *parts) -> None:
    """Imprime, respeitando --quiet."""
    if not getattr(args, "quiet", False):
        print(*parts)


# --------------------------------------------------------------------------- #
# Formatador canônico (fmt)
# --------------------------------------------------------------------------- #
_BARE_VALUE = __import__("re").compile(r"^[A-Za-z_][A-Za-z0-9_./-]*$")


def _fmt_value(value: Any) -> str:
    """Re-emite um valor de parâmetro de forma canônica.

    Heurística (formatador best-effort): números/booleanos saem sem aspas;
    identificadores simples saem sem aspas; demais strings são citadas.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):  # RANGE start..end
        return f"{value[0]}..{value[1]}"
    s = str(value)
    if _BARE_VALUE.match(s):
        return s
    return '"' + s.replace('"', '\\"') + '"'


def format_spec(source: str, *, indent: int = 2) -> str:
    """Reemite uma especificação .endo de forma canônica a partir da AST.

    Formatador *best-effort*: re-valida que a AST do resultado é equivalente à
    original (mesmo ``to_dict()``). Casos de borda conhecidos: comentários
    (``//``) são descartados; a distinção string-literal vs. identificador é
    recuperada por heurística (ver :func:`_fmt_value`); a ordem dos campos é
    normalizada (metadata, objectives, mechanics, loops, narratives).
    """
    from endo_dsl.dsl.parser import parse

    spec = parse(source)
    pad = " " * indent
    out: List[str] = [f'game "{spec.title}" {{']

    if spec.metadata.values:
        out.append(f"{pad}metadata {{")
        for k, v in spec.metadata.values.items():
            out.append(f"{pad}{pad}{k}: {_fmt_value(v)}")
        out.append(f"{pad}}}")

    for o in spec.objectives:
        out.append("")
        out.append(f"{pad}objective {o.name} {{")
        if o.description:
            out.append(f'{pad}{pad}description: "{o.description}"')
        if o.bloom is not None:
            out.append(f"{pad}{pad}bloom: {o.bloom.pt}")
        out.append(f"{pad}}}")

    for m in spec.mechanics:
        out.append("")
        out.append(f"{pad}mechanic {m.name} {{")
        if m.type:
            out.append(f"{pad}{pad}type: {m.type}")
        if m.bloom is not None:
            out.append(f"{pad}{pad}bloom: {m.bloom.pt}")
        if m.addresses:
            out.append(f"{pad}{pad}addresses: {', '.join(m.addresses)}")
        if m.description:
            out.append(f'{pad}{pad}description: "{m.description}"')
        if m.params.values:
            out.append(f"{pad}{pad}params {{")
            for k, v in m.params.values.items():
                out.append(f"{pad}{pad}{pad}{k}: {_fmt_value(v)}")
            out.append(f"{pad}{pad}}}")
        out.append(f"{pad}}}")

    for l in spec.loops:
        out.append("")
        out.append(f"{pad}loop {l.name} {{")
        if l.bloom is not None:
            out.append(f"{pad}{pad}bloom: {l.bloom.pt}")
        if l.description:
            out.append(f'{pad}{pad}description: "{l.description}"')
        if l.transitions:
            out.append(f"{pad}{pad}steps {{")
            for t in l.transitions:
                out.append(f"{pad}{pad}{pad}{t.src} -> {t.dst}")
            out.append(f"{pad}{pad}}}")
        out.append(f"{pad}}}")

    for n in spec.narratives:
        out.append("")
        out.append(f"{pad}narrative {n.name} {{")
        for b in n.branches:
            out.append(f"{pad}{pad}branch {b.name} {{")
            if b.bloom is not None:
                out.append(f"{pad}{pad}{pad}bloom: {b.bloom.pt}")
            if b.text:
                out.append(f'{pad}{pad}{pad}text: "{b.text}"')
            if b.description:
                out.append(f'{pad}{pad}{pad}description: "{b.description}"')
            for c in b.choices:
                out.append(f'{pad}{pad}{pad}choice "{c.text}" -> {c.target}')
            out.append(f"{pad}{pad}}}")
        out.append(f"{pad}}}")

    out.append("}")
    result = "\n".join(out) + "\n"

    # Re-valida equivalência semântica (best-effort round-trip).
    try:
        if parse(result).to_dict() != spec.to_dict():
            # Em caso de divergência, preferimos não corromper: devolve original.
            return source if source.endswith("\n") else source + "\n"
    except Exception:
        return source if source.endswith("\n") else source + "\n"
    return result


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
    p = Platform(_resolve_db(args), seed=False)
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
    p = Platform(_resolve_db(args))
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
    p = Platform(_resolve_db(args))
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
    p = Platform(_resolve_db(args))
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
    p = Platform(_resolve_db(args))
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
    p = Platform(_resolve_db(args))
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
    p = Platform(_resolve_db(args))
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
    serve(host=args.host, port=args.port, db_path=_resolve_db(args))
    return 0


def cmd_demo(args) -> int:
    from endo_dsl.demo import run_demo
    run_demo(db_path=_resolve_db(args))
    return 0


# --------------------------------------------------------------------------- #
# Novos comandos (1.1.0)
# --------------------------------------------------------------------------- #
def cmd_init_db(args) -> int:
    from endo_dsl.db.database import Database, default_db_path
    path = _resolve_db(args) or str(default_db_path())
    if args.force and path != ":memory:" and Path(path).exists():
        Path(path).unlink()
        _say(args, f"Banco anterior removido: {path}")
    db = Database(path)  # initialize() aplica o esquema (idempotente)
    db.close()
    if _emit_json(args, {"db_path": path, "initialized": True}):
        return 0
    _say(args, f"✓ Banco inicializado em {path}")
    return 0


def cmd_seed_components(args) -> int:
    from endo_dsl.platform import Platform
    from endo_dsl.library.seed import seed_canonical
    p = Platform(_resolve_db(args), seed=False)
    if args.reset:
        p.db.execute("DELETE FROM components")
        p.db.commit()
        _say(args, "Componentes anteriores removidos.")
    created = seed_canonical(p.repo, force=args.reset)
    total = len(p.repo.list_all())
    if _emit_json(args, {"created": len(created), "total": total}):
        return 0
    _say(args, f"✓ {len(created)} componente(s) cadastrado(s); {total} no total.")
    return 0


_TEMPLATE = '''\
// {name} — Bloom: {bloom} — Domínio: {domain}
// Gerado por `endo-dsl new`. Edite e compile com `endo-dsl compile`.

game "{name}" {{
  metadata {{
    domain: "{domain}"
    topic: "{topic}"
    bloom: {bloom}
  }}

  objective obj_principal {{
    description: "Descreva aqui o objetivo de aprendizagem."
    bloom: {bloom}
  }}

  mechanic mecanica_principal {{
    type: {mtype}
    bloom: {bloom}
    addresses: obj_principal
    description: "Descreva a mecânica endógena."
    params {{
      difficulty: "medium"
    }}
  }}

  loop principal {{
    bloom: {bloom}
    description: "Loop central de jogabilidade."
    steps {{
      mecanica_principal -> mecanica_principal
    }}
  }}
}}
'''


def cmd_new(args) -> int:
    from endo_dsl.dsl.bloom import parse_bloom
    bloom_in = args.bloom or config.get("default_bloom", "Analisar")
    lvl = parse_bloom(bloom_in)
    bloom = lvl.pt if lvl else "Analisar"
    domain = args.domain or config.get("default_domain", "genérico")
    content = _TEMPLATE.format(
        name=args.name, bloom=bloom, domain=domain,
        topic=args.topic or domain.lower(), mtype=args.type or "classification",
    )
    if args.output:
        out = Path(args.output)
    else:
        out_dir = Path(config.get("output_dir") or ".")
        out = out_dir / f"{args.name.lower().replace(' ', '_')}.endo"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    if _emit_json(args, {"path": str(out), "bloom": bloom, "domain": domain}):
        return 0
    _say(args, f"✓ Arquivo criado: {out}")
    return 0


def cmd_lint(args) -> int:
    from endo_dsl.platform import Platform
    p = Platform(_resolve_db(args), seed=False)
    report = p.validate(_read(args.file))
    issues = list(report.get("errors", [])) + list(report.get("warnings", []))
    if _emit_json(args, {"file": args.file, "ok": not report.get("errors"),
                         "issues": issues}):
        return 1 if report.get("errors") or (args.strict and report.get("warnings")) else 0
    if not issues:
        _say(args, f"✓ {args.file}: nenhum problema encontrado.")
        return 0
    n_err = len(report.get("errors", []))
    n_warn = len(report.get("warnings", []))
    _say(args, f"{args.file}: {n_err} erro(s), {n_warn} aviso(s)")
    _print_issues(issues, sys.stdout)
    if report.get("errors"):
        return 1
    if args.strict and report.get("warnings"):
        return 1
    return 0


def cmd_fmt(args) -> int:
    from endo_dsl.dsl.parser import ParseError
    src = _read(args.file)
    tab = int(config.get("editor.tab_size", 2) or 2)
    try:
        formatted = format_spec(src, indent=tab)
    except ParseError as exc:
        print(f"✗ {args.file}: erro de sintaxe — {exc}", file=sys.stderr)
        return 1
    if args.check:
        if formatted != src:
            print(f"✗ {args.file}: não está formatado (rode `fmt --write`)", file=sys.stderr)
            return 1
        _say(args, f"✓ {args.file}: já está formatado.")
        return 0
    if args.write:
        if formatted != src:
            Path(args.file).write_text(formatted, encoding="utf-8")
            _say(args, f"✓ {args.file}: formatado.")
        else:
            _say(args, f"✓ {args.file}: já está formatado.")
        return 0
    sys.stdout.write(formatted)
    return 0


def cmd_stats(args) -> int:
    from endo_dsl.platform import Platform
    p = Platform(_resolve_db(args), seed=False)
    db = p.db

    def count(sql):
        row = db.query_one(sql)
        return list(row)[0] if row else 0

    data = {
        "components": count("SELECT COUNT(*) FROM components"),
        "components_canonical": count("SELECT COUNT(*) FROM components WHERE status='canonical'"),
        "components_experimental": count("SELECT COUNT(*) FROM components WHERE status='experimental'"),
        "design_sessions": count("SELECT COUNT(*) FROM design_sessions"),
        "specifications": count("SELECT COUNT(*) FROM specifications"),
        "prototypes": count("SELECT COUNT(*) FROM prototypes"),
        "component_usages": count("SELECT COUNT(*) FROM component_usage"),
        "evaluations": count("SELECT COUNT(*) FROM evaluations"),
    }
    if _emit_json(args, data):
        return 0
    _say(args, "Métricas da plataforma Endo-DSL")
    _say(args, "─" * 40)
    for k, v in data.items():
        _say(args, f"  {k:<26} {v:>10}")
    return 0


def cmd_export(args) -> int:
    from endo_dsl.platform import Platform
    p = Platform(_resolve_db(args), seed=False)
    comps = [c.to_dict() for c in p.repo.list_all(with_metrics=False)]
    payload = {"version": __version__, "components": comps}
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        _say(args, f"✓ {len(comps)} componente(s) exportado(s) para {args.out}")
    else:
        print(text)
    return 0


def cmd_import(args) -> int:
    from endo_dsl.platform import Platform
    p = Platform(_resolve_db(args), seed=False)
    raw = json.loads(_read(getattr(args, "in")))
    comps = raw.get("components", raw if isinstance(raw, list) else [])
    created = 0
    skipped = 0
    for c in comps:
        key = c.get("key")
        if key and p.repo.get_by_key(key) is not None:
            if args.merge:
                skipped += 1
                continue
        try:
            p.repo.create(
                name=c["name"], dsl_signature=c["dsl_signature"],
                bloom_level=c["bloom_level"], mechanic_type=c["mechanic_type"],
                description=c["description"], params=c.get("params") or {},
                domain=c.get("domain"), context=c.get("context"),
                age_range=c.get("age_range"), modality=c.get("modality"),
                status=c.get("status", "experimental"), author=c.get("author"),
                key=key if args.merge else None,
            )
            created += 1
        except (KeyError, ValueError) as exc:
            print(f"  aviso: componente ignorado ({exc})", file=sys.stderr)
            skipped += 1
    if _emit_json(args, {"created": created, "skipped": skipped}):
        return 0
    _say(args, f"✓ {created} componente(s) importado(s); {skipped} ignorado(s).")
    return 0


def cmd_config(args) -> int:
    if args.action == "path":
        print(config.config_path())
        return 0
    if args.action == "list":
        flat = config.flatten()
        if _emit_json(args, flat):
            return 0
        for k in sorted(flat):
            print(f"  {k:<22} = {flat[k]}")
        return 0
    if args.action == "get":
        if not args.key:
            print("uso: config get <chave>", file=sys.stderr)
            return 2
        val = config.get(args.key, None)
        print(json.dumps(val, ensure_ascii=False) if args.json else val)
        return 0
    if args.action == "set":
        if not args.key or args.value is None:
            print("uso: config set <chave> <valor>", file=sys.stderr)
            return 2
        config.set(args.key, args.value)
        _say(args, f"✓ {args.key} = {config.get(args.key)}")
        return 0
    if args.action == "reset":
        path = config.reset()
        _say(args, f"✓ configuração restaurada para os padrões em {path}")
        return 0
    return 2


def cmd_theme(args) -> int:
    from endo_dsl import themes
    if args.action == "list":
        names = themes.list_themes()
        if _emit_json(args, names):
            return 0
        current = config.get("theme")
        for n in names:
            mark = " (atual)" if n == current else ""
            print(f"  {n}{mark}")
        return 0
    if args.action == "show":
        if not args.name:
            print("uso: theme show <nome>", file=sys.stderr)
            return 2
        print(themes.as_css(args.name))
        return 0
    if args.action == "set":
        if not args.name:
            print("uso: theme set <nome>", file=sys.stderr)
            return 2
        if args.name not in themes.list_themes():
            print(f"tema desconhecido: {args.name} "
                  f"(disponíveis: {', '.join(themes.list_themes())})", file=sys.stderr)
            return 1
        config.set("theme", args.name)
        _say(args, f"✓ tema definido: {args.name}")
        return 0
    return 2


def cmd_watch(args) -> int:
    from endo_dsl.platform import Platform
    path = Path(args.file)
    if not path.exists():
        print(f"arquivo não encontrado: {path}", file=sys.stderr)
        return 1
    p = Platform(_resolve_db(args))
    interval = max(0.2, float(args.interval))
    _say(args, f"Observando {path} (Ctrl+C para parar)…")
    last = None
    try:
        while True:
            try:
                mtime = path.stat().st_mtime
            except FileNotFoundError:
                time.sleep(interval)
                continue
            if mtime != last:
                last = mtime
                try:
                    result = p.compile(path.read_text(encoding="utf-8"), origin="manual")
                    _say(args, f"✓ recompilado: {result['paths']['html']}")
                except CompileError as exc:
                    print("✗ falha de compilação:", file=sys.stderr)
                    _print_issues(exc.messages)
                except Exception as exc:  # noqa: BLE001
                    print(f"✗ erro: {exc}", file=sys.stderr)
            time.sleep(interval)
    except KeyboardInterrupt:
        _say(args, "\nEncerrado.")
        return 0


def cmd_doctor(args) -> int:
    import platform as _platform
    from endo_dsl import themes
    from endo_dsl.db.database import Database, default_db_path

    lines: List[Dict[str, str]] = []

    def add(status, label, detail=""):
        lines.append({"status": status, "label": label, "detail": detail})

    # Python
    pyok = sys.version_info >= (3, 11)
    add("OK" if pyok else "FAIL", "Python", _platform.python_version())

    # Config
    cpath = config.config_path()
    add("OK" if cpath.exists() else "WARN", "Config",
        f"{cpath}{'' if cpath.exists() else ' (usando padrões)'}")

    # DB
    db_path = _resolve_db(args) or str(default_db_path())
    comp_count = "?"
    try:
        db = Database(db_path)
        row = db.query_one("SELECT COUNT(*) AS c FROM components")
        comp_count = row["c"] if row else 0
        db.close()
        add("OK", "Banco de dados", db_path)
        add("OK" if comp_count else "WARN", "Componentes",
            f"{comp_count} cadastrado(s)" + ("" if comp_count else " (rode seed-components)"))
    except Exception as exc:  # noqa: BLE001
        add("FAIL", "Banco de dados", f"{db_path} — {exc}")

    # Backend
    backend = os.environ.get("ENDO_DSL_BACKEND") or config.get("backend")
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if backend == "claude" and not has_key:
        add("WARN", "Backend LLM", "claude selecionado, mas ANTHROPIC_API_KEY ausente")
    else:
        add("OK", "Backend LLM",
            f"{backend}" + (" (API key presente)" if has_key else ""))

    # Theme
    theme = config.get("theme")
    add("OK" if theme in themes.list_themes() else "WARN", "Tema", str(theme))

    # Write perms (output_dir / cwd)
    out_dir = Path(config.get("output_dir") or ".")
    add("OK" if os.access(out_dir, os.W_OK) else "WARN", "Permissão de escrita", str(out_dir.resolve()))

    if _emit_json(args, {"checks": lines}):
        return 0
    _say(args, "Diagnóstico do ambiente Endo-DSL")
    _say(args, "─" * 50)
    for ln in lines:
        _say(args, f"  [{ln['status']:<4}] {ln['label']:<22} {ln['detail']}")
    return 0 if not any(l["status"] == "FAIL" for l in lines) else 1


# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="endo-dsl",
        description="Endo-DSL — design e geração automática de jogos educacionais endógenos.")
    parser.add_argument("--version", action="version", version=f"Endo-DSL {__version__}")
    parser.add_argument("--config", default=None, help="caminho do arquivo de configuração")
    parser.add_argument("--db", default=None, help="caminho do banco SQLite (padrão: data/endo_dsl.sqlite3)")
    parser.add_argument("--theme", default=None, help="tema de interface (sobrepõe a configuração)")
    parser.add_argument("--backend", default=None, choices=["template", "claude"],
                        help="backend LLM (sobrepõe a configuração)")
    parser.add_argument("--quiet", action="store_true", help="suprime mensagens informativas")
    parser.add_argument("--json", action="store_true", help="saída legível por máquina onde aplicável")
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

    # ---- novos comandos (1.1.0) ---------------------------------------- #
    idb = sub.add_parser("init-db", help="cria/inicializa o esquema SQLite (idempotente)")
    idb.add_argument("--force", action="store_true", help="recria o banco do zero")
    idb.set_defaults(func=cmd_init_db)

    sc = sub.add_parser("seed-components", help="popula os componentes canônicos")
    sc.add_argument("--reset", action="store_true", help="apaga componentes antes de popular")
    sc.set_defaults(func=cmd_seed_components)

    nw = sub.add_parser("new", help="cria um arquivo .endo a partir de um modelo")
    nw.add_argument("name", help="título do jogo")
    nw.add_argument("--bloom", default=None)
    nw.add_argument("--domain", default=None)
    nw.add_argument("--type", default=None, help="tipo de mecânica")
    nw.add_argument("--topic", default=None)
    nw.add_argument("-o", "--output", default=None, help="caminho de saída do .endo")
    nw.set_defaults(func=cmd_new)

    ln = sub.add_parser("lint", help="valida e reporta avisos/estilo com severidades")
    ln.add_argument("file")
    ln.add_argument("--strict", action="store_true", help="falha (saída != 0) em avisos")
    ln.set_defaults(func=cmd_lint)

    fm = sub.add_parser("fmt", help="normaliza/formata um arquivo .endo")
    fm.add_argument("file")
    fm.add_argument("--write", action="store_true", help="edita o arquivo no lugar")
    fm.add_argument("--check", action="store_true", help="falha se não estiver formatado (CI)")
    fm.set_defaults(func=cmd_fmt)

    st = sub.add_parser("stats", help="métricas de biblioteca/uso/geração/avaliação")
    st.set_defaults(func=cmd_stats)

    ex = sub.add_parser("export", help="exporta a biblioteca de componentes para JSON")
    ex.add_argument("--out", default=None, help="arquivo de saída (padrão: stdout)")
    ex.set_defaults(func=cmd_export)

    im = sub.add_parser("import", help="importa componentes de um JSON")
    im.add_argument("--in", dest="in", required=True, help="arquivo JSON de entrada")
    im.add_argument("--merge", action="store_true", help="ignora chaves já existentes")
    im.set_defaults(func=cmd_import)

    cfg = sub.add_parser("config", help="lê/define a configuração do usuário")
    cfg.add_argument("action", choices=["get", "set", "list", "reset", "path"])
    cfg.add_argument("key", nargs="?")
    cfg.add_argument("value", nargs="?")
    cfg.set_defaults(func=cmd_config)

    th = sub.add_parser("theme", help="lista/exibe/define temas de interface")
    th.add_argument("action", choices=["list", "show", "set"])
    th.add_argument("name", nargs="?")
    th.set_defaults(func=cmd_theme)

    wt = sub.add_parser("watch", help="observa um .endo e recompila a cada alteração")
    wt.add_argument("file")
    wt.add_argument("--interval", type=float, default=1.0, help="intervalo de polling (s)")
    wt.set_defaults(func=cmd_watch)

    dc = sub.add_parser("doctor", help="diagnóstico do ambiente")
    dc.set_defaults(func=cmd_doctor)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    # Flags globais que influenciam a configuração efetiva.
    if getattr(args, "config", None):
        os.environ["ENDO_DSL_CONFIG"] = args.config
    if getattr(args, "theme", None):
        os.environ["ENDO_DSL_THEME"] = args.theme
    if getattr(args, "backend", None):
        os.environ["ENDO_DSL_BACKEND"] = args.backend
    try:
        return args.func(args)
    except FileNotFoundError as exc:
        print(f"✗ arquivo não encontrado: {exc.filename or exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:  # pragma: no cover
        return 130


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
