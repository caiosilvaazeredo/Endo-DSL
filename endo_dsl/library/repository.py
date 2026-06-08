"""Repositório da biblioteca de componentes (RF07–RF12).

Encapsula todas as operações de persistência sobre componentes: cadastro,
versionamento, enriquecimento, busca/filtragem, métricas de uso e curadoria.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional

from endo_dsl.db.database import Database, from_json, now_iso, to_json
from endo_dsl.dsl.bloom import parse_bloom
from endo_dsl.library.models import Component, ComponentMetrics, SearchFilters


def slugify(text: str) -> str:
    # Remove acentos (ç -> c, ã -> a) antes de gerar o slug.
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "_", ascii_text.lower()).strip("_")
    return s or "componente"


class ComponentRepository:
    """Acesso a componentes reutilizáveis sobre uma instância de :class:`Database`."""

    def __init__(self, db: Database):
        self.db = db

    # ------------------------------------------------------------------ #
    # RF07 — Cadastro
    # ------------------------------------------------------------------ #
    def create(
        self,
        *,
        name: str,
        dsl_signature: str,
        bloom_level: str,
        mechanic_type: str,
        description: str,
        params: Optional[Dict[str, Any]] = None,
        domain: Optional[str] = None,
        context: Optional[str] = None,
        age_range: Optional[str] = None,
        modality: Optional[str] = None,
        status: str = "experimental",
        author: Optional[str] = None,
        key: Optional[str] = None,
    ) -> int:
        """Cadastra um componente (RF07) e registra sua versão inicial (RF10).

        Campos obrigatórios por RF07: assinatura DSL, nível de Bloom, tipo de
        mecânica, parâmetros e descrição em linguagem natural.
        """
        self._validate_required(name, dsl_signature, bloom_level, mechanic_type, description)
        params = params or {}
        ts = now_iso()
        base_key = key or slugify(name)
        unique_key = self._unique_key(base_key)

        component_id = self.db.insert(
            """INSERT INTO components
               (key, name, current_version, dsl_signature, bloom_level, mechanic_type,
                description, params_json, domain, context, age_range, modality,
                status, author, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (unique_key, name, 1, dsl_signature, bloom_level, mechanic_type,
             description, to_json(params), domain, context, age_range, modality,
             status, author, ts, ts),
        )
        # Versão inicial (RF10)
        self.db.execute(
            """INSERT INTO component_versions
               (component_id, version, dsl_signature, params_json, description,
                change_note, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (component_id, 1, dsl_signature, to_json(params), description,
             "versão inicial", ts),
        )
        # Linha de enriquecimento vazia (RF08)
        self.db.execute(
            """INSERT INTO component_enrichment
               (component_id, case_studies_json, expert_eval_json, references_json, updated_at)
               VALUES (?, '[]', '[]', '[]', ?)""",
            (component_id, ts),
        )
        # Trilha de curadoria (RF12)
        self.db.execute(
            """INSERT INTO curation_log (component_id, action, curator, justification, created_at)
               VALUES (?, 'submit', ?, ?, ?)""",
            (component_id, author, "submissão inicial", ts),
        )
        self.db.commit()
        return component_id

    @staticmethod
    def _validate_required(name, dsl_signature, bloom_level, mechanic_type, description) -> None:
        missing = []
        if not name:
            missing.append("name")
        if not dsl_signature:
            missing.append("dsl_signature")
        if not bloom_level:
            missing.append("bloom_level")
        if not mechanic_type:
            missing.append("mechanic_type")
        if not description:
            missing.append("description")
        if missing:
            raise ValueError(f"campos obrigatórios ausentes (RF07): {', '.join(missing)}")
        if parse_bloom(bloom_level) is None:
            raise ValueError(f"nível de Bloom inválido: {bloom_level!r}")

    def _unique_key(self, base: str) -> str:
        key = base
        n = 2
        while self.db.query_one("SELECT 1 FROM components WHERE key = ?", (key,)):
            key = f"{base}_{n}"
            n += 1
        return key

    # ------------------------------------------------------------------ #
    # RF10 — Versionamento
    # ------------------------------------------------------------------ #
    def update(
        self,
        component_id: int,
        *,
        dsl_signature: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        change_note: str = "",
        **fields: Any,
    ) -> int:
        """Atualiza um componente criando uma NOVA versão (RF10).

        Retorna o novo número de versão. Demais metadados (domínio, contexto…)
        podem ser passados via ``fields``.
        """
        row = self.db.query_one("SELECT * FROM components WHERE id = ?", (component_id,))
        if row is None:
            raise KeyError(f"componente {component_id} não encontrado")

        new_sig = dsl_signature if dsl_signature is not None else row["dsl_signature"]
        new_params = params if params is not None else from_json(row["params_json"], {})
        new_desc = description if description is not None else row["description"]
        new_version = int(row["current_version"]) + 1
        ts = now_iso()

        # Campos de metadados atualizáveis
        updatable = {"bloom_level", "mechanic_type", "domain", "context",
                     "age_range", "modality", "name"}
        sets = ["current_version = ?", "dsl_signature = ?", "params_json = ?",
                "description = ?", "updated_at = ?"]
        vals: List[Any] = [new_version, new_sig, to_json(new_params), new_desc, ts]
        for fname, fval in fields.items():
            if fname in updatable:
                sets.append(f"{fname} = ?")
                vals.append(fval)
        vals.append(component_id)
        self.db.execute(f"UPDATE components SET {', '.join(sets)} WHERE id = ?", vals)

        self.db.execute(
            """INSERT INTO component_versions
               (component_id, version, dsl_signature, params_json, description,
                change_note, created_at)
               VALUES (?,?,?,?,?,?,?)""",
            (component_id, new_version, new_sig, to_json(new_params), new_desc,
             change_note or f"atualização para v{new_version}", ts),
        )
        self.db.commit()
        return new_version

    def versions(self, component_id: int) -> List[Dict[str, Any]]:
        """Histórico de versões de um componente (RF10)."""
        rows = self.db.query_all(
            "SELECT * FROM component_versions WHERE component_id = ? ORDER BY version",
            (component_id,),
        )
        return [
            {
                "version": r["version"],
                "dsl_signature": r["dsl_signature"],
                "params": from_json(r["params_json"], {}),
                "description": r["description"],
                "change_note": r["change_note"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]

    # ------------------------------------------------------------------ #
    # RF08 — Enriquecimento
    # ------------------------------------------------------------------ #
    def enrich(
        self,
        component_id: int,
        *,
        case_study: Optional[Any] = None,
        expert_evaluation: Optional[Any] = None,
        reference: Optional[Any] = None,
    ) -> None:
        """Adiciona estudo de caso, avaliação de especialista e/ou referência (RF08)."""
        row = self.db.query_one(
            "SELECT * FROM component_enrichment WHERE component_id = ?", (component_id,)
        )
        if row is None:
            raise KeyError(f"componente {component_id} não encontrado")
        cases = from_json(row["case_studies_json"], [])
        experts = from_json(row["expert_eval_json"], [])
        refs = from_json(row["references_json"], [])
        if case_study is not None:
            cases.append(case_study)
        if expert_evaluation is not None:
            experts.append(expert_evaluation)
        if reference is not None:
            refs.append(reference)
        self.db.execute(
            """UPDATE component_enrichment
               SET case_studies_json = ?, expert_eval_json = ?, references_json = ?,
                   updated_at = ?
               WHERE component_id = ?""",
            (to_json(cases), to_json(experts), to_json(refs), now_iso(), component_id),
        )
        self.db.commit()

    # ------------------------------------------------------------------ #
    # RF11 — Avaliações de usuários e métricas de uso
    # ------------------------------------------------------------------ #
    def add_rating(self, component_id: int, score: float, *,
                   evaluator: Optional[str] = None, comment: str = "") -> None:
        if not (0 <= score <= 5):
            raise ValueError("a avaliação deve estar entre 0 e 5")
        self.db.execute(
            """INSERT INTO component_ratings (component_id, evaluator, score, comment, created_at)
               VALUES (?,?,?,?,?)""",
            (component_id, evaluator, score, comment, now_iso()),
        )
        self.db.commit()

    def record_usage(self, component_id: int, *, session_id: Optional[int] = None,
                     prototype_id: Optional[int] = None,
                     compiled_ok: Optional[bool] = None,
                     component_version: Optional[int] = None) -> None:
        """Registra uma instanciação do componente (RF11)."""
        ok = None if compiled_ok is None else (1 if compiled_ok else 0)
        self.db.execute(
            """INSERT INTO component_usage
               (component_id, component_version, session_id, prototype_id, compiled_ok, created_at)
               VALUES (?,?,?,?,?,?)""",
            (component_id, component_version, session_id, prototype_id, ok, now_iso()),
        )
        self.db.commit()

    def metrics(self, component_id: int) -> ComponentMetrics:
        """Calcula as métricas de uso de um componente (RF11)."""
        inst = self.db.query_one(
            "SELECT COUNT(*) AS c FROM component_usage WHERE component_id = ?", (component_id,)
        )["c"]
        rating = self.db.query_one(
            "SELECT AVG(score) AS avg, COUNT(*) AS c FROM component_ratings WHERE component_id = ?",
            (component_id,),
        )
        compile_row = self.db.query_one(
            """SELECT COUNT(*) AS total, SUM(compiled_ok) AS ok
               FROM component_usage
               WHERE component_id = ? AND compiled_ok IS NOT NULL""",
            (component_id,),
        )
        total = compile_row["total"] or 0
        ok = compile_row["ok"] or 0
        return ComponentMetrics(
            instantiations=inst or 0,
            avg_rating=rating["avg"],
            rating_count=rating["c"] or 0,
            compile_success_rate=(ok / total) if total else None,
            compile_attempts=total,
        )

    # ------------------------------------------------------------------ #
    # Leitura
    # ------------------------------------------------------------------ #
    def get(self, component_id: int, *, with_metrics: bool = True) -> Optional[Component]:
        row = self.db.query_one("SELECT * FROM components WHERE id = ?", (component_id,))
        if row is None:
            return None
        return self._row_to_component(row, with_metrics=with_metrics)

    def get_by_key(self, key: str, *, with_metrics: bool = True) -> Optional[Component]:
        row = self.db.query_one("SELECT * FROM components WHERE key = ?", (key,))
        if row is None:
            return None
        return self._row_to_component(row, with_metrics=with_metrics)

    def _row_to_component(self, row, *, with_metrics: bool = True) -> Component:
        enr = self.db.query_one(
            "SELECT * FROM component_enrichment WHERE component_id = ?", (row["id"],)
        )
        comp = Component(
            id=row["id"],
            key=row["key"],
            name=row["name"],
            current_version=row["current_version"],
            dsl_signature=row["dsl_signature"],
            bloom_level=row["bloom_level"],
            mechanic_type=row["mechanic_type"],
            description=row["description"],
            params=from_json(row["params_json"], {}),
            domain=row["domain"],
            context=row["context"],
            age_range=row["age_range"],
            modality=row["modality"],
            status=row["status"],
            author=row["author"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            case_studies=from_json(enr["case_studies_json"], []) if enr else [],
            expert_evaluations=from_json(enr["expert_eval_json"], []) if enr else [],
            references=from_json(enr["references_json"], []) if enr else [],
        )
        if with_metrics:
            comp.metrics = self.metrics(row["id"])
        return comp

    # ------------------------------------------------------------------ #
    # RF09 — Busca e filtragem
    # ------------------------------------------------------------------ #
    def search(self, filters: Optional[SearchFilters] = None,
               *, limit: int = 100, with_metrics: bool = True) -> List[Component]:
        """Busca/filtra componentes por múltiplos critérios (RF09)."""
        filters = filters or SearchFilters()
        where: List[str] = []
        params: List[Any] = []

        if not filters.include_rejected and filters.status != "rejected":
            where.append("status != 'rejected'")
        if filters.status:
            where.append("status = ?")
            params.append(filters.status)
        if filters.bloom_level:
            # normaliza nível de Bloom para comparar com o armazenado
            lvl = parse_bloom(filters.bloom_level)
            target = lvl.pt if lvl else filters.bloom_level
            where.append("lower(bloom_level) = lower(?)")
            params.append(target)
        if filters.mechanic_type:
            where.append("mechanic_type = ?")
            params.append(filters.mechanic_type)
        if filters.domain:
            where.append("lower(domain) LIKE lower(?)")
            params.append(f"%{filters.domain}%")
        if filters.context:
            where.append("context = ?")
            params.append(filters.context)
        if filters.age_range:
            where.append("age_range = ?")
            params.append(filters.age_range)
        if filters.modality:
            where.append("modality = ?")
            params.append(filters.modality)
        if filters.text:
            where.append("(lower(name) LIKE lower(?) OR lower(description) LIKE lower(?) "
                         "OR lower(dsl_signature) LIKE lower(?))")
            like = f"%{filters.text}%"
            params.extend([like, like, like])

        clause = (" WHERE " + " AND ".join(where)) if where else ""
        # Componentes canônicos primeiro (RF12 / priorização do agente de recuperação).
        sql = (f"SELECT * FROM components{clause} "
               f"ORDER BY (status = 'canonical') DESC, updated_at DESC LIMIT ?")
        params.append(limit)
        rows = self.db.query_all(sql, params)

        results = [self._row_to_component(r, with_metrics=with_metrics) for r in rows]
        if filters.min_rating is not None:
            results = [
                c for c in results
                if c.metrics.avg_rating is not None and c.metrics.avg_rating >= filters.min_rating
            ]
        return results

    def list_all(self, *, with_metrics: bool = False) -> List[Component]:
        return self.search(SearchFilters(include_rejected=True), with_metrics=with_metrics)

    # ------------------------------------------------------------------ #
    # RF12 / Jornada secundária — Curadoria
    # ------------------------------------------------------------------ #
    def curation_queue(self) -> List[Component]:
        """Componentes experimentais aguardando revisão do curador."""
        rows = self.db.query_all(
            "SELECT * FROM components WHERE status = 'experimental' ORDER BY created_at"
        )
        return [self._row_to_component(r) for r in rows]

    def approve(self, component_id: int, *, curator: Optional[str] = None,
                justification: str = "") -> None:
        """Promove um componente experimental a canônico (RF12)."""
        self._set_status(component_id, "canonical", "approve", curator, justification)

    def reject(self, component_id: int, *, curator: Optional[str] = None,
               justification: str = "") -> None:
        """Rejeita um componente (remove da fila com justificativa) (RF12)."""
        self._set_status(component_id, "rejected", "reject", curator, justification)

    def request_changes(self, component_id: int, *, curator: Optional[str] = None,
                        justification: str = "") -> None:
        """Solicita revisão ao contribuidor (mantém experimental)."""
        ts = now_iso()
        self.db.execute(
            """INSERT INTO curation_log (component_id, action, curator, justification, created_at)
               VALUES (?, 'request_changes', ?, ?, ?)""",
            (component_id, curator, justification, ts),
        )
        self.db.commit()

    def _set_status(self, component_id: int, status: str, action: str,
                    curator: Optional[str], justification: str) -> None:
        row = self.db.query_one("SELECT 1 FROM components WHERE id = ?", (component_id,))
        if row is None:
            raise KeyError(f"componente {component_id} não encontrado")
        ts = now_iso()
        self.db.execute(
            "UPDATE components SET status = ?, updated_at = ? WHERE id = ?",
            (status, ts, component_id),
        )
        self.db.execute(
            """INSERT INTO curation_log (component_id, action, curator, justification, created_at)
               VALUES (?,?,?,?,?)""",
            (component_id, action, curator, justification, ts),
        )
        self.db.commit()

    def curation_history(self, component_id: int) -> List[Dict[str, Any]]:
        rows = self.db.query_all(
            "SELECT * FROM curation_log WHERE component_id = ? ORDER BY created_at",
            (component_id,),
        )
        return [dict(r) for r in rows]
