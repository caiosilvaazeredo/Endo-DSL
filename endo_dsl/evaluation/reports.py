"""Relatórios comparativos protótipos automáticos x manuais (RF26).

Agrega as avaliações registradas e produz comparações por dimensão pedagógica,
nível de Bloom e domínio de conhecimento — base para responder à Questão de
Pesquisa Q4. Fornece os dados estruturados (consumidos pela UI) e uma visualização
textual (barras ASCII) para uso em terminal/relatórios.
"""

from __future__ import annotations

from statistics import mean, pstdev
from typing import Any, Dict, List, Optional

from endo_dsl.evaluation.instrument import DIMENSIONS, overall_score
from endo_dsl.evaluation.store import EvaluationRecord, EvaluationStore


def _agg(records: List[EvaluationRecord]) -> Dict[str, Any]:
    if not records:
        return {"n": 0, "overall_mean": None, "overall_std": None, "per_dimension": {}}
    overalls = [r.overall for r in records]
    per_dim: Dict[str, Any] = {}
    for dim in DIMENSIONS:
        vals = [r.scores[dim.key] for r in records if dim.key in r.scores]
        per_dim[dim.key] = round(mean(vals), 3) if vals else None
    return {
        "n": len(records),
        "overall_mean": round(mean(overalls), 3),
        "overall_std": round(pstdev(overalls), 3) if len(overalls) > 1 else 0.0,
        "per_dimension": per_dim,
    }


def comparative_report(store: EvaluationStore) -> Dict[str, Any]:
    """Relatório comparativo completo entre origens (RF26)."""
    auto = store.list(origin="auto")
    manual = store.list(origin="manual")
    hybrid = store.list(origin="hybrid")

    by_dimension = []
    agg_auto = _agg(auto)
    agg_manual = _agg(manual)
    for dim in DIMENSIONS:
        a = agg_auto["per_dimension"].get(dim.key)
        m = agg_manual["per_dimension"].get(dim.key)
        by_dimension.append({
            "dimension": dim.key,
            "label": dim.label,
            "auto": a,
            "manual": m,
            "delta": round((a - m), 3) if (a is not None and m is not None) else None,
        })

    return {
        "summary": {
            "auto": agg_auto,
            "manual": agg_manual,
            "hybrid": _agg(hybrid),
            "overall_delta": (
                round(agg_auto["overall_mean"] - agg_manual["overall_mean"], 3)
                if agg_auto["overall_mean"] is not None and agg_manual["overall_mean"] is not None
                else None
            ),
        },
        "by_dimension": by_dimension,
        "by_bloom": _group(auto, manual, key=lambda r: r.bloom_level or "—"),
        "by_domain": _group(auto, manual, key=lambda r: r.domain or "—"),
        "interpretation": _interpret(agg_auto, agg_manual),
    }


def _group(auto, manual, *, key) -> Dict[str, Any]:
    keys = sorted({key(r) for r in auto} | {key(r) for r in manual})
    out: Dict[str, Any] = {}
    for k in keys:
        a = [r for r in auto if key(r) == k]
        m = [r for r in manual if key(r) == k]
        out[k] = {
            "auto_mean": round(mean([r.overall for r in a]), 3) if a else None,
            "manual_mean": round(mean([r.overall for r in m]), 3) if m else None,
            "n_auto": len(a),
            "n_manual": len(m),
        }
    return out


def _interpret(agg_auto, agg_manual) -> str:
    a, m = agg_auto["overall_mean"], agg_manual["overall_mean"]
    if a is None or m is None:
        return ("Dados insuficientes para comparação: é preciso avaliar protótipos "
                "automáticos e manuais.")
    delta = a - m
    if abs(delta) < 0.25:
        return (f"Qualidade pedagógica equivalente (Δ={delta:+.2f}): protótipos automáticos "
                f"({a:.2f}) e manuais ({m:.2f}) não diferem de forma relevante.")
    if delta > 0:
        return (f"Protótipos automáticos avaliados acima dos manuais (Δ={delta:+.2f}; "
                f"{a:.2f} vs {m:.2f}).")
    return (f"Protótipos manuais avaliados acima dos automáticos (Δ={delta:+.2f}; "
            f"{m:.2f} vs {a:.2f}).")


def _bar(value: Optional[float], width: int = 20, scale: float = 5.0) -> str:
    if value is None:
        return "·" * width + " (s/ dados)"
    filled = int(round((value / scale) * width))
    return "█" * filled + "░" * (width - filled) + f" {value:.2f}"


def report_as_text(report: Dict[str, Any]) -> str:
    """Renderiza o relatório comparativo como texto com barras ASCII (RF26)."""
    s = report["summary"]
    lines = [
        "═══════════════════════════════════════════════════════════════",
        " RELATÓRIO COMPARATIVO — Protótipos Automáticos x Manuais (RF26)",
        "═══════════════════════════════════════════════════════════════",
        f" Automáticos: n={s['auto']['n']}  média geral={_fmt(s['auto']['overall_mean'])}",
        f" Manuais:     n={s['manual']['n']}  média geral={_fmt(s['manual']['overall_mean'])}",
        "",
        " Por dimensão pedagógica (escala 1–5):",
    ]
    for d in report["by_dimension"]:
        lines.append(f"  {d['label']:<28}")
        lines.append(f"    auto   {_bar(d['auto'])}")
        lines.append(f"    manual {_bar(d['manual'])}")
    lines += ["", " Por nível de Bloom (média geral):"]
    for bloom, vals in report["by_bloom"].items():
        lines.append(f"  {bloom:<14} auto={_fmt(vals['auto_mean'])} (n={vals['n_auto']})  "
                     f"manual={_fmt(vals['manual_mean'])} (n={vals['n_manual']})")
    lines += ["", " Por domínio (média geral):"]
    for dom, vals in report["by_domain"].items():
        lines.append(f"  {dom:<24} auto={_fmt(vals['auto_mean'])} (n={vals['n_auto']})  "
                     f"manual={_fmt(vals['manual_mean'])} (n={vals['n_manual']})")
    lines += ["", " Interpretação:", "  " + report["interpretation"],
              "═══════════════════════════════════════════════════════════════"]
    return "\n".join(lines)


def _fmt(value: Optional[float]) -> str:
    return f"{value:.2f}" if value is not None else "—"
