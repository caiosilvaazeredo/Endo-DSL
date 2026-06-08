"""Orquestração do pipeline multi-agente (RF13, RF17, RF18).

Encadeia recuperação -> geração -> validação, com refinamento iterativo. Registra
TODA tentativa (válida ou inválida) no banco — prompts, componentes selecionados e
erros (RF17) — e expõe métricas de qualidade da geração (RF18).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from endo_dsl.agents.context import DesignContext
from endo_dsl.agents.generation import GenerationAgent
from endo_dsl.agents.llm import LLMBackend, get_backend
from endo_dsl.agents.retrieval import RetrievalAgent, RetrievedComponent
from endo_dsl.agents.validation import ValidationAgent, ValidationReport
from endo_dsl.db.database import Database, from_json, now_iso, to_json
from endo_dsl.library.repository import ComponentRepository


@dataclass
class PipelineResult:
    """Resultado da execução do pipeline."""

    success: bool
    dsl: str
    report: ValidationReport
    selected_components: List[RetrievedComponent] = field(default_factory=list)
    attempts: List[Dict[str, Any]] = field(default_factory=list)
    backend: str = "template"
    session_id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "dsl": self.dsl,
            "validation": self.report.to_dict(),
            "selected_components": [rc.to_dict() for rc in self.selected_components],
            "attempts": self.attempts,
            "backend": self.backend,
            "session_id": self.session_id,
        }


class Pipeline:
    """Pipeline multi-agente Endo-DSL."""

    def __init__(self, db: Database, *, repo: Optional[ComponentRepository] = None,
                 backend: Optional[LLMBackend] = None):
        self.db = db
        self.repo = repo or ComponentRepository(db)
        self.backend = backend or get_backend()
        self.retrieval = RetrievalAgent(self.repo)
        self.generation = GenerationAgent(self.backend)
        self.validation = ValidationAgent()

    # ------------------------------------------------------------------ #
    def retrieve(self, context: DesignContext, *, top_k: int = 5) -> List[RetrievedComponent]:
        """Aciona apenas o agente de recuperação (Fase 2 da jornada — RF14)."""
        return self.retrieval.retrieve(context, top_k=top_k)

    def components_from_keys(self, keys: List[str]) -> List[RetrievedComponent]:
        """Constrói seleção a partir de chaves de componentes (seleção manual do usuário)."""
        out: List[RetrievedComponent] = []
        for k in keys:
            comp = self.repo.get_by_key(k)
            if comp:
                out.append(RetrievedComponent(comp, 1.0, ["selecionado manualmente"]))
        return out

    # ------------------------------------------------------------------ #
    def run(self, context: DesignContext, *,
            components: Optional[List[RetrievedComponent]] = None,
            max_attempts: int = 3,
            session_id: Optional[int] = None,
            persist: bool = True,
            auto_retrieve: bool = True) -> PipelineResult:
        """Executa o pipeline completo com refinamento iterativo (RF15–RF18)."""
        if components is None and auto_retrieve:
            components = self.retrieve(context)
        components = components or []

        attempts_log: List[Dict[str, Any]] = []
        best_report: Optional[ValidationReport] = None
        best_dsl = ""
        feedback: Optional[str] = None

        for attempt_no in range(1, max_attempts + 1):
            dsl = self.generation.generate(context, components, feedback=feedback)
            report = self.validation.validate(dsl, context)
            prompt = self._describe_prompt(context, components, feedback)

            if persist:
                self._log_attempt(session_id, attempt_no, prompt, components, dsl, report)

            entry = {
                "attempt_no": attempt_no,
                "dsl": dsl,
                "validation": report.to_dict(),
                "prompt": prompt,
            }
            attempts_log.append(entry)

            if best_report is None or self._score(report) > self._score(best_report):
                best_report, best_dsl = report, dsl

            if report.valid:
                break
            feedback = self._format_feedback(report)

        # Registra uso dos componentes na sessão (RF11).
        if persist and session_id is not None:
            for rc in components:
                self.repo.record_usage(
                    rc.component.id, session_id=session_id,
                    component_version=rc.component.current_version,
                )

        return PipelineResult(
            success=bool(best_report and best_report.valid),
            dsl=best_dsl,
            report=best_report or ValidationReport(),
            selected_components=components,
            attempts=attempts_log,
            backend=self.generation.backend_name,
            session_id=session_id,
        )

    # ------------------------------------------------------------------ #
    @staticmethod
    def _score(report: ValidationReport) -> int:
        return sum([report.syntactic_ok, report.semantic_ok,
                    report.pedagogical_ok, report.params_ok])

    @staticmethod
    def _describe_prompt(ctx: DesignContext, components, feedback) -> str:
        keys = ", ".join(rc.component.key for rc in components) or "(nenhum)"
        base = (f"objetivo='{ctx.learning_objective}' | domínio='{ctx.domain}' | "
                f"bloom='{ctx.bloom_target.pt}' | componentes=[{keys}]")
        if feedback:
            base += f" | refinamento: {feedback}"
        return base

    @staticmethod
    def _format_feedback(report: ValidationReport) -> str:
        return "; ".join(e.get("message", "") for e in report.errors)[:500]

    def _log_attempt(self, session_id, attempt_no, prompt, components,
                     dsl, report: ValidationReport) -> None:
        self.db.execute(
            """INSERT INTO generation_attempts
               (session_id, attempt_no, prompt, selected_components_json, generated_dsl,
                syntactic_ok, semantic_ok, pedagogical_ok, params_ok, valid,
                errors_json, backend, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (session_id, attempt_no, prompt,
             to_json([rc.component.key for rc in components]), dsl,
             int(report.syntactic_ok), int(report.semantic_ok),
             int(report.pedagogical_ok), int(report.params_ok), int(report.valid),
             to_json(report.errors), self.generation.backend_name, now_iso()),
        )
        self.db.commit()

    # ------------------------------------------------------------------ #
    # RF18 — Métricas de qualidade da geração
    # ------------------------------------------------------------------ #
    def metrics(self, session_id: Optional[int] = None) -> Dict[str, Any]:
        """Taxa de validade na 1ª tentativa, taxa de rejeição e erros mais frequentes."""
        where = "WHERE session_id = ?" if session_id is not None else ""
        params = (session_id,) if session_id is not None else ()

        total = self.db.query_one(
            f"SELECT COUNT(*) AS c FROM generation_attempts {where}", params)["c"] or 0
        valid_total = self.db.query_one(
            f"SELECT COUNT(*) AS c FROM generation_attempts {where} "
            f"{'AND' if where else 'WHERE'} valid = 1", params)["c"] or 0

        first_clause = (where + " AND attempt_no = 1") if where else "WHERE attempt_no = 1"
        first_total = self.db.query_one(
            f"SELECT COUNT(*) AS c FROM generation_attempts {first_clause}", params)["c"] or 0
        first_valid = self.db.query_one(
            f"SELECT COUNT(*) AS c FROM generation_attempts {first_clause} AND valid = 1",
            params)["c"] or 0

        # Tipos de erro mais frequentes.
        rows = self.db.query_all(
            f"SELECT errors_json FROM generation_attempts {where} "
            f"{'AND' if where else 'WHERE'} valid = 0", params)
        codes: Counter = Counter()
        for r in rows:
            for err in from_json(r["errors_json"], []):
                codes[err.get("code") or err.get("kind") or "?"] += 1

        return {
            "total_attempts": total,
            "valid_attempts": valid_total,
            "first_attempt_valid_rate": round(first_valid / first_total, 3) if first_total else None,
            "rejection_rate": round((total - valid_total) / total, 3) if total else None,
            "most_frequent_errors": codes.most_common(8),
            "backend": self.generation.backend_name,
        }
