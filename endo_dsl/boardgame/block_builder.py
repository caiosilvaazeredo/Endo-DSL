"""Construtor de blocos MDA — config de blocos -> DSL boardgame{} -> HTML5.

Recebe a configuração do Construtor (``/builder``): blocos de mecânica,
dinâmica e estética selecionados/parametrizados em painéis separados, mais o
fluxo desenhado no editor BPMN. Emite a DSL ``boardgame{}`` equivalente e
compila o protótipo jogável aplicando o tema estético e as fases do fluxo.

Formato da config::

    {
      "title": "...", "domain": "...", "topic": "...", "bloom": "Analisar",
      "players": 4, "duration": 30, "age_range": "10-14",
      "objective": "texto do objetivo de aprendizagem",
      "mechanics":  [{"id": "roll_and_move", "params": {"dice": "2d6"}}, ...],
      "dynamics":   ["corrida", "tensao_crescente", ...],
      "aesthetics": ["fantasia_medieval", ...],
      "flow": {"nodes": [{"id","type","label","ref"}],
               "edges": [{"from","to","label"}]}
    }
"""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any, Dict, List, Optional

from endo_dsl.boardgame.catalogs import (
    AESTHETICS_BLOCKS,
    DYNAMICS_BLOCKS,
    MECHANICS_BLOCKS,
)

_BLOOM_NAMES = ["Lembrar", "Compreender", "Aplicar", "Analisar", "Avaliar", "Criar"]


def _ident(label: str, fallback: str = "bloco") -> str:
    """Converte um rótulo livre em identificador DSL válido."""
    norm = unicodedata.normalize("NFKD", str(label)).encode("ascii", "ignore").decode()
    norm = re.sub(r"[^A-Za-z0-9_]+", "_", norm).strip("_").lower()
    if not norm or norm[0].isdigit():
        norm = f"{fallback}_{norm}" if norm else fallback
    return norm


def _fmt_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return '"' + str(v).replace('"', "'") + '"'


def _game_type_from_blocks(mech_blocks: List[Dict[str, Any]]) -> str:
    """Tipo de jogo dominante a partir dos dsl_type dos blocos de mecânica."""
    votes: Dict[str, int] = {}
    for b in mech_blocks:
        cat = MECHANICS_BLOCKS.get(b["id"], {})
        t = cat.get("dsl_type", "trilha")
        votes[t] = votes.get(t, 0) + 1
    if not votes:
        return "trilha"
    return max(votes.items(), key=lambda kv: kv[1])[0]


_DSL_TYPE_TO_BOARD = {
    "trilha": "track",
    "quiz_battle": "quiz",
    "memory_match": "cards",
    "cards_only": "cards",
    "strategy_grid": "grid",
    "cooperative_quest": "track",
}


