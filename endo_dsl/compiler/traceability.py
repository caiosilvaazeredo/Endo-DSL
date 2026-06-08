"""Documento de rastreabilidade objetivo -> mecânica (RF23).

Gera, automaticamente a partir da AST, um documento que vincula cada objetivo de
aprendizagem declarado às mecânicas que o implementam, com seus níveis de Bloom.
Disponível em JSON (estruturado), Markdown (leitura) e HTML (visualização).
"""

from __future__ import annotations

from typing import Any, Dict

from endo_dsl.dsl.ast import GameSpec


def build(spec: GameSpec) -> Dict[str, Any]:
    """Documento de rastreabilidade estruturado (RF23)."""
    objectives = []
    for o in spec.objectives:
        mechs = [m for m in spec.mechanics if o.name in m.addresses]
        objectives.append({
            "objective": o.name,
            "description": o.description or o.name,
            "bloom": o.bloom.pt if o.bloom else None,
            "mechanics": [
                {
                    "name": m.name,
                    "type": m.type,
                    "bloom": m.bloom.pt if m.bloom else None,
                    "source_component": m.source_component,
                }
                for m in mechs
            ],
            "covered": bool(mechs),
        })
    # Mecânicas que não endereçam objetivo algum (lacuna de rastreabilidade).
    orphan = [m.name for m in spec.mechanics if not m.addresses]
    return {
        "title": spec.title,
        "domain": spec.metadata.get("domain"),
        "objectives": objectives,
        "orphan_mechanics": orphan,
        "coverage": _coverage(objectives),
    }


def _coverage(objectives) -> Dict[str, Any]:
    total = len(objectives)
    covered = sum(1 for o in objectives if o["covered"])
    return {
        "objectives_total": total,
        "objectives_covered": covered,
        "ratio": round(covered / total, 3) if total else None,
    }


def as_markdown(spec: GameSpec) -> str:
    doc = build(spec)
    lines = [
        f"# Rastreabilidade pedagógica — {doc['title']}",
        "",
        f"Domínio: **{doc['domain'] or '—'}**  ",
        f"Cobertura de objetivos: **{doc['coverage']['objectives_covered']}/"
        f"{doc['coverage']['objectives_total']}**",
        "",
        "| Objetivo | Nível de Bloom | Mecânicas que o implementam |",
        "|----------|----------------|------------------------------|",
    ]
    for o in doc["objectives"]:
        mechs = ", ".join(
            f"`{m['name']}` ({m['type']}, {m['bloom']})" for m in o["mechanics"]
        ) or "_— nenhuma —_"
        lines.append(f"| {o['description']} | {o['bloom'] or '—'} | {mechs} |")
    if doc["orphan_mechanics"]:
        lines += ["", "## Mecânicas sem objetivo vinculado",
                  ", ".join(f"`{m}`" for m in doc["orphan_mechanics"])]
    return "\n".join(lines)


def as_html(spec: GameSpec) -> str:
    doc = build(spec)
    rows = ""
    for o in doc["objectives"]:
        mechs = "<br>".join(
            f"<code>{m['name']}</code> <span style='color:#888'>({m['type']}, {m['bloom']})</span>"
            for m in o["mechanics"]
        ) or "<em>— nenhuma —</em>"
        rows += (f"<tr><td>{_esc(o['description'])}</td><td>{o['bloom'] or '—'}</td>"
                 f"<td>{mechs}</td></tr>")
    cov = doc["coverage"]
    return (
        "<!doctype html><meta charset='utf-8'>"
        f"<title>Rastreabilidade — {_esc(doc['title'])}</title>"
        "<style>body{font-family:system-ui;max-width:800px;margin:40px auto;padding:0 16px}"
        "table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:8px;"
        "text-align:left;vertical-align:top}th{background:#f4f6fb}</style>"
        f"<h1>Rastreabilidade pedagógica — {_esc(doc['title'])}</h1>"
        f"<p>Domínio: <b>{_esc(doc['domain'] or '—')}</b> · Cobertura: "
        f"<b>{cov['objectives_covered']}/{cov['objectives_total']}</b></p>"
        "<table><tr><th>Objetivo</th><th>Bloom</th><th>Mecânicas</th></tr>"
        f"{rows}</table>"
    )


def _esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
