"""Entrada estruturada do pipeline (RF13).

Representa o contexto educacional informado pelo Designer/Educador na Fase 1 da
jornada: objetivo de aprendizagem, área de conhecimento, perfil do aprendiz,
restrições de contexto e nível cognitivo desejado da Taxonomia de Bloom.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from endo_dsl.dsl.bloom import Bloom, parse_bloom


@dataclass
class DesignContext:
    """Contexto de design educacional estruturado (RF13)."""

    learning_objective: str
    domain: str
    bloom_target: Bloom
    # Perfil do aprendiz (RF13)
    age_range: Optional[str] = None
    education_level: Optional[str] = None
    learner_context: Optional[str] = None  # formal | informal | ...
    # Restrições de contexto (RF13)
    duration_minutes: Optional[int] = None
    platform: str = "web"
    no_extensive_reading: bool = False
    topic: Optional[str] = None  # tema específico (ex.: "frações")
    title: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DesignContext":
        bloom = data.get("bloom_target")
        level = parse_bloom(bloom) if isinstance(bloom, str) else bloom
        if level is None:
            raise ValueError(f"bloom_target inválido: {bloom!r}")
        return cls(
            learning_objective=data.get("learning_objective", ""),
            domain=data.get("domain", ""),
            bloom_target=level,
            age_range=data.get("age_range"),
            education_level=data.get("education_level"),
            learner_context=data.get("learner_context") or data.get("context"),
            duration_minutes=data.get("duration_minutes") or data.get("duration"),
            platform=data.get("platform", "web"),
            no_extensive_reading=bool(data.get("no_extensive_reading", False)),
            topic=data.get("topic"),
            title=data.get("title"),
            extra={k: v for k, v in data.items() if k not in _KNOWN_KEYS},
        )

    def query_text(self) -> str:
        """Texto consolidado usado pelo agente de recuperação (similaridade semântica)."""
        parts = [self.learning_objective, self.domain or "", self.topic or "",
                 self.learner_context or "", self.education_level or ""]
        return " ".join(p for p in parts if p)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "learning_objective": self.learning_objective,
            "domain": self.domain,
            "bloom_target": self.bloom_target.pt,
            "age_range": self.age_range,
            "education_level": self.education_level,
            "learner_context": self.learner_context,
            "duration_minutes": self.duration_minutes,
            "platform": self.platform,
            "no_extensive_reading": self.no_extensive_reading,
            "topic": self.topic,
            "title": self.title,
            "extra": self.extra,
        }


_KNOWN_KEYS = {
    "learning_objective", "domain", "bloom_target", "age_range", "education_level",
    "learner_context", "context", "duration_minutes", "duration", "platform",
    "no_extensive_reading", "topic", "title",
}
