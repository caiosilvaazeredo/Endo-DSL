"""Compila BoardGameSpec (ou DSL fonte) para protótipo HTML5 jogável."""

from __future__ import annotations

from typing import Optional

from endo_dsl.boardgame.dsl_extension import parse_boardgame_dsl
from endo_dsl.boardgame.content_builder import build_board_content
from endo_dsl.boardgame.board_engine import render_board_game
from endo_dsl.boardgame.ast_nodes import BoardGameSpec


def compile_boardgame(spec: BoardGameSpec, domain: Optional[str] = None,
                      topic: Optional[str] = None) -> dict:
    """Compila um BoardGameSpec em HTML5 jogável.

    Returns dict com keys: html, content_pack, metadata, traceability.
    """
    spec_dict = {
        "title": spec.title,
        "metadata": dict(spec.metadata.values) if hasattr(spec.metadata, 'values') else {},
        "mechanics": [{"id": getattr(m, 'name', getattr(m, 'id', '')),
                       "type": getattr(m, 'type', getattr(m, 'mechanic_type', '')),
                       "bloom": m.bloom.value if m.bloom else 1,
                       "params": dict(m.params.entries) if hasattr(getattr(m, 'params', None), 'entries') else (m.params or {})}
                      for m in spec.mechanics],
        "board": ({
            "type": spec.board.type,
            "rows": spec.board.rows,
            "cols": spec.board.cols,
            "spaces": [s.__dict__ for s in spec.board.spaces],
        } if spec.board else {"type": "track"}),
        "rules": {},
        "objectives": [{"id": getattr(o, 'name', ''),
                        "description": getattr(o, 'description', ''),
                        "bloom": o.bloom.value if o.bloom else 1}
                       for o in spec.objectives],
    }

    _domain = domain or spec.metadata.get("domain", "generico")
    _topic = topic or spec.metadata.get("topic", "")

    content = build_board_content(spec_dict, domain=_domain, topic=_topic)
    content["title"] = spec.title

    html = render_board_game(content)

    objectives_total = len(spec.objectives)
    bloom_covered = set()
    for o in spec.objectives:
        if o.bloom:
            bloom_covered.add(o.bloom.value)
    traceability = {
        "objectives_total": objectives_total,
        "bloom_levels_covered": list(bloom_covered),
        "mechanics_used": [getattr(m, 'name', getattr(m, 'id', '')) for m in spec.mechanics],
        "content_questions": len(content.get("questions", [])),
    }

    return {
        "html": html,
        "content_pack": content,
        "metadata": {
            "title": spec.title,
            "domain": _domain,
            "topic": _topic,
            "bloom": spec.metadata.get("bloom", ""),
            "players": spec.metadata.get("players", "2-4"),
            "duration": spec.metadata.get("duration", 30),
            "board_type": content.get("board_type", "track"),
        },
        "traceability": traceability,
    }


def compile_boardgame_source(dsl_source: str, domain: Optional[str] = None,
                              topic: Optional[str] = None) -> dict:
    """Parse DSL boardgame e compila para HTML5."""
    spec = parse_boardgame_dsl(dsl_source)
    return compile_boardgame(spec, domain=domain, topic=topic)
