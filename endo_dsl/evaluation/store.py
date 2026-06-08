"""Persistência e exportação de avaliações (RF25).

Registra avaliações em formato estruturado e as exporta em JSON e CSV, incluindo:
origem do protótipo (automático/manual), componentes utilizados, nível cognitivo
declarado, avaliadores e pontuações por dimensão.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from endo_dsl.db.database import Database, from_json, now_iso, to_json
from endo_dsl.evaluation.instrument import (
    INSTRUMENT_VERSION,
    dimension_keys,
    overall_score,
    validate_scores,
)


@dataclass
class EvaluationRecord:
    id: int
    prototype_id: Optional[int]
    origin: str
    evaluator: Optional[str]
    bloom_level: Optional[str]
    domain: Optional[str]
    components_used: List[str] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)
    comments: str = ""
    instrument_version: str = INSTRUMENT_VERSION
    created_at: str = ""

    @property
    def overall(self) -> float:
        return overall_score(self.scores)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "prototype_id": self.prototype_id,
            "origin": self.origin,
            "evaluator": self.evaluator,
            "bloom_level": self.bloom_level,
            "domain": self.domain,
            "components_used": self.components_used,
            "scores": self.scores,
            "overall": self.overall,
            "comments": self.comments,
            "instrument_version": self.instrument_version,
            "created_at": self.created_at,
        }


class EvaluationStore:
    """Armazena e recupera avaliações de protótipos (RF25)."""

    def __init__(self, db: Database):
        self.db = db

    def record(self, *, scores: Dict[str, float], origin: str,
               prototype_id: Optional[int] = None,
               evaluator: Optional[str] = None,
               bloom_level: Optional[str] = None,
               domain: Optional[str] = None,
               components_used: Optional[List[str]] = None,
               comments: str = "") -> int:
        """Registra uma avaliação (RF24/RF25)."""
        if origin not in ("auto", "manual", "hybrid"):
            raise ValueError("origin deve ser 'auto', 'manual' ou 'hybrid'")
        clean = validate_scores(scores)
        eval_id = self.db.insert(
            """INSERT INTO evaluations
               (prototype_id, origin, evaluator, bloom_level, domain,
                components_used_json, scores_json, comments, instrument_version, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (prototype_id, origin, evaluator, bloom_level, domain,
             to_json(components_used or []), to_json(clean), comments,
             INSTRUMENT_VERSION, now_iso()),
        )
        return eval_id

    def get(self, eval_id: int) -> Optional[EvaluationRecord]:
        row = self.db.query_one("SELECT * FROM evaluations WHERE id = ?", (eval_id,))
        return self._row(row) if row else None

    def list(self, *, origin: Optional[str] = None,
             prototype_id: Optional[int] = None) -> List[EvaluationRecord]:
        where = []
        params: List[Any] = []
        if origin:
            where.append("origin = ?")
            params.append(origin)
        if prototype_id is not None:
            where.append("prototype_id = ?")
            params.append(prototype_id)
        clause = (" WHERE " + " AND ".join(where)) if where else ""
        rows = self.db.query_all(
            f"SELECT * FROM evaluations{clause} ORDER BY created_at DESC", params)
        return [self._row(r) for r in rows]

    def _row(self, row) -> EvaluationRecord:
        return EvaluationRecord(
            id=row["id"],
            prototype_id=row["prototype_id"],
            origin=row["origin"],
            evaluator=row["evaluator"],
            bloom_level=row["bloom_level"],
            domain=row["domain"],
            components_used=from_json(row["components_used_json"], []),
            scores=from_json(row["scores_json"], {}),
            comments=row["comments"] or "",
            instrument_version=row["instrument_version"] or INSTRUMENT_VERSION,
            created_at=row["created_at"],
        )

    # ------------------------------------------------------------------ #
    # Exportação estruturada (RF25)
    # ------------------------------------------------------------------ #
    def export_json(self, **filters) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self.list(**filters)]

    def export_csv(self, **filters) -> str:
        """Exporta as avaliações como CSV (uma linha por avaliação)."""
        records = self.list(**filters)
        dims = dimension_keys()
        header = (["id", "prototype_id", "origin", "evaluator", "bloom_level",
                   "domain", "components_used", "overall"] + dims +
                  ["instrument_version", "created_at", "comments"])
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(header)
        for r in records:
            writer.writerow(
                [r.id, r.prototype_id, r.origin, r.evaluator, r.bloom_level,
                 r.domain, ";".join(r.components_used), r.overall]
                + [r.scores.get(d, "") for d in dims]
                + [r.instrument_version, r.created_at, r.comments]
            )
        return buf.getvalue()
