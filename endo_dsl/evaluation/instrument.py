"""Instrumento estruturado de avaliação de qualidade pedagógica (RF24).

Define dimensões avaliáveis de forma idêntica para protótipos **gerados
automaticamente** e **desenvolvidos manualmente**, viabilizando a comparação
direta exigida por RF24/RF26 (Questão de Pesquisa Q4).

As dimensões dialogam com instrumentos consolidados de avaliação de jogos
educacionais (p.ex. MEEGA+), porém com foco no que a Endo-DSL se propõe a
sustentar: alinhamento pedagógico, coerência cognitiva e endogeneidade.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

INSTRUMENT_VERSION = "endo-eval-1.0"

LIKERT_MIN = 1
LIKERT_MAX = 5


@dataclass(frozen=True)
class EvaluationDimension:
    key: str
    label: str
    question: str
    weight: float = 1.0


# Dimensões do instrumento (escala Likert 1–5 em cada uma).
DIMENSIONS: List[EvaluationDimension] = [
    EvaluationDimension(
        "pedagogical_alignment", "Alinhamento pedagógico",
        "As mecânicas implementam de fato os objetivos de aprendizagem declarados?", 1.3),
    EvaluationDimension(
        "cognitive_coherence", "Coerência cognitiva (Bloom)",
        "O nível cognitivo exercitado corresponde ao nível de Bloom pretendido?", 1.2),
    EvaluationDimension(
        "endogeneity", "Endogeneidade",
        "O conteúdo está integrado à mecânica (aprender é jogar), e não justaposto?", 1.3),
    EvaluationDimension(
        "instructional_clarity", "Clareza instrucional",
        "As instruções e os desafios são claros e compreensíveis?", 1.0),
    EvaluationDimension(
        "audience_fit", "Adequação ao público",
        "O jogo é adequado à faixa etária e ao contexto do aprendiz?", 1.0),
    EvaluationDimension(
        "engagement_potential", "Potencial de engajamento",
        "O jogo tem potencial para manter o interesse do aprendiz?", 1.0),
    EvaluationDimension(
        "content_adaptability", "Adaptabilidade de conteúdo",
        "O conteúdo pode ser reparametrizado para outros domínios sem perder coerência?", 0.8),
]

_DIM_INDEX: Dict[str, EvaluationDimension] = {d.key: d for d in DIMENSIONS}


def blank_form() -> Dict[str, object]:
    """Formulário em branco do instrumento (para preenchimento por avaliador)."""
    return {
        "instrument_version": INSTRUMENT_VERSION,
        "scale": {"min": LIKERT_MIN, "max": LIKERT_MAX},
        "dimensions": [
            {"key": d.key, "label": d.label, "question": d.question,
             "weight": d.weight, "score": None}
            for d in DIMENSIONS
        ],
        "comments": "",
    }


def validate_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """Valida e normaliza um conjunto de pontuações por dimensão (RF25)."""
    clean: Dict[str, float] = {}
    for key, value in scores.items():
        if key not in _DIM_INDEX:
            raise ValueError(f"dimensão desconhecida: {key!r}")
        v = float(value)
        if not (LIKERT_MIN <= v <= LIKERT_MAX):
            raise ValueError(
                f"pontuação fora da escala [{LIKERT_MIN},{LIKERT_MAX}] em {key}: {v}")
        clean[key] = v
    return clean


def overall_score(scores: Dict[str, float]) -> float:
    """Média ponderada das dimensões pontuadas (0 se nenhuma)."""
    num = 0.0
    den = 0.0
    for key, value in scores.items():
        dim = _DIM_INDEX.get(key)
        if dim is None:
            continue
        num += dim.weight * float(value)
        den += dim.weight
    return round(num / den, 3) if den else 0.0


def dimension_keys() -> List[str]:
    return [d.key for d in DIMENSIONS]
