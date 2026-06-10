"""Módulo 5 — Avaliação e Comparação (RF24–RF26)."""

from endo_dsl.evaluation.instrument import (
    INSTRUMENT_VERSION,
    DIMENSIONS,
    EvaluationDimension,
    blank_form,
    validate_scores,
    overall_score,
)
from endo_dsl.evaluation.store import EvaluationStore, EvaluationRecord
from endo_dsl.evaluation.reports import comparative_report, report_as_text

__all__ = [
    "INSTRUMENT_VERSION",
    "DIMENSIONS",
    "EvaluationDimension",
    "blank_form",
    "validate_scores",
    "overall_score",
    "EvaluationStore",
    "EvaluationRecord",
    "comparative_report",
    "report_as_text",
]
