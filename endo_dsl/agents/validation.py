"""Agente de Validação (RF16).

Verifica a especificação gerada ANTES de entregá-la ao usuário, conferindo quatro
dimensões:

1. **validade sintática** — a DSL é analisável (RF03);
2. **validade semântica** — sem incoerências mecânica/Bloom (RF04);
3. **coerência pedagógica** — mecânicas endereçam os objetivos e alcançam o nível;
4. **consistência com os parâmetros de entrada** — domínio, Bloom e plataforma
   conferem com o contexto informado (RF13).
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from endo_dsl.agents.context import DesignContext
from endo_dsl.dsl.ast import GameSpec
from endo_dsl.dsl.parser import ParseError, parse
from endo_dsl.dsl.semantic import validate_semantics


@dataclass
class ValidationReport:
    """Relatório das quatro checagens do agente de validação (RF16)."""

    syntactic_ok: bool = False
    semantic_ok: bool = False
    pedagogical_ok: bool = False
    params_ok: bool = False
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    spec: Optional[GameSpec] = None

    @property
    def valid(self) -> bool:
        return all([self.syntactic_ok, self.semantic_ok,
                    self.pedagogical_ok, self.params_ok])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.valid,
            "syntactic_ok": self.syntactic_ok,
            "semantic_ok": self.semantic_ok,
            "pedagogical_ok": self.pedagogical_ok,
            "params_ok": self.params_ok,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def summary(self) -> str:
        flag = lambda b: "✓" if b else "✗"  # noqa: E731
        return (f"sintática {flag(self.syntactic_ok)} · semântica {flag(self.semantic_ok)} · "
                f"pedagógica {flag(self.pedagogical_ok)} · parâmetros {flag(self.params_ok)}")


def _norm(text: str) -> str:
    return unicodedata.normalize("NFKD", (text or "").lower()).encode("ascii", "ignore").decode()


class ValidationAgent:
    """Valida especificações DSL geradas (RF16)."""

    def validate(self, dsl_source: str,
                 context: Optional[DesignContext] = None) -> ValidationReport:
        report = ValidationReport()

        # 1. Sintaxe (RF03)
        try:
            spec = parse(dsl_source)
            report.spec = spec
            report.syntactic_ok = True
        except ParseError as exc:
            report.errors.append(exc.to_dict())
            return report  # sem AST não há como prosseguir

        # 2. Semântica (RF04)
        issues = validate_semantics(spec)
        sem_errors = [i.to_dict() for i in issues if i.severity == "error"]
        report.warnings.extend(i.to_dict() for i in issues if i.severity == "warning")
        report.errors.extend(sem_errors)
        report.semantic_ok = not sem_errors

        # 3. Coerência pedagógica
        report.pedagogical_ok = self._check_pedagogical(spec, context, report)

        # 4. Consistência com parâmetros de entrada (RF13)
        report.params_ok = self._check_params(spec, context, report)

        return report

    def _check_pedagogical(self, spec: GameSpec, ctx: Optional[DesignContext],
                           report: ValidationReport) -> bool:
        ok = True
        # Todo objetivo deve ser endereçado por ao menos uma mecânica.
        addressed = {a for m in spec.mechanics for a in m.addresses}
        for o in spec.objectives:
            if o.name not in addressed:
                report.errors.append({
                    "kind": "pedagogical", "code": "P_UNADDRESSED",
                    "message": f"objetivo '{o.name}' não é endereçado por nenhuma mecânica.",
                    "suggestion": "vincule uma mecânica via 'addresses'.",
                })
                ok = False
        if not spec.objectives:
            report.errors.append({
                "kind": "pedagogical", "code": "P_NO_OBJECTIVE",
                "message": "a especificação não declara objetivos pedagógicos.",
            })
            ok = False
        # Deve haver mecânica alcançando o nível de Bloom alvo (se informado).
        if ctx is not None:
            reaches = any(m.bloom is not None and int(m.bloom) >= int(ctx.bloom_target)
                          for m in spec.mechanics)
            if not reaches and spec.mechanics:
                report.warnings.append({
                    "kind": "pedagogical", "code": "P_BELOW_TARGET",
                    "message": f"nenhuma mecânica alcança o nível alvo "
                               f"'{ctx.bloom_target.pt}'.",
                    "suggestion": "adicione/eleve uma mecânica ao nível pretendido.",
                })
        return ok

    def _check_params(self, spec: GameSpec, ctx: Optional[DesignContext],
                      report: ValidationReport) -> bool:
        if ctx is None:
            return True
        ok = True
        meta = spec.metadata
        # Domínio
        spec_domain = _norm(str(meta.get("domain", "")))
        ctx_domain = _norm(ctx.domain)
        if ctx_domain and spec_domain and not (
            ctx_domain in spec_domain or spec_domain in ctx_domain
            or set(spec_domain.split()) & set(ctx_domain.split())
        ):
            report.warnings.append({
                "kind": "params", "code": "C_DOMAIN",
                "message": f"o domínio gerado ('{meta.get('domain')}') difere do "
                           f"contexto ('{ctx.domain}').",
            })
        # Nível de Bloom alvo presente
        if ctx.bloom_target not in spec.bloom_levels:
            report.errors.append({
                "kind": "params", "code": "C_BLOOM",
                "message": f"o nível de Bloom alvo '{ctx.bloom_target.pt}' não aparece "
                           f"em nenhum objetivo ou mecânica.",
                "suggestion": f"inclua um elemento no nível '{ctx.bloom_target.pt}'.",
            })
            ok = False
        # Plataforma
        spec_platform = _norm(str(meta.get("platform", "")))
        if spec_platform and _norm(ctx.platform) and spec_platform != _norm(ctx.platform):
            report.warnings.append({
                "kind": "params", "code": "C_PLATFORM",
                "message": f"plataforma gerada ('{meta.get('platform')}') difere da "
                           f"solicitada ('{ctx.platform}').",
            })
        return ok
