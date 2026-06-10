"""Modelos de dados da biblioteca de componentes."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ComponentMetrics:
    """Métricas de uso de um componente (RF11)."""

    instantiations: int = 0          # frequência de instanciação
    avg_rating: Optional[float] = None  # média das avaliações de usuários
    rating_count: int = 0
    compile_success_rate: Optional[float] = None  # taxa de sucesso na compilação
    compile_attempts: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instantiations": self.instantiations,
            "avg_rating": round(self.avg_rating, 2) if self.avg_rating is not None else None,
            "rating_count": self.rating_count,
            "compile_success_rate": (
                round(self.compile_success_rate, 3)
                if self.compile_success_rate is not None else None
            ),
            "compile_attempts": self.compile_attempts,
        }


@dataclass
class Component:
    """Um componente DSL reutilizável (RF07) com classificação e métricas."""

    id: int
    key: str
    name: str
    current_version: int
    dsl_signature: str
    bloom_level: str
    mechanic_type: str
    description: str
    params: Dict[str, Any] = field(default_factory=dict)
    domain: Optional[str] = None
    context: Optional[str] = None
    age_range: Optional[str] = None
    modality: Optional[str] = None
    status: str = "experimental"          # 'canonical' | 'experimental' | 'rejected' (RF12)
    author: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    metrics: ComponentMetrics = field(default_factory=ComponentMetrics)
    # Enriquecimento opcional (RF08)
    case_studies: List[Any] = field(default_factory=list)
    expert_evaluations: List[Any] = field(default_factory=list)
    references: List[Any] = field(default_factory=list)

    @property
    def is_canonical(self) -> bool:
        return self.status == "canonical"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "current_version": self.current_version,
            "dsl_signature": self.dsl_signature,
            "bloom_level": self.bloom_level,
            "mechanic_type": self.mechanic_type,
            "description": self.description,
            "params": self.params,
            "domain": self.domain,
            "context": self.context,
            "age_range": self.age_range,
            "modality": self.modality,
            "status": self.status,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metrics": self.metrics.to_dict(),
            "case_studies": self.case_studies,
            "expert_evaluations": self.expert_evaluations,
            "references": self.references,
        }


@dataclass
class SearchFilters:
    """Critérios de busca/filtragem de componentes (RF09)."""

    text: Optional[str] = None            # busca livre em nome/descrição/assinatura
    bloom_level: Optional[str] = None
    mechanic_type: Optional[str] = None
    domain: Optional[str] = None
    context: Optional[str] = None         # formal | informal
    age_range: Optional[str] = None
    modality: Optional[str] = None
    min_rating: Optional[float] = None    # avaliação mínima (RF09)
    status: Optional[str] = None          # canonical | experimental
    include_rejected: bool = False
