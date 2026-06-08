"""Componentes canônicos iniciais da biblioteca.

Conjunto curado de padrões de design endógeno cobrindo os seis níveis da
Taxonomia de Bloom e diferentes tipos de mecânica. Servem de ponto de partida
para o Agente de Recuperação (RF14) e como exemplos canônicos (RF12).

A função :func:`seed_canonical` é idempotente (não duplica por ``key``).
"""

from __future__ import annotations

from typing import List

from endo_dsl.library.repository import ComponentRepository

_CURATOR = "curadoria"

# (key, name, bloom, type, description, params, dsl_signature)
_SEED: List[dict] = [
    dict(
        key="recordacao_relampago", name="Recordação Relâmpago",
        bloom="Lembrar", mtype="recall",
        description="Cartões rápidos em que o jogador recupera da memória fatos, termos ou "
                    "definições sob tempo, com reforço imediato.",
        params={"content": "fatos/termos", "difficulty": "easy", "domain": "genérico",
                "time_limit": 30},
        sig='mechanic recordacao { type: recall bloom: Lembrar params { content: "$TERMOS" '
            'difficulty: "easy" } description: "Recupere o termo correto antes do tempo acabar." }',
    ),
    dict(
        key="pareamento_conceitual", name="Pareamento Conceitual",
        bloom="Compreender", mtype="matching",
        description="Associa conceitos às suas definições/exemplos, consolidando a compreensão "
                    "por correspondência.",
        params={"content": "conceito-definição", "difficulty": "easy", "domain": "genérico"},
        sig='mechanic pareamento { type: matching bloom: Compreender params { content: '
            '"$PARES" } description: "Associe cada conceito à sua definição." }',
    ),
    dict(
        key="exploracao_investigativa", name="Exploração Investigativa",
        bloom="Compreender", mtype="exploration",
        description="O jogador investiga um ambiente/dataset para descobrir relações e formular "
                    "explicações sobre o fenômeno estudado.",
        params={"content": "fenômeno", "difficulty": "medium", "domain": "genérico"},
        sig='mechanic exploracao { type: exploration bloom: Compreender params { content: '
            '"$FENOMENO" } description: "Investigue e descubra as relações ocultas." }',
    ),
    dict(
        key="sequenciador_processual", name="Sequenciador Processual",
        bloom="Aplicar", mtype="sequencing",
        description="Ordena etapas de um processo (temporal, causal ou procedural), aplicando "
                    "regras de precedência.",
        params={"content": "etapas", "difficulty": "medium", "domain": "genérico"},
        sig='mechanic sequenciador { type: sequencing bloom: Aplicar params { content: '
            '"$ETAPAS" } description: "Coloque as etapas do processo na ordem correta." }',
    ),
    dict(
        key="simulador_de_cenario", name="Simulador de Cenário",
        bloom="Aplicar", mtype="simulation",
        description="Modelo interativo em que o jogador aplica conceitos manipulando variáveis e "
                    "observando consequências.",
        params={"content": "variáveis", "difficulty": "medium", "domain": "genérico"},
        sig='mechanic simulador { type: simulation bloom: Aplicar params { content: "$MODELO" '
            'difficulty: "medium" } description: "Ajuste as variáveis e observe o resultado." }',
    ),
    dict(
        key="balanca_comparadora", name="Balança Comparadora",
        bloom="Analisar", mtype="comparison",
        description="O jogador compara grandezas equilibrando uma balança, analisando relações de "
                    "maior/menor/igual.",
        params={"content": "grandezas", "difficulty": "medium", "domain": "genérico"},
        sig='mechanic balanca { type: comparison bloom: Analisar params { content: "$ITENS" } '
            'description: "Equilibre a balança comparando as grandezas." }',
    ),
    dict(
        key="classificador_por_categorias", name="Classificador por Categorias",
        bloom="Analisar", mtype="classification",
        description="Distribui elementos em categorias segundo critérios, exigindo análise de "
                    "atributos distintivos.",
        params={"content": "elementos", "difficulty": "medium", "domain": "genérico"},
        sig='mechanic classificador { type: classification bloom: Analisar params { content: '
            '"$ELEMENTOS" } description: "Classifique cada elemento na categoria correta." }',
    ),
    dict(
        key="quebra_cabeca_de_regras", name="Quebra-cabeça de Regras",
        bloom="Analisar", mtype="puzzle",
        description="Problema estruturado que se resolve aplicando e combinando regras do domínio.",
        params={"content": "problema", "difficulty": "hard", "domain": "genérico"},
        sig='mechanic puzzle { type: puzzle bloom: Analisar params { content: "$PROBLEMA" '
            'difficulty: "hard" } description: "Resolva o problema aplicando as regras." }',
    ),
    dict(
        key="dilema_de_decisao", name="Dilema de Decisão",
        bloom="Avaliar", mtype="decision",
        description="O jogador pondera critérios e consequências para escolher entre alternativas "
                    "em um dilema, justificando o julgamento.",
        params={"content": "dilema", "difficulty": "hard", "domain": "genérico"},
        sig='mechanic dilema { type: decision bloom: Avaliar params { content: "$DILEMA" } '
            'description: "Pondere os critérios e decida, justificando a escolha." }',
    ),
    dict(
        key="juri_avaliador", name="Júri Avaliador",
        bloom="Avaliar", mtype="critique",
        description="O jogador julga a qualidade/validade de artefatos com base em critérios "
                    "explícitos, exercitando avaliação crítica.",
        params={"content": "artefatos", "difficulty": "hard", "domain": "genérico"},
        sig='mechanic juri { type: critique bloom: Avaliar params { content: "$ARTEFATOS" } '
            'description: "Avalie cada artefato segundo os critérios e justifique." }',
    ),
    dict(
        key="oficina_de_criacao", name="Oficina de Criação",
        bloom="Criar", mtype="design",
        description="Espaço aberto em que o jogador projeta um artefato original que satisfaz "
                    "requisitos, integrando o conteúdo aprendido.",
        params={"content": "requisitos", "difficulty": "hard", "domain": "genérico"},
        sig='mechanic oficina { type: design bloom: Criar params { content: "$REQUISITOS" } '
            'description: "Crie um artefato original que atenda aos requisitos." }',
    ),
    dict(
        key="construtor_modular", name="Construtor Modular",
        bloom="Criar", mtype="construction",
        description="Montagem de um artefato a partir de peças/módulos seguindo regras, "
                    "culminando em uma produção autoral.",
        params={"content": "módulos", "difficulty": "medium", "domain": "genérico"},
        sig='mechanic construtor { type: construction bloom: Criar params { content: "$MODULOS" } '
            'description: "Combine os módulos para construir a solução." }',
    ),
]


def seed_canonical(repo: ComponentRepository, *, force: bool = False) -> List[int]:
    """Cadastra os componentes canônicos ausentes. Retorna os ids criados."""
    created: List[int] = []
    for item in _SEED:
        if not force and repo.get_by_key(item["key"]) is not None:
            continue
        cid = repo.create(
            name=item["name"],
            dsl_signature=item["sig"],
            bloom_level=item["bloom"],
            mechanic_type=item["mtype"],
            description=item["description"],
            params=item["params"],
            domain="genérico (multidomínio)",
            context="formal",
            age_range="livre",
            modality="digital",
            status="canonical",
            author=_CURATOR,
            key=item["key"],
        )
        created.append(cid)
    return created
