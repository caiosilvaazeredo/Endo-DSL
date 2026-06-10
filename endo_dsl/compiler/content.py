"""Construção do *content pack* dos protótipos (RF21, RF22).

Mapeia cada mecânica da AST para uma **interação** jogável e provê o **conteúdo**
(itens, pares, categorias) que a alimenta. A separação estrutura/conteúdo é o que
permite reparametrizar o domínio de um protótipo sem recompilar (RF22): basta
trocar o banco de conteúdo associado.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from endo_dsl.dsl.ast import GameSpec, Mechanic
from endo_dsl.dsl.bloom import Bloom
from endo_dsl.dsl.semantic import MECHANIC_TYPES

# Mapa tipo de mecânica -> interação jogável da engine.
INTERACTION_FOR_TYPE: Dict[str, str] = {
    "recall": "choose", "flashcard": "choose", "quiz": "choose", "comparison": "choose",
    "labeling": "match", "matching": "match",
    "classification": "classify",
    "sequencing": "order",
    "puzzle": "order", "construction": "order", "design": "order",
    "simulation": "choose", "strategy": "choose", "decision": "choose",
    "role_play": "choose", "critique": "choose", "debate": "choose",
    "storytelling": "order", "exploration": "choose",
}


def interaction_for(mech_type: str) -> str:
    return INTERACTION_FOR_TYPE.get(mech_type, "choose")


# --------------------------------------------------------------------------- #
# Bancos de conteúdo por domínio. Cada banco fornece itens para cada interação.
# Dois domínios reais (para demonstrar RF22) + um gerador genérico de fallback.
# --------------------------------------------------------------------------- #
_FRACOES = {
    "choose": [
        {"prompt": "Qual fração é maior?", "options": ["1/2", "1/3"], "correct": 0,
         "explanation": "1/2 = 0,5 e 1/3 ≈ 0,33; logo 1/2 é maior."},
        {"prompt": "Qual fração é maior?", "options": ["2/5", "3/5"], "correct": 1,
         "explanation": "Com o mesmo denominador, maior numerador = maior fração."},
        {"prompt": "Qual fração equivale a 1/2?", "options": ["3/6", "2/5", "4/9"], "correct": 0,
         "explanation": "3/6 simplifica para 1/2."},
        {"prompt": "Qual é maior: 3/4 ou 5/8?", "options": ["3/4", "5/8"], "correct": 0,
         "explanation": "3/4 = 6/8 > 5/8."},
    ],
    "order": {"prompt": "Ordene as frações da menor para a maior:",
              "items": ["1/5", "1/3", "1/2", "3/4"]},
    "match": {"prompt": "Associe cada fração à sua forma decimal:",
              "pairs": [{"a": "1/2", "b": "0,5"}, {"a": "1/4", "b": "0,25"},
                        {"a": "3/4", "b": "0,75"}, {"a": "1/10", "b": "0,1"}]},
    "classify": {"prompt": "Classifique cada fração:",
                 "categories": ["Própria (<1)", "Imprópria (≥1)"],
                 "items": [{"text": "2/3", "category": "Própria (<1)"},
                           {"text": "5/4", "category": "Imprópria (≥1)"},
                           {"text": "7/8", "category": "Própria (<1)"},
                           {"text": "9/9", "category": "Imprópria (≥1)"}]},
}

_AMBIENTAL = {
    "choose": [
        {"prompt": "Qual atitude reduz mais a emissão de CO₂ no dia a dia?",
         "options": ["Ir de bicicleta ao trabalho", "Deixar luzes acesas", "Trocar de celular todo ano"],
         "correct": 0, "explanation": "O transporte ativo evita queima de combustível fóssil."},
        {"prompt": "Qual resíduo vai na lixeira AZUL (reciclável)?",
         "options": ["Papelão", "Resto de comida", "Papel engordurado"], "correct": 0,
         "explanation": "Papelão limpo é reciclável; restos orgânicos e papel engordurado não."},
        {"prompt": "O que é energia renovável?",
         "options": ["Energia solar", "Carvão mineral", "Petróleo"], "correct": 0,
         "explanation": "A solar se renova naturalmente; carvão e petróleo são finitos."},
        {"prompt": "Qual ação ajuda a economizar água?",
         "options": ["Fechar a torneira ao escovar os dentes", "Lavar a calçada com mangueira"],
         "correct": 0, "explanation": "Pequenos hábitos evitam grande desperdício."},
    ],
    "order": {"prompt": "Ordene as etapas da reciclagem do papel:",
              "items": ["Descarte na lixeira azul", "Coleta seletiva", "Triagem na cooperativa",
                        "Reprocessamento em fábrica", "Novo produto de papel"]},
    "match": {"prompt": "Associe cada material à sua cor de coleta seletiva:",
              "pairs": [{"a": "Papel", "b": "Azul"}, {"a": "Plástico", "b": "Vermelho"},
                        {"a": "Vidro", "b": "Verde"}, {"a": "Metal", "b": "Amarelo"}]},
    "classify": {"prompt": "Classifique cada resíduo:",
                 "categories": ["Reciclável", "Orgânico"],
                 "items": [{"text": "Garrafa PET", "category": "Reciclável"},
                           {"text": "Casca de banana", "category": "Orgânico"},
                           {"text": "Lata de alumínio", "category": "Reciclável"},
                           {"text": "Borra de café", "category": "Orgânico"}]},
}

DOMAIN_BANKS: Dict[str, Dict[str, Any]] = {
    "frações": _FRACOES,
    "fracoes": _FRACOES,
    "matemática": _FRACOES,
    "matematica": _FRACOES,
    "educação ambiental": _AMBIENTAL,
    "educacao ambiental": _AMBIENTAL,
    "meio ambiente": _AMBIENTAL,
    "sustentabilidade": _AMBIENTAL,
}


def _generic_bank(topic: str) -> Dict[str, Any]:
    """Banco de conteúdo de fallback, coerente com o tópico declarado (placeholder jogável)."""
    t = topic or "o conteúdo"
    return {
        "choose": [
            {"prompt": f"Sobre {t}: qual afirmação está correta?",
             "options": [f"Afirmação correta sobre {t}", f"Distrator A sobre {t}",
                         f"Distrator B sobre {t}"],
             "correct": 0, "shuffle": True,
             "explanation": f"Esta é a alternativa coerente com {t}. "
                            "(Conteúdo de exemplo — substituível via reparametrização — RF22.)"},
            {"prompt": f"Qual exemplo ilustra melhor {t}?",
             "options": [f"Exemplo representativo de {t}", "Exemplo não relacionado"],
             "correct": 0, "shuffle": True,
             "explanation": f"O primeiro exemplifica diretamente {t}."},
        ],
        "order": {"prompt": f"Ordene as etapas relativas a {t}:",
                  "items": [f"1ª etapa de {t}", f"2ª etapa de {t}",
                            f"3ª etapa de {t}", f"4ª etapa de {t}"]},
        "match": {"prompt": f"Associe os conceitos de {t}:",
                  "pairs": [{"a": f"Conceito 1 ({t})", "b": "Definição 1"},
                            {"a": f"Conceito 2 ({t})", "b": "Definição 2"},
                            {"a": f"Conceito 3 ({t})", "b": "Definição 3"}]},
        "classify": {"prompt": f"Classifique os exemplos de {t}:",
                     "categories": ["Categoria A", "Categoria B"],
                     "items": [{"text": f"Exemplo 1 ({t})", "category": "Categoria A"},
                               {"text": f"Exemplo 2 ({t})", "category": "Categoria B"},
                               {"text": f"Exemplo 3 ({t})", "category": "Categoria A"}]},
    }


def resolve_bank(domain: Optional[str], topic: Optional[str]) -> Dict[str, Any]:
    """Escolhe o banco de conteúdo a partir do domínio/tópico declarado."""
    for candidate in (domain, topic):
        if not candidate:
            continue
        key = str(candidate).strip().lower()
        if key in DOMAIN_BANKS:
            return DOMAIN_BANKS[key]
        for bank_key, bank in DOMAIN_BANKS.items():
            if bank_key in key or key in bank_key:
                return bank
    return _generic_bank(topic or domain or "o conteúdo")


def _bloom_obj(level: Optional[Bloom]) -> Optional[Dict[str, Any]]:
    if level is None:
        return None
    return {"level": int(level), "name": level.pt, "slug": level.slug}


def _stage_content(mech: Mechanic, interaction: str, bank: Dict[str, Any]) -> Dict[str, Any]:
    """Seleciona/clona o conteúdo do banco para a interação da mecânica."""
    if interaction == "choose":
        return {"items": [dict(i) for i in bank.get("choose", _generic_bank("o conteúdo")["choose"])]}
    if interaction == "order":
        return dict(bank.get("order", _generic_bank("o conteúdo")["order"]))
    if interaction == "match":
        return dict(bank.get("match", _generic_bank("o conteúdo")["match"]))
    if interaction == "classify":
        return dict(bank.get("classify", _generic_bank("o conteúdo")["classify"]))
    return {"text": mech.description or "Reflita sobre o desafio proposto."}


def build_content_pack(spec: GameSpec, *,
                       content_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Constrói o content pack completo (estrutura + conteúdo) a partir da AST.

    ``content_overrides`` permite injetar/forçar um domínio ou conteúdo específico
    (usado pela reparametrização — RF22).
    """
    overrides = content_overrides or {}
    domain = overrides.get("domain") or spec.metadata.get("domain")
    # tópico declarado em params 'content' de alguma mecânica
    topic = overrides.get("topic")
    if not topic:
        for m in spec.mechanics:
            if m.params.get("content"):
                topic = str(m.params.get("content"))
                break
    bank = resolve_bank(domain, topic)

    objectives = [
        {
            "name": o.name,
            "description": o.description or o.name,
            "bloom": _bloom_obj(o.bloom),
            "bloom_name": o.bloom.pt if o.bloom else "—",
        }
        for o in spec.objectives
    ]

    stages: List[Dict[str, Any]] = []
    for m in spec.mechanics:
        interaction = interaction_for(m.type)
        type_label = MECHANIC_TYPES[m.type].label if m.type in MECHANIC_TYPES else m.type
        stages.append({
            "mechanic": m.name,
            "type": m.type,
            "type_label": type_label,
            "bloom": _bloom_obj(m.bloom),
            "interaction": interaction,
            "description": m.description,
            "addresses": list(m.addresses),
            "source_component": m.source_component,
            "params": dict(m.params.values),
            "content": _stage_content(m, interaction, bank),
        })

    bloom_levels = [_bloom_obj(b) for b in spec.bloom_levels]

    pack = {
        "title": spec.title,
        "meta": dict(spec.metadata.values),
        "domain": domain,
        "objectives": objectives,
        "stages": stages,
        "bloom_levels": bloom_levels,
        "traceability": build_traceability_data(spec),
    }
    return pack


def build_traceability_data(spec: GameSpec) -> Dict[str, Any]:
    """Dados de rastreabilidade objetivo -> mecânicas (consumido pela engine e por RF23)."""
    links = []
    for o in spec.objectives:
        addressing = [
            {"name": m.name, "type": m.type, "bloom": m.bloom.pt if m.bloom else "—"}
            for m in spec.mechanics if o.name in m.addresses
        ]
        links.append({
            "objective": o.name,
            "objective_description": o.description or o.name,
            "bloom": o.bloom.pt if o.bloom else "—",
            "mechanics": addressing,
        })
    return {"links": links}