def blocks_to_dsl(config: Dict[str, Any]) -> str:
    """Emite a DSL boardgame{} a partir da configuração de blocos MDA + fluxo."""
    title = str(config.get("title") or "Jogo de Blocos").replace('"', "'")
    domain = str(config.get("domain") or "Geral")
    topic = str(config.get("topic") or domain)
    bloom = config.get("bloom") or "Analisar"
    if bloom not in _BLOOM_NAMES:
        bloom = "Analisar"
    players = int(config.get("players") or 2)
    duration = int(config.get("duration") or 30)
    age_range = str(config.get("age_range") or "10-14")
    objective = str(config.get("objective") or
                    f"Praticar {topic} no nível {bloom}").replace('"', "'")

    mech_sel: List[Dict[str, Any]] = [
        m if isinstance(m, dict) else {"id": m, "params": {}}
        for m in config.get("mechanics", [])
        if (m["id"] if isinstance(m, dict) else m) in MECHANICS_BLOCKS
    ]
    dyn_sel = [d for d in config.get("dynamics", []) if d in DYNAMICS_BLOCKS]
    aes_sel = [a for a in config.get("aesthetics", []) if a in AESTHETICS_BLOCKS]
    flow = config.get("flow") or {}

    game_type = _game_type_from_blocks(mech_sel)
    board_type = _DSL_TYPE_TO_BOARD.get(game_type, "track")

    L: List[str] = []
    L.append(f'boardgame "{title}" {{')
    L.append("  metadata {")
    L.append(f'    domain: "{domain}"')
    L.append(f'    topic: "{topic}"')
    L.append(f"    bloom: {bloom}")
    L.append(f'    age_range: "{age_range}"')
    L.append(f"    duration: {duration}")
    L.append(f"    players: {players}")
    L.append("  }")
    L.append("")
    L.append("  objective obj_principal {")
    L.append(f'    description: "{objective}"')
    L.append(f"    bloom: {bloom}")
    L.append("  }")

    # --- mecânicas: um bloco mechanic por bloco lógico selecionado --------- #
    for m in mech_sel:
        cat = MECHANICS_BLOCKS[m["id"]]
        mid = _ident(m["id"], "mec")
        params = dict(cat.get("params", {}))
        params.update({k: v for k, v in (m.get("params") or {}).items()
                       if k in params or True})
        bl = _BLOOM_NAMES[max(0, min(5, int(cat.get("bloom", 3)) - 1))]
        L.append("")
        L.append(f"  mechanic {mid} {{")
        L.append(f'    type: {cat.get("dsl_type", "trilha")}')
        L.append(f"    bloom: {bl}")
        L.append("    addresses: obj_principal")
        desc = f'{cat["name"]} — {cat["desc"]} (inspirado em: {cat["inspired_by"]})'
        L.append(f'    description: "{desc.replace(chr(34), chr(39))}"')
        if params:
            L.append("    params {")
            for k, v in params.items():
                L.append(f"      {_ident(k)}: {_fmt_value(v)}")
            L.append("    }")
        L.append("  }")

    # --- board derivado do tipo dominante ----------------------------------- #
    L.append("")
    L.append("  board {")
    L.append(f"    type: {board_type}")
    if board_type == "grid":
        rows = cols = 8
        for m in mech_sel:
            p = {**MECHANICS_BLOCKS[m["id"]].get("params", {}), **(m.get("params") or {})}
            rows = int(p.get("rows", rows)); cols = int(p.get("cols", cols))
        L.append(f"    rows: {rows}")
        L.append(f"    cols: {cols}")
    L.append("  }")

    # --- regras: fluxo BPMN vira fases de turno ------------------------------ #
    phases = _flow_to_phases(flow, mech_sel)
    L.append("")
    L.append("  rules {")
    L.append('    turn_order: "sequencial"')
    win = _win_condition(flow) or f"Atingir o objetivo de {topic} primeiro"
    L.append(f'    win_condition: "{win.replace(chr(34), chr(39))}"')
    for ph in phases:
        L.append(f"    phase {_ident(ph['id'], 'fase')} {{")
        L.append(f'      action: "{str(ph["label"]).replace(chr(34), chr(39))}"')
        L.append(f"      required: {_fmt_value(bool(ph.get('required', True)))}")
        L.append("    }")
    L.append("  }")

    # --- gdc: registra dinâmicas, estéticas e fluxo (rastreabilidade MDA) ---- #
    L.append("")
    L.append("  gdc {")
    if mech_sel:
        L.append(f'    mechanics: "{", ".join(MECHANICS_BLOCKS[m["id"]]["name"] for m in mech_sel)}"')
    if dyn_sel:
        L.append(f'    dynamics: "{", ".join(DYNAMICS_BLOCKS[d]["name"] for d in dyn_sel)}"')
    if aes_sel:
        L.append(f'    aesthetics: "{", ".join(AESTHETICS_BLOCKS[a]["name"] for a in aes_sel)}"')
    if flow.get("nodes"):
        chain = " -> ".join(str(n.get("label") or n.get("type"))
                            for n in flow["nodes"])
        L.append(f'    flow: "{chain.replace(chr(34), chr(39))}"')
    insp = sorted({MECHANICS_BLOCKS[m["id"]]["inspired_by"] for m in mech_sel})
    if insp:
        L.append(f'    inspired_by: "{"; ".join(insp)}"')
    L.append("  }")
    L.append("}")
    return "\n".join(L) + "\n"


