"""Agente de Recuperação (RF14).

Consulta a biblioteca de componentes e seleciona os mais relevantes para o
contexto de entrada, combinando **similaridade semântica** (lexical, offline) com
**filtros estruturados** (nível de Bloom, domínio, afinidade de mecânica). Componentes
canônicos são priorizados (RF12), em linha com a jornada secundária do curador.

A similaridade é lexical (cosseno sobre saco-de-palavras com remoção de stopwords
em português) — um proxy determinístico que dispensa serviços externos de
embeddings, mas é facilmente substituível por um modelo vetorial.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from typing import List, Optional

from endo_dsl.agents.context import DesignContext
from endo_dsl.dsl.bloom import parse_bloom
from endo_dsl.dsl.semantic import mechanic_bloom_affinity
from endo_dsl.library.models import Component, SearchFilters
from endo_dsl.library.repository import ComponentRepository

_STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "ou", "que", "com",
    "para", "por", "em", "no", "na", "nos", "nas", "um", "uma", "uns", "umas", "ao",
    "à", "se", "sua", "seu", "ser", "como", "the", "of", "to", "and", "is", "in",
    "será", "capaz", "aluno", "aprendiz", "sobre", "entre", "mais", "menos",
}


def _normalize(text: str) -> List[str]:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return [t for t in tokens if t not in _STOPWORDS and len(t) > 1]


def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    num = sum(a[t] * b[t] for t in common)
    da = math.sqrt(sum(v * v for v in a.values()))
    db = math.sqrt(sum(v * v for v in b.values()))
    return num / (da * db) if da and db else 0.0


@dataclass
class RetrievedComponent:
    """Componente recuperado com sua pontuação e justificativa de relevância."""

    component: Component
    score: float
    reasons: List[str]

    def to_dict(self) -> dict:
        d = self.component.to_dict()
        d["relevance_score"] = round(self.score, 4)
        d["relevance_reasons"] = self.reasons
        return d


class RetrievalAgent:
    """Seleciona componentes relevantes da biblioteca para um contexto (RF14)."""

    def __init__(self, repo: ComponentRepository):
        self.repo = repo

    def retrieve(self, context: DesignContext, *, top_k: int = 5,
                 candidate_pool: int = 200) -> List[RetrievedComponent]:
        # Pré-filtro estruturado amplo (não exige match exato de Bloom para não
        # excluir componentes adjacentes úteis).
        candidates = self.repo.search(
            SearchFilters(domain=None, include_rejected=False),
            limit=candidate_pool,
        )
        query_tokens = Counter(_normalize(context.query_text()))
        scored: List[RetrievedComponent] = []
        for comp in candidates:
            score, reasons = self._score(comp, context, query_tokens)
            if score > 0:
                scored.append(RetrievedComponent(comp, score, reasons))
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]

    def _score(self, comp: Component, ctx: DesignContext, query_tokens: Counter):
        reasons: List[str] = []
        comp_text = " ".join([comp.name, comp.description, comp.mechanic_type,
                              comp.domain or "", comp.dsl_signature])
        sem = _cosine(query_tokens, Counter(_normalize(comp_text)))
        score = 0.45 * sem
        if sem > 0.05:
            reasons.append(f"similaridade semântica {sem:.2f}")

        # Filtro estruturado: nível de Bloom (RF14).
        comp_bloom = parse_bloom(comp.bloom_level)
        if comp_bloom is not None:
            dist = abs(int(comp_bloom) - int(ctx.bloom_target))
            if dist == 0:
                score += 0.30
                reasons.append(f"nível de Bloom exato ({comp_bloom.pt})")
            elif dist == 1:
                score += 0.15
                reasons.append(f"nível de Bloom adjacente ({comp_bloom.pt})")
            else:
                score += max(0.0, 0.10 - 0.03 * dist)

        # Domínio (RF14).
        if comp.domain and ctx.domain:
            cd = _normalize(comp.domain)
            xd = _normalize(ctx.domain)
            if set(cd) & set(xd):
                score += 0.15
                reasons.append(f"domínio compatível ({comp.domain})")

        # Afinidade do tipo de mecânica com o Bloom alvo.
        affinity = mechanic_bloom_affinity(comp.mechanic_type)
        if affinity and ctx.bloom_target in affinity:
            score += 0.10
            reasons.append(f"mecânica '{comp.mechanic_type}' sustenta {ctx.bloom_target.pt}")

        # Prioriza componentes canônicos (RF12).
        if comp.is_canonical:
            score += 0.08
            reasons.append("componente canônico")

        # Qualidade (avaliações dos usuários).
        if comp.metrics.avg_rating:
            score += 0.02 * (comp.metrics.avg_rating / 5.0)

        return score, reasons
