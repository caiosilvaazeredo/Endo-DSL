"""Catálogo de mecânicas de jogos de tabuleiro — endo_dsl.boardgame.mechanics.

Cada entrada do catálogo documenta uma mecânica real, usada em jogos de
tabuleiro conhecidos, com sua afinidade cognitiva (Bloom), exemplos de jogos
reais (BGG) e parâmetros configuráveis para geração de especificações.

Referências: BoardGameGeek Mechanics, Ludopedia.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from endo_dsl.dsl.bloom import Bloom


@dataclass
class BoardMechanic:
    """Descreve uma mecânica de jogo de tabuleiro catalogada."""

    id: str
    name: str                        # Nome em português
    description: str
    bloom_affinity: List[Bloom]
    game_examples: List[str]         # Jogos reais que usam a mecânica
    params: Dict[str, Any]           # Parâmetros configuráveis com defaults
    interaction_type: str            # Categoria de interação


# ---------------------------------------------------------------------------
# Catálogo principal
# ---------------------------------------------------------------------------

MECHANICS_CATALOG: Dict[str, BoardMechanic] = {

    "grid_movement": BoardMechanic(
        id="grid_movement",
        name="Movimento em Grade",
        description=(
            "Peças se movem em um tabuleiro quadriculado segundo regras direcionais "
            "fixas (ortogonal, diagonal, L etc.). A grade impõe restrições espaciais "
            "que criam problemas táticos e estratégicos."
        ),
        bloom_affinity=[Bloom.APLICAR, Bloom.ANALISAR],
        game_examples=["Xadrez", "Damas", "Batalha Naval", "Reversi", "Go"],
        params={
            "grid_rows": {"type": "int", "default": 8, "min": 4, "max": 20},
            "grid_cols": {"type": "int", "default": 8, "min": 4, "max": 20},
            "move_directions": {"type": "list", "default": ["orthogonal", "diagonal"]},
            "blocked_spaces": {"type": "bool", "default": False},
        },
        interaction_type="movement",
    ),

    "roll_and_move": BoardMechanic(
        id="roll_and_move",
        name="Rolar e Mover",
        description=(
            "Jogadores rolam dados e avançam sua peça o número correspondente de "
            "casas em uma trilha. O acaso do dado é o motor principal do progresso, "
            "combinado com efeitos das casas em que o jogador para."
        ),
        bloom_affinity=[Bloom.LEMBRAR, Bloom.COMPREENDER],
        game_examples=["Banco Imobiliário", "Jogo da Vida", "Ludo", "Parcheesi", "War"],
        params={
            "dice_count": {"type": "int", "default": 1},
            "dice_sides": {"type": "int", "default": 6},
            "track_length": {"type": "int", "default": 40},
            "loop_track": {"type": "bool", "default": True},
        },
        interaction_type="movement",
    ),

    "hand_management": BoardMechanic(
        id="hand_management",
        name="Gerenciamento de Mão",
        description=(
            "Jogadores mantêm cartas na mão e decidem quando e como jogá-las, "
            "equilibrando uso imediato com reserva estratégica. A composição da mão "
            "cria decisões táticas contínuas."
        ),
        bloom_affinity=[Bloom.APLICAR, Bloom.ANALISAR],
        game_examples=["Uno", "Imagem & Ação", "Coup", "Hanabi", "7 Wonders"],
        params={
            "hand_size": {"type": "int", "default": 7},
            "draw_per_turn": {"type": "int", "default": 1},
            "discard_rule": {"type": "str", "default": "any"},
            "visible_to_others": {"type": "bool", "default": False},
        },
        interaction_type="cards",
    ),

    "set_collection": BoardMechanic(
        id="set_collection",
        name="Coleção de Conjuntos",
        description=(
            "Jogadores acumulam grupos de itens que formam conjuntos valorados. "
            "Completar um conjunto gera pontos ou efeitos especiais; a competição "
            "por itens cria tensão e decisões de prioridade."
        ),
        bloom_affinity=[Bloom.COMPREENDER, Bloom.APLICAR],
        game_examples=["Ticket to Ride", "Rummy", "Mahjong", "Sushi Go", "Jogo da Memória"],
        params={
            "set_size": {"type": "int", "default": 3},
            "set_types": {"type": "int", "default": 4},
            "points_per_set": {"type": "int", "default": 5},
            "partial_score": {"type": "bool", "default": False},
        },
        interaction_type="collection",
    ),

    "area_control": BoardMechanic(
        id="area_control",
        name="Controle de Área",
        description=(
            "Jogadores competem pelo domínio de regiões do tabuleiro posicionando "
            "peças ou tropas. Quem controla mais territórios ou territórios-chave "
            "vence. Exige planejamento espacial e leitura do adversário."
        ),
        bloom_affinity=[Bloom.ANALISAR, Bloom.AVALIAR],
        game_examples=["Risk", "War", "Catan", "Smallworld", "Kemet"],
        params={
            "regions_count": {"type": "int", "default": 12},
            "troops_per_player": {"type": "int", "default": 20},
            "majority_threshold": {"type": "int", "default": 1},
            "scoring_rounds": {"type": "int", "default": 3},
        },
        interaction_type="area_control",
    ),

    "resource_management": BoardMechanic(
        id="resource_management",
        name="Gestão de Recursos",
        description=(
            "Jogadores produzem, armazenam e gastam recursos para executar ações. "
            "Balancear produção e consumo, e otimizar conversões, é o núcleo "
            "estratégico desta mecânica."
        ),
        bloom_affinity=[Bloom.APLICAR, Bloom.ANALISAR, Bloom.AVALIAR],
        game_examples=["Catan", "Puerto Rico", "Agricola", "Brass", "Terraforming Mars"],
        params={
            "resource_types": {"type": "list", "default": ["madeira", "tijolo", "trigo", "lã", "minério"]},
            "storage_limit": {"type": "int", "default": 7},
            "production_per_turn": {"type": "int", "default": 2},
        },
        interaction_type="resource_management",
    ),

    "worker_placement": BoardMechanic(
        id="worker_placement",
        name="Alocação de Trabalhadores",
        description=(
            "Jogadores posicionam trabalhadores em espaços de ação limitados para "
            "executar ações exclusivas. A competição pelos espaços força "
            "priorização e planejamento antecipado."
        ),
        bloom_affinity=[Bloom.ANALISAR, Bloom.AVALIAR],
        game_examples=["Agricola", "Stone Age", "Pandemic", "Lords of Waterdeep", "Viticulture"],
        params={
            "workers_per_player": {"type": "int", "default": 3},
            "action_spaces": {"type": "int", "default": 12},
            "exclusive_spaces": {"type": "bool", "default": True},
            "rounds": {"type": "int", "default": 6},
        },
        interaction_type="worker_placement",
    ),

    "deck_building": BoardMechanic(
        id="deck_building",
        name="Construção de Baralho",
        description=(
            "Jogadores iniciam com um baralho fraco e durante o jogo compram cartas "
            "melhores que integram seu baralho. A evolução do baralho é o arco "
            "central da estratégia."
        ),
        bloom_affinity=[Bloom.APLICAR, Bloom.ANALISAR, Bloom.CRIAR],
        game_examples=["Dominion", "Clank!", "Star Realms", "Thunderstone", "Legendary"],
        params={
            "starting_deck_size": {"type": "int", "default": 10},
            "market_size": {"type": "int", "default": 5},
            "shuffle_on_empty": {"type": "bool", "default": True},
            "trash_allowed": {"type": "bool", "default": True},
        },
        interaction_type="deck_building",
    ),

    "tile_placement": BoardMechanic(
        id="tile_placement",
        name="Colocação de Peças/Tiles",
        description=(
            "Jogadores posicionam peças (tiles) para construir o tabuleiro ou "
            "completar padrões. A combinação de bordas, formas e adjacências gera "
            "um espaço de puzzles emergente."
        ),
        bloom_affinity=[Bloom.APLICAR, Bloom.ANALISAR],
        game_examples=["Carcassonne", "Blokus", "Scrabble", "Azul", "Barenpark"],
        params={
            "tile_shapes": {"type": "list", "default": ["square", "L", "T"]},
            "placement_rules": {"type": "str", "default": "edge_match"},
            "scoring_per_feature": {"type": "bool", "default": True},
        },
        interaction_type="tile_placement",
    ),

    "pattern_recognition": BoardMechanic(
        id="pattern_recognition",
        name="Reconhecimento de Padrões",
        description=(
            "Jogadores identificam padrões visuais, sequências ou correspondências "
            "entre estímulos. O desempenho é medido por velocidade e precisão de "
            "identificação. Ativa atenção e memória operacional."
        ),
        bloom_affinity=[Bloom.LEMBRAR, Bloom.COMPREENDER],
        game_examples=["Genius", "Simon", "Jogo da Memória", "Dobble/Spot it", "Set"],
        params={
            "pattern_complexity": {"type": "str", "default": "low", "options": ["low", "medium", "high"]},
            "time_limit_seconds": {"type": "int", "default": 0},
            "visual_only": {"type": "bool", "default": True},
        },
        interaction_type="pattern",
    ),

    "deduction": BoardMechanic(
        id="deduction",
        name="Dedução Lógica",
        description=(
            "Jogadores coletam pistas e raciocinam por eliminação para descobrir "
            "uma solução oculta (assassino, localização, objeto). Exige pensamento "
            "sistemático e uso de informação parcial."
        ),
        bloom_affinity=[Bloom.ANALISAR, Bloom.AVALIAR],
        game_examples=["Detetive/Clue", "Cluedo", "Mysterium", "Sherlock Holmes", "Deduction"],
        params={
            "clue_types": {"type": "int", "default": 3},
            "solution_categories": {"type": "int", "default": 3},
            "false_clues": {"type": "bool", "default": False},
            "note_sheet": {"type": "bool", "default": True},
        },
        interaction_type="deduction",
    ),

    "word_building": BoardMechanic(
        id="word_building",
        name="Formação de Palavras",
        description=(
            "Jogadores formam palavras a partir de letras disponíveis, acumulando "
            "pontos segundo o valor das letras e posicionamento. Exercita vocabulário, "
            "ortografia e raciocínio combinatório."
        ),
        bloom_affinity=[Bloom.LEMBRAR, Bloom.COMPREENDER, Bloom.APLICAR],
        game_examples=["Scrabble", "Bananagrams", "Stop", "Palavras Cruzadas", "Jogo das Palavras"],
        params={
            "letter_distribution": {"type": "str", "default": "portuguese"},
            "min_word_length": {"type": "int", "default": 2},
            "dictionary": {"type": "str", "default": "pt_BR"},
            "bonus_tiles": {"type": "bool", "default": True},
        },
        interaction_type="word",
    ),

    "trivia": BoardMechanic(
        id="trivia",
        name="Perguntas e Respostas (Trivia)",
        description=(
            "Jogadores respondem perguntas sobre um domínio de conhecimento para "
            "pontuar ou avançar. A dificuldade pode ser categorizada por tema e "
            "nível cognitivo, tornando-a ideal para jogos educativos."
        ),
        bloom_affinity=[Bloom.LEMBRAR, Bloom.COMPREENDER, Bloom.APLICAR],
        game_examples=["Perguntados", "Show do Milhão", "Genius Perguntados", "Imagem & Ação", "War Perguntados"],
        params={
            "question_count": {"type": "int", "default": 50},
            "categories": {"type": "list", "default": ["geral"]},
            "time_limit_seconds": {"type": "int", "default": 30},
            "multiple_choice": {"type": "bool", "default": True},
            "choices_count": {"type": "int", "default": 4},
        },
        interaction_type="cards",
    ),

    "cooperative": BoardMechanic(
        id="cooperative",
        name="Cooperação",
        description=(
            "Todos os jogadores trabalham juntos como um time contra o jogo. "
            "Comunicação, divisão de papéis e planejamento coletivo são essenciais; "
            "o grupo ganha ou perde junto."
        ),
        bloom_affinity=[Bloom.APLICAR, Bloom.ANALISAR, Bloom.AVALIAR],
        game_examples=["Pandemic", "Hanabi", "Forbidden Island", "Spirit Island", "Flash Point"],
        params={
            "threat_level": {"type": "str", "default": "normal", "options": ["easy", "normal", "hard"]},
            "roles": {"type": "bool", "default": True},
            "hidden_info": {"type": "bool", "default": False},
            "win_conditions": {"type": "int", "default": 1},
        },
        interaction_type="cooperation",
    ),

    "auction_bidding": BoardMechanic(
        id="auction_bidding",
        name="Leilão / Lance",
        description=(
            "Jogadores competem por itens ou direitos fazendo lances em moeda do "
            "jogo. Avaliar o valor justo, blefar e gerir o orçamento são habilidades "
            "centrais. Ativa raciocínio econômico."
        ),
        bloom_affinity=[Bloom.ANALISAR, Bloom.AVALIAR],
        game_examples=["Banco Imobiliário", "Power Grid", "Ra", "Modern Art", "For Sale"],
        params={
            "starting_money": {"type": "int", "default": 1500},
            "auction_type": {"type": "str", "default": "open", "options": ["open", "blind", "dutch"]},
            "minimum_bid": {"type": "int", "default": 1},
            "pass_allowed": {"type": "bool", "default": True},
        },
        interaction_type="auction",
    ),

    "push_your_luck": BoardMechanic(
        id="push_your_luck",
        name="Arriscar a Sorte",
        description=(
            "Jogadores decidem quando parar de acumular benefícios antes de sofrer "
            "penalidade por excesso de risco. Cada rolagem/ação adicional aumenta o "
            "ganho potencial mas também a chance de perda total."
        ),
        bloom_affinity=[Bloom.APLICAR, Bloom.AVALIAR],
        game_examples=["Perudo", "Can't Stop", "King of Tokyo", "Quake", "Bohnanza"],
        params={
            "bust_condition": {"type": "str", "default": "three_of_a_kind"},
            "max_presses": {"type": "int", "default": 5},
            "progressive_penalty": {"type": "bool", "default": True},
        },
        interaction_type="dice",
    ),

    "social_deduction": BoardMechanic(
        id="social_deduction",
        name="Dedução Social",
        description=(
            "Jogadores têm papéis secretos (vilão/herói) e devem identificar "
            "os adversários por pistas comportamentais, argumentação e voto. "
            "Exige leitura de sinais sociais e retórica persuasiva."
        ),
        bloom_affinity=[Bloom.ANALISAR, Bloom.AVALIAR],
        game_examples=["Lobisomem de Millers Hollow", "Coup", "Avalon", "Secret Hitler", "Among Us (tabuleiro)"],
        params={
            "player_count_min": {"type": "int", "default": 5},
            "player_count_max": {"type": "int", "default": 15},
            "role_count": {"type": "int", "default": 3},
            "night_phase": {"type": "bool", "default": True},
            "elimination": {"type": "bool", "default": True},
        },
        interaction_type="social",
    ),

    "memory": BoardMechanic(
        id="memory",
        name="Memória",
        description=(
            "Peças ou cartas ficam viradas para baixo; jogadores viram pares e "
            "tentam memorizar posições para encontrar correspondências. Exercita "
            "atenção, memória de curto prazo e estratégia de exploração."
        ),
        bloom_affinity=[Bloom.LEMBRAR, Bloom.COMPREENDER],
        game_examples=["Jogo da Memória", "Dobble/Spot it", "Pelmanism", "Memory Disney"],
        params={
            "card_pairs": {"type": "int", "default": 24},
            "category": {"type": "str", "default": "figures"},
            "face_down_start": {"type": "bool", "default": True},
            "flips_per_turn": {"type": "int", "default": 2},
        },
        interaction_type="memory",
    ),

    "dice_rolling": BoardMechanic(
        id="dice_rolling",
        name="Rolagem de Dados",
        description=(
            "Dados são lançados para determinar resultados — movimento, combate, "
            "produção ou eventos aleatórios. Pode ser puro acaso ou combinado com "
            "escolhas de mitigação (reroll, modificadores)."
        ),
        bloom_affinity=[Bloom.LEMBRAR, Bloom.APLICAR],
        game_examples=["Ludo", "Parcheesi", "Xadrez com Dados", "King of Tokyo", "Yahtzee"],
        params={
            "dice_count": {"type": "int", "default": 2},
            "dice_sides": {"type": "int", "default": 6},
            "reroll_allowed": {"type": "bool", "default": False},
            "reroll_count": {"type": "int", "default": 1},
        },
        interaction_type="dice",
    ),

    "card_drafting": BoardMechanic(
        id="card_drafting",
        name="Seleção/Passagem de Cartas (Drafting)",
        description=(
            "Jogadores selecionam cartas de um conjunto compartilhado e passam o "
            "restante para o próximo. As escolhas são simultâneas e interativas: "
            "negar cartas ao adversário é tão importante quanto tomar as melhores."
        ),
        bloom_affinity=[Bloom.ANALISAR, Bloom.AVALIAR],
        game_examples=["7 Wonders", "Sushi Go", "Blood Rage", "Terraforming Mars", "Wingspan"],
        params={
            "cards_per_hand": {"type": "int", "default": 7},
            "direction": {"type": "str", "default": "left", "options": ["left", "right", "alternate"]},
            "rounds": {"type": "int", "default": 3},
            "keep_per_turn": {"type": "int", "default": 1},
        },
        interaction_type="drafting",
    ),

    "track_movement": BoardMechanic(
        id="track_movement",
        name="Movimento em Trilha",
        description=(
            "Jogadores movem peças ao longo de uma trilha linear ou circular "
            "com casas especiais. A ordem de chegada define vencedor ou acesso a "
            "benefícios; casas especiais adicionam eventos e decisões."
        ),
        bloom_affinity=[Bloom.LEMBRAR, Bloom.COMPREENDER],
        game_examples=["Trilha", "Ludo", "Jogo da Vida", "Cobra e Escada", "Banco Imobiliário"],
        params={
            "track_length": {"type": "int", "default": 60},
            "circular": {"type": "bool", "default": False},
            "special_spaces": {"type": "int", "default": 10},
            "shortcut_spaces": {"type": "bool", "default": True},
        },
        interaction_type="movement",
    ),

    "territory_building": BoardMechanic(
        id="territory_building",
        name="Construção de Território",
        description=(
            "Jogadores expandem influência no tabuleiro construindo estruturas ou "
            "conectando pontos. A adjacência e a conectividade da rede definem valor "
            "e pontuação dos territórios construídos."
        ),
        bloom_affinity=[Bloom.APLICAR, Bloom.ANALISAR],
        game_examples=["Catan", "Go", "Reversi/Othello", "Tigris & Euphrates", "Blokus"],
        params={
            "structure_types": {"type": "list", "default": ["estrada", "cidade", "aldeia"]},
            "connection_scoring": {"type": "bool", "default": True},
            "max_structures": {"type": "int", "default": 15},
        },
        interaction_type="building",
    ),

    "elimination": BoardMechanic(
        id="elimination",
        name="Eliminação",
        description=(
            "Jogadores que atingem determinada condição de derrota (sem cartas, "
            "sem peças, pontuação negativa) são eliminados. O jogo continua até "
            "restar apenas um jogador ou equipe."
        ),
        bloom_affinity=[Bloom.APLICAR, Bloom.AVALIAR],
        game_examples=["Uno", "War", "Seis Que Leva", "Lobo & Ovelhas", "Coup"],
        params={
            "lives_per_player": {"type": "int", "default": 1},
            "rejoin_allowed": {"type": "bool", "default": False},
            "last_player_wins": {"type": "bool", "default": True},
        },
        interaction_type="combat",
    ),

    "scoring": BoardMechanic(
        id="scoring",
        name="Pontuação por Área/Feature",
        description=(
            "Jogadores acumulam pontos por concluir features (estradas, cidades, "
            "monges, regiões) que são avaliadas no final ou em pontos intermediários. "
            "Gerenciar quais features completar primeiro é a chave estratégica."
        ),
        bloom_affinity=[Bloom.ANALISAR, Bloom.AVALIAR],
        game_examples=["Scrabble", "Carcassonne", "Ticket to Ride", "Azul", "Wingspan"],
        params={
            "scoring_moments": {"type": "list", "default": ["end_game"]},
            "bonus_scoring": {"type": "bool", "default": True},
            "negative_points": {"type": "bool", "default": False},
        },
        interaction_type="scoring",
    ),

    "quiz_challenge": BoardMechanic(
        id="quiz_challenge",
        name="Desafio de Perguntas Educativas",
        description=(
            "Variante educativa do trivia: perguntas são alinhadas a objetivos "
            "pedagógicos específicos, categorizadas por nível de Bloom e vinculadas "
            "a conteúdo curricular. Acerto correto avança o jogador ou concede recurso."
        ),
        bloom_affinity=[Bloom.LEMBRAR, Bloom.COMPREENDER, Bloom.APLICAR, Bloom.ANALISAR],
        game_examples=["Perguntados Educativo", "Banco Imobiliário Educativo", "Trilha do Saber", "Show do Saber"],
        params={
            "question_count": {"type": "int", "default": 40},
            "bloom_distribution": {"type": "dict", "default": {
                "Lembrar": 0.30, "Compreender": 0.30,
                "Aplicar": 0.25, "Analisar": 0.15,
            }},
            "feedback_on_error": {"type": "bool", "default": True},
            "hint_allowed": {"type": "bool", "default": True},
            "hint_penalty": {"type": "int", "default": 1},
            "time_limit_seconds": {"type": "int", "default": 60},
        },
        interaction_type="cards",
    ),
}


# ---------------------------------------------------------------------------
# Templates de arcátipos de jogos de tabuleiro
# ---------------------------------------------------------------------------

BOARD_GAME_TEMPLATES: Dict[str, Dict] = {
    "trilha": {
        "name": "Trilha Educativa",
        "description": "Trilha com dados, casas especiais e perguntas — estilo Cobra e Escada educativo.",
        "mechanics": ["track_movement", "roll_and_move", "quiz_challenge"],
        "bloom_focus": [Bloom.LEMBRAR, Bloom.COMPREENDER, Bloom.APLICAR],
        "player_range": (2, 4),
        "duration_min": 20,
    },
    "quiz_battle": {
        "name": "Batalha de Quiz",
        "description": "Duelo de trivia com eliminação e pontuação — estilo Perguntados.",
        "mechanics": ["trivia", "elimination", "scoring"],
        "bloom_focus": [Bloom.LEMBRAR, Bloom.COMPREENDER, Bloom.APLICAR],
        "player_range": (2, 6),
        "duration_min": 30,
    },
    "memory_match": {
        "name": "Jogo da Memória Temático",
        "description": "Pares temáticos com coleção de conjuntos e reconhecimento de padrões.",
        "mechanics": ["memory", "pattern_recognition", "set_collection"],
        "bloom_focus": [Bloom.LEMBRAR, Bloom.COMPREENDER],
        "player_range": (2, 4),
        "duration_min": 15,
    },
    "word_race": {
        "name": "Corrida de Palavras",
        "description": "Formação de palavras com pontuação e limite de tempo — estilo Scrabble.",
        "mechanics": ["word_building", "scoring", "tile_placement"],
        "bloom_focus": [Bloom.LEMBRAR, Bloom.COMPREENDER, Bloom.APLICAR],
        "player_range": (2, 4),
        "duration_min": 45,
    },
    "strategy_grid": {
        "name": "Grade Estratégica",
        "description": "Tabuleiro de grade com controle de área e eliminação — estilo Xadrez/Damas.",
        "mechanics": ["grid_movement", "area_control", "elimination"],
        "bloom_focus": [Bloom.APLICAR, Bloom.ANALISAR, Bloom.AVALIAR],
        "player_range": (2, 2),
        "duration_min": 30,
    },
    "cooperative_quest": {
        "name": "Missão Cooperativa",
        "description": "RPG de tabuleiro cooperativo com alocação de papéis e gestão de recursos.",
        "mechanics": ["cooperative", "worker_placement", "resource_management"],
        "bloom_focus": [Bloom.APLICAR, Bloom.ANALISAR, Bloom.AVALIAR],
        "player_range": (2, 5),
        "duration_min": 60,
    },
    "auction_economy": {
        "name": "Economia e Leilão",
        "description": "Gestão econômica com leilões e troca — estilo Banco Imobiliário.",
        "mechanics": ["resource_management", "auction_bidding", "trading"],
        "bloom_focus": [Bloom.APLICAR, Bloom.ANALISAR, Bloom.AVALIAR],
        "player_range": (3, 6),
        "duration_min": 60,
    },
    "deduction_mystery": {
        "name": "Mistério e Dedução",
        "description": "Investigação com dedução social, pistas e seleção de cartas — estilo Cluedo.",
        "mechanics": ["deduction", "social_deduction", "card_drafting"],
        "bloom_focus": [Bloom.ANALISAR, Bloom.AVALIAR],
        "player_range": (3, 6),
        "duration_min": 45,
    },
}
