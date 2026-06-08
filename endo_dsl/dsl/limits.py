"""Limites formais da gramática — RF06.

Documenta, de forma programática e auditável, **quais construtos do Endo-GDC são
diretamente formalizáveis** na Endo-DSL e **quais dependem de interpretação
humana**, justificando a exclusão de elementos subjetivos (engajamento percebido,
experiência do jogador, tom estético).

Esta separação responde à Questão de Pesquisa Q1 (RF01, RF06) e ancora o "ponto
de controle humano" descrito na Fase 4 da jornada do usuário.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ConstructLimit:
    name: str
    status: str  # "formalizado" | "parcial" | "humano"
    rationale: str


# Construtos diretamente formalizáveis na gramática.
FORMALIZED: List[ConstructLimit] = [
    ConstructLimit(
        "Mecânicas de jogo (tipo)",
        "formalizado",
        "O tipo de mecânica é um enum fechado e verificável (ver MECHANIC_TYPES); "
        "cada tipo tem semântica operacional e mapeia para um template do compilador.",
    ),
    ConstructLimit(
        "Objetivos pedagógicos",
        "formalizado",
        "Declarados como entidades nomeadas com nível de Bloom; verificáveis e "
        "rastreáveis até as mecânicas que os endereçam (RF23).",
    ),
    ConstructLimit(
        "Níveis cognitivos (Taxonomia de Bloom)",
        "formalizado",
        "Os seis níveis são construtos de primeira classe (RF02), com ordem total "
        "e regras de afinidade por tipo de mecânica (RF04).",
    ),
    ConstructLimit(
        "Loops de jogabilidade",
        "formalizado",
        "Representados como grafo de transições entre estados; verificável quanto a "
        "fechamento de ciclo e estados alcançáveis.",
    ),
    ConstructLimit(
        "Ramificações narrativas (estrutura)",
        "formalizado",
        "A topologia de ramos e escolhas é um grafo dirigido verificável; alvos de "
        "escolha são checados quanto à existência.",
    ),
    ConstructLimit(
        "Parâmetros de conteúdo/dificuldade/domínio",
        "formalizado",
        "Pares chave-valor tipados; permitem parametrização de conteúdo independente "
        "da estrutura (RF22).",
    ),
]

# Construtos parcialmente formalizáveis (estrutura sim, qualidade não).
PARTIAL: List[ConstructLimit] = [
    ConstructLimit(
        "Coerência pedagógica mecânica-objetivo",
        "parcial",
        "A gramática verifica alinhamento de nível de Bloom (RF04), mas a adequação "
        "didática fina (a mecânica realmente ensina o conceito?) requer julgamento.",
    ),
    ConstructLimit(
        "Conteúdo textual narrativo",
        "parcial",
        "A presença e a topologia do texto são formalizadas; a *qualidade* literária "
        "e a clareza do enunciado não são verificáveis pela gramática.",
    ),
    ConstructLimit(
        "Curva de dificuldade",
        "parcial",
        "O parâmetro 'difficulty' é declarável e ordenável, mas o balanceamento "
        "percebido depende de teste com usuários reais.",
    ),
]

# Construtos deliberadamente NÃO formalizados (dependem de interpretação humana).
HUMAN: List[ConstructLimit] = [
    ConstructLimit(
        "Engajamento percebido",
        "humano",
        "É um constructo psicológico subjetivo, medido a posteriori com instrumentos "
        "(RF24), não declarável a priori sem reduzir indevidamente sua complexidade.",
    ),
    ConstructLimit(
        "Experiência do jogador (UX/fun)",
        "humano",
        "Emerge da interação completa; formalizá-la incorreria em falsa precisão. "
        "Fica a cargo do designer na Fase 4 da jornada.",
    ),
    ConstructLimit(
        "Tom narrativo e estética",
        "humano",
        "Escolhas de voz, humor e estilo visual são expressivas e contextuais; a DSL "
        "as deixa ao controle humano explícito (ponto de controle da Fase 4).",
    ),
    ConstructLimit(
        "Adequação cultural do conteúdo",
        "humano",
        "Sensibilidade a contexto cultural/regional exige curadoria humana; a gramática "
        "não a captura.",
    ),
]


def all_limits() -> List[ConstructLimit]:
    return FORMALIZED + PARTIAL + HUMAN


def as_markdown() -> str:
    """Renderiza a documentação dos limites como Markdown (para relatórios/UI)."""
    lines = [
        "# Limites Formais da Gramática Endo-DSL (RF06)",
        "",
        "Resposta à Questão de Pesquisa **Q1**: *quais construtos do Endo-GDC são",
        "formalizáveis numa gramática computacional e quais dependem de interpretação",
        "humana?*",
        "",
    ]
    for title, group in (
        ("Formalizados (verificáveis pela gramática)", FORMALIZED),
        ("Parcialmente formalizados (estrutura sim, qualidade não)", PARTIAL),
        ("Não formalizados (controle humano deliberado)", HUMAN),
    ):
        lines.append(f"## {title}")
        lines.append("")
        for c in group:
            lines.append(f"- **{c.name}** — {c.rationale}")
        lines.append("")
    return "\n".join(lines)


def as_dict() -> dict:
    return {
        "formalized": [c.__dict__ for c in FORMALIZED],
        "partial": [c.__dict__ for c in PARTIAL],
        "human": [c.__dict__ for c in HUMAN],
    }
