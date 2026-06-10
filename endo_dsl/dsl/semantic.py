"""Validação semântica da Endo-DSL — RF04.

Diferente da validação sintática (que verifica a *forma*), a validação semântica
verifica a *coerência* da especificação. O cheque central, exigido por RF04, é a
compatibilidade entre o **tipo de mecânica** e o **nível cognitivo de Bloom**
declarado: por exemplo, uma mecânica de memorização (`recall`) rotulada como
nível "Criar" é uma inconsistência.

Cada tipo de mecânica possui uma *afinidade* — o conjunto de níveis de Bloom que
ela naturalmente exercita. A distância entre o nível declarado e a afinidade
determina a severidade do problema (``error`` x ``warning``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from endo_dsl.dsl.ast import GameSpec, Mechanic
from endo_dsl.dsl.bloom import Bloom


@dataclass
class MechanicType:
    """Catálogo de uma mecânica endógena e sua afinidade cognitiva."""

    key: str
    label: str
    bloom_affinity: Set[Bloom]
    description: str
    endogenous: bool = True  # a maioria é endógena por construção


def _aff(*levels: Bloom) -> Set[Bloom]:
    return set(levels)


# Catálogo de tipos de mecânica reconhecidos pela gramática, com a faixa de
# níveis de Bloom que cada um naturalmente exercita. Esta tabela é o coração da
# checagem de coerência semântica (RF04) e também documenta os limites do que a
# gramática formaliza (RF06).
MECHANIC_TYPES: Dict[str, MechanicType] = {
    "recall": MechanicType(
        "recall", "Recordação / memorização",
        _aff(Bloom.LEMBRAR), "Recuperar fatos, termos ou definições da memória."),
    "flashcard": MechanicType(
        "flashcard", "Cartões de memória",
        _aff(Bloom.LEMBRAR, Bloom.COMPREENDER), "Reconhecer e recordar pares estímulo-resposta."),
    "matching": MechanicType(
        "matching", "Associação / pareamento",
        _aff(Bloom.LEMBRAR, Bloom.COMPREENDER), "Associar elementos correspondentes entre si."),
    "labeling": MechanicType(
        "labeling", "Rotulagem",
        _aff(Bloom.LEMBRAR, Bloom.COMPREENDER), "Identificar e nomear partes de um todo."),
    "quiz": MechanicType(
        "quiz", "Questionário",
        _aff(Bloom.LEMBRAR, Bloom.COMPREENDER, Bloom.APLICAR),
        "Responder perguntas objetivas sobre o conteúdo."),
    "classification": MechanicType(
        "classification", "Classificação / categorização",
        _aff(Bloom.COMPREENDER, Bloom.ANALISAR),
        "Agrupar elementos segundo critérios ou categorias."),
    "sequencing": MechanicType(
        "sequencing", "Ordenação / sequenciamento",
        _aff(Bloom.COMPREENDER, Bloom.APLICAR, Bloom.ANALISAR),
        "Organizar elementos em ordem lógica, temporal ou causal."),
    "comparison": MechanicType(
        "comparison", "Comparação",
        _aff(Bloom.COMPREENDER, Bloom.ANALISAR),
        "Identificar semelhanças e diferenças entre elementos."),
    "simulation": MechanicType(
        "simulation", "Simulação",
        _aff(Bloom.APLICAR, Bloom.ANALISAR),
        "Operar um modelo do fenômeno e observar consequências."),
    "puzzle": MechanicType(
        "puzzle", "Quebra-cabeça / resolução de problemas",
        _aff(Bloom.APLICAR, Bloom.ANALISAR),
        "Aplicar regras para resolver um problema estruturado."),
    "construction": MechanicType(
        "construction", "Construção",
        _aff(Bloom.APLICAR, Bloom.CRIAR),
        "Montar um artefato a partir de componentes seguindo regras."),
    "strategy": MechanicType(
        "strategy", "Estratégia / gestão de recursos",
        _aff(Bloom.APLICAR, Bloom.ANALISAR, Bloom.AVALIAR),
        "Planejar e otimizar decisões sob restrições."),
    "role_play": MechanicType(
        "role_play", "Interpretação de papéis",
        _aff(Bloom.APLICAR, Bloom.ANALISAR, Bloom.AVALIAR),
        "Assumir um papel e agir conforme seu contexto e valores."),
    "decision": MechanicType(
        "decision", "Tomada de decisão",
        _aff(Bloom.ANALISAR, Bloom.AVALIAR),
        "Escolher entre alternativas ponderando critérios e consequências."),
    "critique": MechanicType(
        "critique", "Crítica / julgamento",
        _aff(Bloom.AVALIAR,),
        "Julgar a qualidade ou validade de algo com base em critérios."),
    "debate": MechanicType(
        "debate", "Debate / argumentação",
        _aff(Bloom.ANALISAR, Bloom.AVALIAR),
        "Defender posições com argumentos e refutar contra-argumentos."),
    "design": MechanicType(
        "design", "Projeto / criação",
        _aff(Bloom.CRIAR,),
        "Produzir um artefato original que atende a requisitos."),
    "storytelling": MechanicType(
        "storytelling", "Construção narrativa",
        _aff(Bloom.AVALIAR, Bloom.CRIAR),
        "Compor uma narrativa original a partir de elementos dados."),
    "exploration": MechanicType(
        "exploration", "Exploração",
        _aff(Bloom.COMPREENDER, Bloom.APLICAR),
        "Investigar um ambiente para descobrir relações e regras."),
}


def mechanic_bloom_affinity(mech_type: str) -> Optional[Set[Bloom]]:
    """Retorna o conjunto de níveis de Bloom afins a um tipo de mecânica, ou None."""
    entry = MECHANIC_TYPES.get(mech_type)
    return set(entry.bloom_affinity) if entry else None


@dataclass
class SemanticIssue:
    """Um problema de coerência encontrado pela validação semântica."""

    severity: str  # "error" | "warning"
    code: str
    message: str
    line: int = 0
    col: int = 0
    suggestion: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "col": self.col,
            "suggestion": self.suggestion,
            "kind": "semantic",
        }


def _bloom_distance(level: Bloom, affinity: Set[Bloom]) -> int:
    """Menor distância (em níveis) entre ``level`` e o conjunto de afinidade."""
    return min(abs(int(level) - int(a)) for a in affinity)


def validate_semantics(spec: GameSpec) -> List[SemanticIssue]:
    """Executa todas as checagens semânticas e retorna a lista de problemas.

    Uma especificação é semanticamente válida se nenhum problema com severidade
    ``error`` for retornado (warnings não invalidam, mas devem ser exibidos).
    """
    issues: List[SemanticIssue] = []

    issues.extend(_check_unique_names(spec))
    issues.extend(_check_mechanic_types(spec))
    issues.extend(_check_mechanic_bloom_coherence(spec))
    issues.extend(_check_objective_references(spec))
    issues.extend(_check_pedagogical_alignment(spec))
    issues.extend(_check_loops(spec))
    issues.extend(_check_narratives(spec))
    issues.extend(_check_coverage(spec))

    # Ordena por linha para apresentação estável.
    issues.sort(key=lambda i: (i.line, 0 if i.severity == "error" else 1))
    return issues


def _check_unique_names(spec: GameSpec) -> List[SemanticIssue]:
    issues: List[SemanticIssue] = []
    seen: Dict[str, str] = {}
    for kind, items in (
        ("objetivo", spec.objectives),
        ("mecânica", spec.mechanics),
        ("loop", spec.loops),
        ("narrativa", spec.narratives),
    ):
        for item in items:
            if item.name in seen:
                issues.append(SemanticIssue(
                    "error", "E_DUP_NAME",
                    f"nome '{item.name}' já usado por outro {seen[item.name]}; "
                    f"identificadores devem ser únicos.",
                    item.line, item.col,
                    suggestion="renomeie um dos elementos.",
                ))
            else:
                seen[item.name] = kind
    return issues


def _check_mechanic_types(spec: GameSpec) -> List[SemanticIssue]:
    issues: List[SemanticIssue] = []
    import difflib
    for m in spec.mechanics:
        if not m.type:
            issues.append(SemanticIssue(
                "error", "E_NO_TYPE",
                f"a mecânica '{m.name}' não declara um 'type'.",
                m.line, m.col,
                suggestion=f"tipos válidos: {', '.join(sorted(MECHANIC_TYPES))}",
            ))
        elif m.type not in MECHANIC_TYPES:
            match = difflib.get_close_matches(m.type, list(MECHANIC_TYPES), n=1, cutoff=0.5)
            issues.append(SemanticIssue(
                "error", "E_BAD_TYPE",
                f"tipo de mecânica desconhecido: '{m.type}' (mecânica '{m.name}').",
                m.line, m.col,
                suggestion=(f"você quis dizer '{match[0]}'?" if match
                            else f"tipos válidos: {', '.join(sorted(MECHANIC_TYPES))}"),
            ))
    return issues


def _check_mechanic_bloom_coherence(spec: GameSpec) -> List[SemanticIssue]:
    """RF04 — núcleo: coerência entre tipo de mecânica e nível de Bloom declarado."""
    issues: List[SemanticIssue] = []
    for m in spec.mechanics:
        if m.bloom is None:
            issues.append(SemanticIssue(
                "error", "E_NO_BLOOM",
                f"a mecânica '{m.name}' não declara um nível de Bloom.",
                m.line, m.col,
                suggestion="adicione, p.ex.: bloom: Analisar",
            ))
            continue
        affinity = mechanic_bloom_affinity(m.type)
        if affinity is None:
            continue  # tipo inválido já reportado em _check_mechanic_types
        if m.bloom in affinity:
            continue
        distance = _bloom_distance(m.bloom, affinity)
        affinity_names = ", ".join(sorted(b.pt for b in affinity))
        if distance >= 2:
            issues.append(SemanticIssue(
                "error", "E_BLOOM_MISMATCH",
                f"incoerência cognitiva: a mecânica '{m.name}' é do tipo "
                f"'{m.type}' ({MECHANIC_TYPES[m.type].label}), que exercita "
                f"tipicamente [{affinity_names}], mas foi rotulada como "
                f"'{m.bloom.pt}'.",
                m.line, m.col,
                suggestion=f"use um nível em [{affinity_names}], ou troque o tipo de mecânica "
                           f"por um que sustente '{m.bloom.pt}'.",
            ))
        else:
            issues.append(SemanticIssue(
                "warning", "W_BLOOM_STRETCH",
                f"a mecânica '{m.name}' ('{m.type}') normalmente exercita "
                f"[{affinity_names}]; o nível '{m.bloom.pt}' é adjacente e pode "
                f"exigir reforço de design para se sustentar.",
                m.line, m.col,
                suggestion=f"considere [{affinity_names}] ou justifique o desenho da mecânica.",
            ))
    return issues


def _check_objective_references(spec: GameSpec) -> List[SemanticIssue]:
    issues: List[SemanticIssue] = []
    import difflib
    obj_names = [o.name for o in spec.objectives]
    for m in spec.mechanics:
        for target in m.addresses:
            if target not in obj_names:
                match = difflib.get_close_matches(target, obj_names, n=1, cutoff=0.5)
                issues.append(SemanticIssue(
                    "error", "E_BAD_REF",
                    f"a mecânica '{m.name}' referencia o objetivo inexistente "
                    f"'{target}'.",
                    m.line, m.col,
                    suggestion=(f"você quis dizer '{match[0]}'?" if match
                                else f"objetivos declarados: {', '.join(obj_names) or '(nenhum)'}"),
                ))
    return issues


def _check_pedagogical_alignment(spec: GameSpec) -> List[SemanticIssue]:
    """Coerência pedagógica: a mecânica deve sustentar o nível do objetivo que endereça."""
    issues: List[SemanticIssue] = []
    for m in spec.mechanics:
        if m.bloom is None:
            continue
        for target in m.addresses:
            obj = spec.objective(target)
            if obj is None or obj.bloom is None:
                continue
            # Se o objetivo exige um nível bem acima do que a mecânica oferece,
            # há desalinhamento (a mecânica não leva o aluno ao objetivo).
            if int(m.bloom) <= int(obj.bloom) - 2:
                issues.append(SemanticIssue(
                    "warning", "W_ALIGN",
                    f"a mecânica '{m.name}' opera em '{m.bloom.pt}', mas o objetivo "
                    f"'{obj.name}' exige '{obj.bloom.pt}'; a mecânica pode não levar "
                    f"o aluno ao nível pretendido.",
                    m.line, m.col,
                    suggestion="eleve o nível da mecânica ou adicione mecânicas intermediárias.",
                ))
    return issues


def _check_loops(spec: GameSpec) -> List[SemanticIssue]:
    issues: List[SemanticIssue] = []
    for loop in spec.loops:
        if not loop.transitions:
            issues.append(SemanticIssue(
                "warning", "W_EMPTY_LOOP",
                f"o loop '{loop.name}' não declara transições em 'steps'.",
                loop.line, loop.col,
                suggestion="adicione transições, p.ex.: apresenta -> desafia",
            ))
            continue
        states: Set[str] = set()
        for t in loop.transitions:
            states.add(t.src)
            states.add(t.dst)
        # Um loop de jogabilidade deve, idealmente, fechar um ciclo.
        dsts = {t.dst for t in loop.transitions}
        srcs = {t.src for t in loop.transitions}
        if not (dsts & srcs):
            issues.append(SemanticIssue(
                "warning", "W_OPEN_LOOP",
                f"o loop '{loop.name}' parece linear (não retorna a nenhum estado anterior).",
                loop.line, loop.col,
                suggestion="loops de jogabilidade normalmente realimentam um estado anterior.",
            ))
    return issues


def _check_narratives(spec: GameSpec) -> List[SemanticIssue]:
    issues: List[SemanticIssue] = []
    for nar in spec.narratives:
        branch_names = {b.name for b in nar.branches}
        for b in nar.branches:
            for c in b.choices:
                if c.target not in branch_names:
                    issues.append(SemanticIssue(
                        "error", "E_BAD_BRANCH",
                        f"na narrativa '{nar.name}', a escolha \"{c.text}\" aponta para "
                        f"o ramo inexistente '{c.target}'.",
                        c.line, c.col,
                        suggestion=f"ramos existentes: {', '.join(sorted(branch_names))}",
                    ))
    return issues


def _check_coverage(spec: GameSpec) -> List[SemanticIssue]:
    """Avisa sobre objetivos não endereçados por nenhuma mecânica (cobertura)."""
    issues: List[SemanticIssue] = []
    addressed: Set[str] = set()
    for m in spec.mechanics:
        addressed.update(m.addresses)
    for o in spec.objectives:
        if o.name not in addressed:
            issues.append(SemanticIssue(
                "warning", "W_UNADDRESSED",
                f"o objetivo '{o.name}' não é endereçado por nenhuma mecânica.",
                o.line, o.col,
                suggestion="adicione 'addresses: " + o.name + "' a alguma mecânica.",
            ))
    if not spec.mechanics:
        issues.append(SemanticIssue(
            "error", "E_NO_MECHANIC",
            "a especificação não declara nenhuma mecânica de jogo.",
            spec.line, spec.col,
            suggestion="todo jogo endógeno precisa de ao menos uma mecânica.",
        ))
    return issues
