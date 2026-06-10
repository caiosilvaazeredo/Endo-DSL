"""Módulo 3 — Pipeline Multi-Agente LLM (RF13–RF18).

Três agentes coordenados por um pipeline:

* :class:`~endo_dsl.agents.retrieval.RetrievalAgent`  — RF14 (recuperação);
* :class:`~endo_dsl.agents.generation.GenerationAgent` — RF15 (geração);
* :class:`~endo_dsl.agents.validation.ValidationAgent` — RF16 (validação).

O backend de linguagem é plugável (:mod:`endo_dsl.agents.llm`): usa a API da
Claude quando configurada, ou um compositor determinístico offline caso contrário,
de modo que o pipeline sempre é executável e testável.
"""

from endo_dsl.agents.context import DesignContext
from endo_dsl.agents.retrieval import RetrievalAgent, RetrievedComponent
from endo_dsl.agents.generation import GenerationAgent
from endo_dsl.agents.validation import ValidationAgent, ValidationReport
from endo_dsl.agents.pipeline import Pipeline, PipelineResult

__all__ = [
    "DesignContext",
    "RetrievalAgent",
    "RetrievedComponent",
    "GenerationAgent",
    "ValidationAgent",
    "ValidationReport",
    "Pipeline",
    "PipelineResult",
]
