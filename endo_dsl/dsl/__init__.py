"""Módulo 1 — Motor da DSL: gramática formal, parser e validadores.

Cobre RF01–RF06.
"""

from endo_dsl.dsl.bloom import Bloom, BLOOM_ORDER
from endo_dsl.dsl.ast import (
    GameSpec,
    Metadata,
    Objective,
    Mechanic,
    GameplayLoop,
    Transition,
    Narrative,
    Branch,
    Choice,
    Params,
)
from endo_dsl.dsl.parser import parse, ParseError
from endo_dsl.dsl.semantic import (
    validate_semantics,
    SemanticIssue,
    MECHANIC_TYPES,
    mechanic_bloom_affinity,
)

__all__ = [
    "Bloom",
    "BLOOM_ORDER",
    "GameSpec",
    "Metadata",
    "Objective",
    "Mechanic",
    "GameplayLoop",
    "Transition",
    "Narrative",
    "Branch",
    "Choice",
    "Params",
    "parse",
    "ParseError",
    "validate_semantics",
    "SemanticIssue",
    "MECHANIC_TYPES",
    "mechanic_bloom_affinity",
]