def _flow_to_phases(flow: Dict[str, Any],
                    mech_sel: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ordena os nós do fluxo (BFS pelas arestas) e converte em fases de turno."""
    nodes = {n["id"]: n for n in flow.get("nodes", []) if n.get("id")}
    edges = flow.get("edges", [])
    if not nodes:
        # fluxo padrão: uma fase por mecânica
        return [{"id": m["id"], "label": MECHANICS_BLOCKS[m["id"]]["name"]}
                for m in mech_sel] or [{"id": "jogada", "label": "Jogada do jogador"}]
    succ: Dict[str, List[str]] = {}
    indeg: Dict[str, int] = {nid: 0 for nid in nodes}
    for e in edges:
        a, b = e.get("from"), e.get("to")
        if a in nodes and b in nodes:
            succ.setdefault(a, []).append(b)
            indeg[b] += 1
    order: List[str] = []
    queue = [nid for nid, d in indeg.items() if d == 0] or list(nodes)
    seen = set()
    while queue:
        nid = queue.pop(0)
        if nid in seen:
            continue
        seen.add(nid)
        order.append(nid)
        for nb in succ.get(nid, []):
            if nb not in seen:
                queue.append(nb)
    phases = []
    for nid in order:
        n = nodes[nid]
        if n.get("type") in ("start", "end"):
            continue
        phases.append({"id": nid, "label": n.get("label") or n.get("type", "fase"),
                       "required": n.get("type") != "event"})
    return phases or [{"id": "jogada", "label": "Jogada do jogador"}]


def _win_condition(flow: Dict[str, Any]) -> Optional[str]:
    for n in flow.get("nodes", []):
        if n.get("type") == "end" and n.get("label"):
            return str(n["label"])
    return None


# --------------------------------------------------------------------------- #
# Compilação: blocos -> DSL -> HTML5 com tema estético + fluxo embutidos
# --------------------------------------------------------------------------- #

def compile_blocks(config: Dict[str, Any]) -> Dict[str, Any]:
    """Compila a config de blocos em protótipo HTML5 jogável.

    Retorna ``{"dsl", "html", "content_pack", "traceability", "metadata"}``.
    """
    from endo_dsl.boardgame.compiler import compile_boardgame_source

    dsl_source = blocks_to_dsl(config)
    result = compile_boardgame_source(
        dsl_source, domain=config.get("domain"), topic=config.get("topic"))

    aes_sel = [a for a in config.get("aesthetics", []) if a in AESTHETICS_BLOCKS]
    dyn_sel = [d for d in config.get("dynamics", []) if d in DYNAMICS_BLOCKS]
    html = result["html"]
    if aes_sel:
        html = _apply_aesthetic_theme(html, aes_sel[0])
    if config.get("flow", {}).get("nodes"):
        html = _inject_flow_banner(html, config["flow"])
    result["html"] = html
    result["dsl"] = dsl_source

    trace = result.get("traceability") or {}
    trace["mda"] = {
        "mechanics": [m["id"] if isinstance(m, dict) else m
                      for m in config.get("mechanics", [])],
        "dynamics": dyn_sel,
        "aesthetics": aes_sel,
        "flow_nodes": len(config.get("flow", {}).get("nodes", [])),
    }
    result["traceability"] = trace
    return result


def _apply_aesthetic_theme(html: str, aesthetic_id: str) -> str:
    """Injeta o tema visual do bloco estético como CSS de sobreposição."""
    theme = AESTHETICS_BLOCKS[aesthetic_id]["theme"]
    name = AESTHETICS_BLOCKS[aesthetic_id]["name"]
    css = f"""
/* Tema estético Endo-DSL: {name} */
:root {{
  --bg: {theme['bg']} !important;
  --surface: {theme['surface']} !important;
  --primary: {theme['primary']} !important;
  --secondary: {theme['secondary']} !important;
  --text: {theme['text']} !important;
}}
body {{
  background: {theme['bg']} !important;
  color: {theme['text']} !important;
  font-family: {theme['font']}, sans-serif !important;
}}
body .card, body .panel, body .board-space, body .question-card,
body [class*="card"], body [class*="panel"] {{
  background: {theme['surface']};
  color: {theme['text']};
}}
body button, body .btn {{
  background: {theme['primary']};
  color: #fff;
}}
body button:hover, body .btn:hover {{ background: {theme['secondary']}; }}
"""
    return html.replace("</head>", f"<style>{css}</style>\n</head>", 1)


def _inject_flow_banner(html: str, flow: Dict[str, Any]) -> str:
    """Embute o fluxo BPMN no jogo como faixa de fases navegável."""
    nodes = [n for n in flow.get("nodes", [])
             if n.get("type") not in ("start", "end")]
    if not nodes:
        return html
    steps = "".join(
        f'<span class="endo-flow-step" data-node="{n.get("id", i)}">'
        f'{i + 1}. {str(n.get("label") or n.get("type", "fase"))}</span>'
        for i, n in enumerate(nodes))
    banner = f"""
<style>
.endo-flow-bar {{ display:flex; gap:.4rem; flex-wrap:wrap; padding:.45rem .8rem;
  font: 12px/1.4 system-ui, sans-serif; background: rgba(0,0,0,.55); color:#fff;
  position: sticky; top: 0; z-index: 999; }}
.endo-flow-step {{ padding:.15rem .55rem; border-radius:999px;
  background: rgba(255,255,255,.14); white-space: nowrap; }}
.endo-flow-step.active {{ background:#4f46e5; font-weight:700; }}
</style>
<div class="endo-flow-bar" id="endo-flow-bar">{steps}</div>
<script>
(function() {{
  var i = 0, steps = document.querySelectorAll('#endo-flow-bar .endo-flow-step');
  if (!steps.length) return;
  function mark() {{ steps.forEach(function(s, k) {{ s.classList.toggle('active', k === i); }}); }}
  mark();
  window.endoFlowNext = function() {{ i = (i + 1) % steps.length; mark(); }};
  document.addEventListener('click', function(ev) {{
    if (ev.target.closest('button')) window.endoFlowNext();
  }});
}})();
</script>
"""
    return html.replace("<body>", "<body>" + banner, 1)
