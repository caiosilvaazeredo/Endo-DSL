"""Fachada da plataforma Endo-DSL.

Integra os cinco módulos e materializa a jornada do usuário (Fases 1–7 e jornada
do curador) numa API de alto nível, reaproveitada pela CLI e pela interface web.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from endo_dsl.agents.context import DesignContext
from endo_dsl.agents.llm import LLMBackend, get_backend
from endo_dsl.agents.pipeline import Pipeline, PipelineResult
from endo_dsl.compiler.compiler import CompileError, compile_source, reparametrize_content
from endo_dsl.db.database import Database, default_db_path, from_json, now_iso, to_json
from endo_dsl.dsl.parser import ParseError, parse
from endo_dsl.dsl.semantic import validate_semantics
from endo_dsl.evaluation.reports import comparative_report, report_as_text
from endo_dsl.evaluation.store import EvaluationStore
from endo_dsl.library.models import SearchFilters
from endo_dsl.library.repository import ComponentRepository
from endo_dsl.library.seed import seed_canonical


class Platform:
    """Ponto único de acesso aos subsistemas da Endo-DSL."""

    def __init__(self, db_path: Optional[str] = None, *,
                 backend: Optional[LLMBackend] = None,
                 workspace: Optional[str] = None,
                 seed: bool = True):
        self.db = Database(db_path or str(default_db_path()))
        self.repo = ComponentRepository(self.db)
        self.backend = backend or get_backend()
        self.pipeline = Pipeline(self.db, repo=self.repo, backend=self.backend)
        self.evaluations = EvaluationStore(self.db)
        ws = workspace or str(Path(self.db.path).parent / "prototypes")
        self.workspace = Path(ws)
        self.workspace.mkdir(parents=True, exist_ok=True)
        if seed:
            seed_canonical(self.repo)

    def close(self) -> None:
        self.db.close()

    # ================================================================== #
    # Fase 1 — Sessão de design (contexto educacional) — RF13
    # ================================================================== #
    def create_session(self, name: str, context: Dict[str, Any]) -> int:
        ctx = DesignContext.from_dict(context)
        return self.db.insert(
            """INSERT INTO design_sessions
               (name, domain, learning_objective, bloom_target, learner_profile_json,
                constraints_json, status, created_at)
               VALUES (?,?,?,?,?,?, 'open', ?)""",
            (name, ctx.domain, ctx.learning_objective, ctx.bloom_target.pt,
             to_json({"age_range": ctx.age_range, "education_level": ctx.education_level,
                      "learner_context": ctx.learner_context}),
             to_json({"duration_minutes": ctx.duration_minutes, "platform": ctx.platform,
                      "no_extensive_reading": ctx.no_extensive_reading,
                      "topic": ctx.topic, "title": ctx.title, **ctx.extra}),
             now_iso()),
        )

    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.query_one("SELECT * FROM design_sessions WHERE id = ?", (session_id,))
        if not row:
            return None
        d = dict(row)
        d["learner_profile"] = from_json(d.pop("learner_profile_json"), {})
        d["constraints"] = from_json(d.pop("constraints_json"), {})
        return d

    def session_context(self, session_id: int) -> DesignContext:
        s = self.get_session(session_id)
        if not s:
            raise KeyError(f"sessão {session_id} não encontrada")
        data = {
            "learning_objective": s["learning_objective"],
            "domain": s["domain"],
            "bloom_target": s["bloom_target"],
            **(s.get("learner_profile") or {}),
            **(s.get("constraints") or {}),
        }
        return DesignContext.from_dict(data)

    # ================================================================== #
    # Fase 2 — Recuperação de componentes — RF14
    # ================================================================== #
    def retrieve(self, context: DesignContext, *, top_k: int = 5):
        return self.pipeline.retrieve(context, top_k=top_k)

    def search_components(self, filters: Optional[SearchFilters] = None, **kwargs):
        return self.repo.search(filters or SearchFilters(**kwargs))

    def get_component(self, key: str):
        return self.repo.get_by_key(key)

    # ================================================================== #
    # Fase 3 — Geração da especificação DSL — RF15–RF18
    # ================================================================== #
    def generate(self, session_id: int, *,
                 selected_keys: Optional[List[str]] = None,
                 from_scratch: bool = False,
                 max_attempts: int = 3) -> PipelineResult:
        ctx = self.session_context(session_id)
        components = None
        if selected_keys is not None:
            components = self.pipeline.components_from_keys(selected_keys)
        elif from_scratch:
            components = []
        return self.pipeline.run(ctx, components=components, session_id=session_id,
                                 max_attempts=max_attempts,
                                 auto_retrieve=not from_scratch)

    def generation_metrics(self, session_id: Optional[int] = None) -> Dict[str, Any]:
        return self.pipeline.metrics(session_id)

    # ================================================================== #
    # Fase 4 — Validação em tempo real (revisão pelo usuário) — RF03/RF04
    # ================================================================== #
    def validate(self, dsl_source: str) -> Dict[str, Any]:
        """Valida sintaxe + semântica de uma especificação (para o editor — RF05)."""
        try:
            spec = parse(dsl_source)
        except ParseError as exc:
            return {"syntactic_ok": False, "semantic_ok": False,
                    "errors": [exc.to_dict()], "warnings": []}
        issues = [i.to_dict() for i in validate_semantics(spec)]
        errors = [i for i in issues if i["severity"] == "error"]
        warnings = [i for i in issues if i["severity"] == "warning"]
        return {
            "syntactic_ok": True,
            "semantic_ok": not errors,
            "errors": errors,
            "warnings": warnings,
            "title": spec.title,
            "bloom_levels": [b.pt for b in spec.bloom_levels],
        }

    # ================================================================== #
    # Fase 5 — Compilação e geração do protótipo — RF19–RF23
    # ================================================================== #
    def compile(self, dsl_source: str, *,
                session_id: Optional[int] = None,
                origin: str = "manual",
                title: Optional[str] = None) -> Dict[str, Any]:
        """Compila a DSL, persiste especificação e protótipo, escreve artefatos."""
        result = compile_source(dsl_source)  # levanta CompileError (RF20)

        spec_id = self.db.insert(
            """INSERT INTO specifications (session_id, title, dsl_source, origin, parsed_ok, created_at)
               VALUES (?,?,?,?,1,?)""",
            (session_id, title or result.spec.title, dsl_source, origin, now_iso()),
        )
        out_dir = self.workspace / f"proto_{spec_id}"
        paths = result.write(out_dir, basename="prototype")

        proto_id = self.db.insert(
            """INSERT INTO prototypes
               (spec_id, session_id, title, html_path, traceability_json, bloom_levels_json,
                origin, compiled_ok, created_at)
               VALUES (?,?,?,?,?,?,?,1,?)""",
            (spec_id, session_id, result.spec.title, paths["html"],
             to_json(result.traceability), to_json(result.bloom_levels), origin, now_iso()),
        )

        # RF11 — taxa de sucesso na compilação por componente utilizado.
        self._record_component_compiles(result.spec, session_id, proto_id, ok=True)

        return {
            "prototype_id": proto_id,
            "spec_id": spec_id,
            "title": result.spec.title,
            "paths": paths,
            "html": result.html,
            "traceability": result.traceability,
            "bloom_levels": result.bloom_levels,
            "warnings": result.warnings,
        }

    def _record_component_compiles(self, spec, session_id, proto_id, *, ok: bool) -> None:
        for m in spec.mechanics:
            if not m.source_component:
                continue
            comp = self.repo.get_by_key(m.source_component, with_metrics=False)
            if comp:
                self.repo.record_usage(comp.id, session_id=session_id,
                                       prototype_id=proto_id, compiled_ok=ok,
                                       component_version=comp.current_version)

    def get_prototype(self, prototype_id: int) -> Optional[Dict[str, Any]]:
        row = self.db.query_one("SELECT * FROM prototypes WHERE id = ?", (prototype_id,))
        if not row:
            return None
        d = dict(row)
        d["traceability"] = from_json(d.pop("traceability_json"), {})
        d["bloom_levels"] = from_json(d.pop("bloom_levels_json"), [])
        return d

    def list_prototypes(self) -> List[Dict[str, Any]]:
        rows = self.db.query_all("SELECT * FROM prototypes ORDER BY created_at DESC")
        return [dict(r) for r in rows]

    def prototype_html(self, prototype_id: int) -> Optional[str]:
        proto = self.get_prototype(prototype_id)
        if not proto or not proto.get("html_path"):
            return None
        p = Path(proto["html_path"])
        return p.read_text(encoding="utf-8") if p.exists() else None

    # RF22 — Reparametrização de conteúdo (troca de domínio sem recompilar).
    def reparametrize(self, prototype_id: int, *, domain: Optional[str] = None,
                      topic: Optional[str] = None) -> Dict[str, Any]:
        html = self.prototype_html(prototype_id)
        if html is None:
            raise KeyError(f"protótipo {prototype_id} não encontrado")
        new_html = reparametrize_content(html, domain=domain, topic=topic)
        proto = self.get_prototype(prototype_id)
        out_path = Path(proto["html_path"]).with_name("prototype.reparam.html")
        out_path.write_text(new_html, encoding="utf-8")
        return {"prototype_id": prototype_id, "path": str(out_path),
                "domain": domain, "html": new_html}

    # ================================================================== #
    # Fase 6 — Avaliação pedagógica — RF24–RF26
    # ================================================================== #
    def evaluate(self, *, scores: Dict[str, float], origin: str,
                 prototype_id: Optional[int] = None, evaluator: Optional[str] = None,
                 bloom_level: Optional[str] = None, domain: Optional[str] = None,
                 components_used: Optional[List[str]] = None, comments: str = "") -> int:
        # Enriquece automaticamente a partir do protótipo, se houver.
        if prototype_id is not None:
            proto = self.get_prototype(prototype_id)
            if proto:
                bloom_level = bloom_level or (proto["bloom_levels"][-1]
                                              if proto["bloom_levels"] else None)
                domain = domain or (proto["traceability"] or {}).get("domain")
        return self.evaluations.record(
            scores=scores, origin=origin, prototype_id=prototype_id, evaluator=evaluator,
            bloom_level=bloom_level, domain=domain, components_used=components_used,
            comments=comments)

    def comparison_report(self, *, as_text: bool = False):
        rep = comparative_report(self.evaluations)
        return report_as_text(rep) if as_text else rep

    # ================================================================== #
    # Fase 7 / Jornada do curador — Biblioteca — RF07, RF12
    # ================================================================== #
    def contribute_component(self, **kwargs) -> int:
        """Submete um novo componente experimental (Fase 7)."""
        kwargs.setdefault("status", "experimental")
        return self.repo.create(**kwargs)

    def curation_queue(self):
        return self.repo.curation_queue()

    def approve_component(self, component_id: int, **kw) -> None:
        self.repo.approve(component_id, **kw)

    def reject_component(self, component_id: int, **kw) -> None:
        self.repo.reject(component_id, **kw)

    def request_component_changes(self, component_id: int, **kw) -> None:
        self.repo.request_changes(component_id, **kw)
