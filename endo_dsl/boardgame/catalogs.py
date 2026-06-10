"""Catálogos de blocos lógicos MDA — Mecânicas, Dinâmicas e Estéticas.

Cada catálogo tem 50+ opções configuráveis inspiradas nos jogos de tabuleiro
mais conhecidos. Os blocos são a matéria-prima do Construtor de Blocos
(``/builder``): o usuário seleciona e parametriza blocos em três painéis
separados (M, D, A), define o fluxo num editor BPMN e o sistema emite a DSL
``boardgame{}`` correspondente (ver :mod:`endo_dsl.boardgame.block_builder`).

Fidelidade: os parâmetros expostos permitem recriar a estrutura dos jogos
que inspiraram cada bloco (Catan, Monopoly, Uno, Cluedo, Pandemic, …),
ainda que recriação não seja o objetivo pedagógico.
"""

from __future__ import annotations

from typing import Any, Dict

# --------------------------------------------------------------------------- #
# MECÂNICAS — 56 blocos
# Cada item: name, desc, category, bloom (nível alvo 1-6), inspired_by,
# params (dict nome -> default; tipos inferidos do default), dsl_type
# (tipo emitido no bloco mechanic{} da DSL).
# --------------------------------------------------------------------------- #

def _m(name, desc, category, bloom, inspired, dsl_type, **params):
    return {"name": name, "desc": desc, "category": category, "bloom": bloom,
            "inspired_by": inspired, "dsl_type": dsl_type, "params": params}


MECHANICS_BLOCKS: Dict[str, Dict[str, Any]] = {
    # --- movimento e tabuleiro -------------------------------------------- #
    "roll_and_move":      _m("Rolar e Mover", "Rola dados e move o peão pelo número obtido.", "movimento", 1, "Ludo, Monopoly", "trilha", dice="2d6", spaces=36, allow_backwards=False),
    "track_movement":     _m("Trilha Linear", "Percurso linear de casas do início ao fim.", "movimento", 1, "Jogo da Vida, Candy Land", "trilha", spaces=40, shortcuts=2, traps=3),
    "grid_movement":      _m("Movimento em Grade", "Peças movem-se ortogonal/diagonal em grade NxM.", "movimento", 4, "Xadrez, Damas", "strategy_grid", rows=8, cols=8, diagonal=True, capture=True),
    "point_to_point":     _m("Ponto a Ponto", "Movimento entre nós conectados de um grafo.", "movimento", 3, "Pandemic, Ticket to Ride", "strategy_grid", nodes=12, max_moves=4),
    "area_movement":      _m("Movimento por Áreas", "Tabuleiro dividido em regiões adjacentes.", "movimento", 4, "Risk, War", "strategy_grid", regions=10, units_per_region=5),
    "tile_placement":     _m("Colocação de Peças", "Jogador posiciona peças que estendem o tabuleiro.", "movimento", 5, "Carcassonne, Dominó", "strategy_grid", tiles=24, match_edges=True),
    "pattern_movement":   _m("Movimento por Padrão", "Cada peça tem padrão próprio de movimento.", "movimento", 4, "Xadrez", "strategy_grid", piece_types=4),
    "race_to_finish":     _m("Corrida ao Final", "Vence quem chega primeiro à última casa.", "movimento", 1, "Ludo, Gamão", "trilha", spaces=30, exact_landing=False),
    "snakes_ladders":     _m("Escadas e Atalhos", "Casas especiais que avançam ou retrocedem o peão.", "movimento", 1, "Cobras e Escadas", "trilha", ladders=4, snakes=4, spaces=36),
    "movement_points":    _m("Pontos de Movimento", "Orçamento de pontos gasto para mover por terreno.", "movimento", 3, "Scythe, wargames", "strategy_grid", points_per_turn=5, terrain_costs=True),

    # --- dados e sorte ----------------------------------------------------- #
    "dice_rolling":       _m("Rolagem de Dados", "Resultados de dados decidem ações ou recursos.", "sorte", 1, "Catan, Yahtzee", "trilha", dice="2d6", reroll_allowed=False),
    "dice_allocation":    _m("Alocação de Dados", "Dados rolados são alocados a ações distintas.", "sorte", 4, "Sagrada, Alien Frontiers", "strategy_grid", dice_pool=4, slots=3),
    "push_your_luck":     _m("Force a Sorte", "Continuar arriscando ou parar e garantir ganhos.", "sorte", 5, "Can't Stop, Blackjack", "quiz_battle", bust_threshold=3, bank_option=True),
    "random_events":      _m("Eventos Aleatórios", "Cartas/casas de evento alteram o estado do jogo.", "sorte", 2, "Monopoly (Sorte/Revés)", "trilha", event_count=12, severity="media"),
    "probability_mgmt":   _m("Gestão de Probabilidade", "Decidir com base em distribuição conhecida de resultados.", "sorte", 5, "Catan (números 6/8)", "strategy_grid", show_odds=True),

    # --- cartas ------------------------------------------------------------ #
    "hand_management":    _m("Gestão de Mão", "Decidir quais cartas jogar e quando.", "cartas", 4, "Uno, Magic", "cards_only", hand_size=7, draw_per_turn=1),
    "deck_building":      _m("Construção de Baralho", "Comprar cartas que entram no próprio baralho.", "cartas", 6, "Dominion, Star Realms", "cards_only", market_size=5, starting_deck=10),
    "card_drafting":      _m("Draft de Cartas", "Escolher uma carta e passar o resto adiante.", "cartas", 5, "7 Wonders, Sushi Go", "cards_only", pack_size=7, rounds=3),
    "matching_cards":     _m("Combinação de Cartas", "Jogar carta que combine em cor/número/conceito.", "cartas", 2, "Uno, Mau-Mau", "cards_only", match_rules="cor_ou_valor", wild_cards=4),
    "set_collection":     _m("Coleção de Conjuntos", "Juntar conjuntos de cartas/itens para pontuar.", "cartas", 3, "Rummikub, Ticket to Ride", "cards_only", set_size=3, set_types=6),
    "trick_taking":       _m("Vazas", "Rodadas em que a carta mais alta leva a vaza.", "cartas", 4, "Copas, Truco", "cards_only", suits=4, trump=True),
    "memory_pairs":       _m("Pares de Memória", "Encontrar pares de cartas viradas para baixo.", "cartas", 1, "Jogo da Memória", "memory_match", pairs=12, peek_time=2),
    "card_trading":       _m("Troca de Cartas", "Negociar cartas com outros jogadores.", "cartas", 5, "Pit, Catan", "cards_only", trade_limit=3),
    "hidden_hand":        _m("Mão Oculta", "Informações privadas na mão de cada jogador.", "cartas", 4, "Poker, Coup", "cards_only", hand_size=2, bluff_allowed=True),
    "discard_pile":       _m("Pilha de Descarte", "Cartas descartadas formam recurso reaproveitável.", "cartas", 3, "Uno, Canastra", "cards_only", pickup_allowed=True),

    # --- recursos e economia ------------------------------------------------ #
    "resource_mgmt":      _m("Gestão de Recursos", "Coletar, gastar e converter recursos.", "economia", 4, "Catan, Agricola", "strategy_grid", resource_types=5, starting_amount=3),
    "trading":            _m("Negociação", "Trocas livres de recursos entre jogadores.", "economia", 5, "Catan, Monopoly", "strategy_grid", bank_rate=4, player_trades=True),
    "auction_bidding":    _m("Leilão e Lances", "Disputar itens por lances abertos ou fechados.", "economia", 5, "Monopoly, Modern Art", "quiz_battle", auction_type="aberto", starting_money=100),
    "property_ownership": _m("Propriedade", "Comprar casas que geram renda quando visitadas.", "economia", 3, "Monopoly", "trilha", properties=22, rent_multiplier=2),
    "income_engine":      _m("Motor de Renda", "Construções geram recursos a cada rodada.", "economia", 6, "Splendor, Monopoly", "strategy_grid", engine_slots=4),
    "investment":         _m("Investimento", "Aplicar recursos agora para retorno futuro.", "economia", 5, "Acquire, Stockpile", "strategy_grid", risk_levels=3),
    "scarcity":           _m("Escassez", "Recursos limitados forçam priorização.", "economia", 5, "Agricola", "strategy_grid", pool_size=20),
    "banking":            _m("Banco", "Reserva central que compra/vende/empresta.", "economia", 3, "Monopoly", "trilha", loan_allowed=False, interest=10),

    # --- conhecimento e quiz ------------------------------------------------ #
    "trivia_questions":   _m("Perguntas e Respostas", "Responder corretamente para avançar/pontuar.", "conhecimento", 1, "Trivial Pursuit, Perfil", "quiz_battle", questions=20, options=4, time_limit=30),
    "category_wedges":    _m("Categorias", "Dominar todas as categorias de conhecimento.", "conhecimento", 2, "Trivial Pursuit", "quiz_battle", categories=6),
    "word_building":      _m("Formação de Palavras", "Construir palavras com letras disponíveis.", "conhecimento", 3, "Scrabble, Boggle", "memory_match", letter_pool=7, bonus_tiles=True),
    "clue_deduction":     _m("Dedução por Pistas", "Eliminar hipóteses com pistas até a resposta.", "conhecimento", 4, "Cluedo, Sherlock", "quiz_battle", suspects=6, weapons=6, rooms=9),
    "sequencing":         _m("Sequenciamento", "Ordenar eventos/etapas na ordem correta.", "conhecimento", 3, "Timeline", "memory_match", sequence_length=6),
    "classification":     _m("Classificação", "Agrupar itens por critérios conceituais.", "conhecimento", 4, "Concept", "memory_match", groups=4, items_per_group=4),
    "estimation":         _m("Estimativa", "Estimar quantidades/valores e comparar com o real.", "conhecimento", 5, "Wits & Wagers", "quiz_battle", tolerance=10),
    "true_false_gauntlet":_m("Verdadeiro ou Falso", "Sequência rápida de afirmações V/F.", "conhecimento", 1, "Quiz shows", "quiz_battle", statements=15, streak_bonus=True),

    # --- conflito e interação ----------------------------------------------- #
    "area_control":       _m("Controle de Área", "Maioria de peças numa região domina-a.", "conflito", 4, "Risk, El Grande", "strategy_grid", regions=8, majority_bonus=3),
    "capture_pieces":     _m("Captura de Peças", "Eliminar peças adversárias por regras de captura.", "conflito", 4, "Damas, Xadrez", "strategy_grid", capture_type="salto"),
    "battle_resolution":  _m("Resolução de Batalha", "Comparar forças/dados para resolver combate.", "conflito", 3, "Risk, War", "strategy_grid", attacker_dice=3, defender_dice=2),
    "take_that":          _m("Ataque Direto", "Cartas/ações que prejudicam adversário específico.", "conflito", 3, "Uno (+4), Munchkin", "cards_only", attack_cards=8),
    "blocking":           _m("Bloqueio", "Ocupar posições para impedir o avanço alheio.", "conflito", 4, "Ludo, Quoridor", "trilha", block_strength=2),
    "elimination":        _m("Eliminação", "Jogadores são eliminados até restar um.", "conflito", 2, "War, Coup", "strategy_grid", lives=3),
    "alliances":          _m("Alianças", "Acordos temporários entre jogadores.", "conflito", 5, "Diplomacy, Risk", "strategy_grid", formal_pacts=False),
    "bluffing":           _m("Blefe", "Declarar informação possivelmente falsa.", "conflito", 5, "Coup, Perudo", "cards_only", challenge_allowed=True),

    # --- cooperação --------------------------------------------------------- #
    "coop_objective":     _m("Objetivo Cooperativo", "Todos vencem ou perdem juntos.", "cooperacao", 3, "Pandemic, Forbidden Island", "cooperative_quest", threat_track=8, team_actions=4),
    "role_powers":        _m("Papéis com Poderes", "Cada jogador tem habilidade única.", "cooperacao", 3, "Pandemic", "cooperative_quest", roles=5),
    "shared_resources":   _m("Recursos Compartilhados", "Pool comum de recursos gerido em grupo.", "cooperacao", 4, "Forbidden Desert", "cooperative_quest", pool=15),
    "traitor_mechanic":   _m("Traidor Oculto", "Um membro secreto trabalha contra a equipe.", "cooperacao", 5, "Betrayal, Saboteur", "cooperative_quest", traitor_count=1),
    "communication_limit":_m("Comunicação Limitada", "Restrições sobre o que pode ser dito.", "cooperacao", 4, "Hanabi, The Mind", "cooperative_quest", hints_per_round=1),

    # --- tempo e turnos ------------------------------------------------------ #
    "turn_order_variable":_m("Ordem de Turno Variável", "Ordem dos turnos muda por regra/leilão.", "tempo", 3, "Power Grid", "strategy_grid", order_rule="pontuacao_inversa"),
    "action_points":      _m("Pontos de Ação", "N ações por turno escolhidas de um menu.", "tempo", 4, "Pandemic, Tikal", "cooperative_quest", actions_per_turn=4),
    "real_time":          _m("Tempo Real", "Todos jogam simultaneamente contra o relógio.", "tempo", 2, "Jungle Speed, Boggle", "memory_match", round_seconds=60),
    "timed_rounds":       _m("Rodadas Cronometradas", "Cada rodada tem limite de tempo.", "tempo", 2, "Pictionary", "quiz_battle", seconds_per_round=45),
    "programmed_actions": _m("Ações Programadas", "Planejar ações com antecedência e revelar.", "tempo", 6, "RoboRally, Colt Express", "strategy_grid", program_length=4),
}

# --------------------------------------------------------------------------- #
# DINÂMICAS — 52 blocos
# Comportamentos emergentes desejados; influenciam regras, pacing e validação.
# --------------------------------------------------------------------------- #

def _d(name, desc, category, emerges_from, inspired, **params):
    return {"name": name, "desc": desc, "category": category,
            "emerges_from": emerges_from, "inspired_by": inspired, "params": params}


DYNAMICS_BLOCKS: Dict[str, Dict[str, Any]] = {
    "competicao_direta":   _d("Competição Direta", "Jogadores disputam o mesmo objetivo frontalmente.", "competicao", ["capture_pieces", "battle_resolution"], "Xadrez, War", intensity="alta"),
    "corrida":             _d("Corrida", "Pressão por ser o primeiro a atingir a meta.", "competicao", ["race_to_finish", "roll_and_move"], "Ludo", pace="acelerado"),
    "king_of_the_hill":    _d("Rei da Colina", "Manter posição dominante sob ataque constante.", "competicao", ["area_control"], "King of Tokyo", contest_rate="alta"),
    "catch_the_leader":    _d("Alcançar o Líder", "Mecanismos que ajudam quem está atrás.", "competicao", ["random_events"], "Mario Kart (analógico)", rubber_band=True),
    "rivalidade_pareada":  _d("Rivalidade Pareada", "Duelo 1x1 dentro de jogo multijogador.", "competicao", ["take_that"], "Munchkin", duel_frequency="media"),
    "guerra_de_atrito":    _d("Guerra de Atrito", "Desgaste gradual de recursos mútuos.", "competicao", ["elimination", "battle_resolution"], "Risk", duration="longa"),

    "colaboracao_total":   _d("Colaboração Total", "Sucesso só com coordenação plena do grupo.", "cooperacao", ["coop_objective", "role_powers"], "Pandemic", coordination="alta"),
    "divisao_de_tarefas":  _d("Divisão de Tarefas", "Especialização espontânea por papel/posição.", "cooperacao", ["role_powers"], "Pandemic", specialization=True),
    "sacrificio":          _d("Sacrifício", "Abrir mão de ganho individual pelo grupo.", "cooperacao", ["shared_resources"], "Forbidden Island", frequency="media"),
    "confianca_fragil":    _d("Confiança Frágil", "Cooperar sabendo que pode haver traidor.", "cooperacao", ["traitor_mechanic"], "Saboteur", paranoia="alta"),
    "ensino_mutuo":        _d("Ensino Mútuo", "Jogadores explicam conceitos uns aos outros.", "cooperacao", ["communication_limit", "trivia_questions"], "Hanabi (adaptado)", peer_learning=True),

    "tensao_crescente":    _d("Tensão Crescente", "Risco/dificuldade aumenta a cada rodada.", "ritmo", ["push_your_luck", "coop_objective"], "Pandemic (epidemias)", curve="exponencial"),
    "climax_final":        _d("Clímax Final", "Última rodada decide tudo.", "ritmo", ["race_to_finish"], "Camel Up", endgame_weight="alto"),
    "altos_e_baixos":      _d("Altos e Baixos", "Reviravoltas frequentes de sorte.", "ritmo", ["random_events", "snakes_ladders"], "Cobras e Escadas", swing="alto"),
    "bola_de_neve":        _d("Bola de Neve", "Vantagens iniciais se amplificam.", "ritmo", ["income_engine"], "Monopoly", snowball=True),
    "recuperacao":         _d("Recuperação", "Sempre é possível voltar ao jogo.", "ritmo", ["catch_the_leader"], "Uno", comeback=True),
    "rodadas_relampago":   _d("Rodadas Relâmpago", "Turnos muito curtos mantêm todos atentos.", "ritmo", ["real_time", "timed_rounds"], "Halli Galli", turn_seconds=15),
    "marato_na_reta":      _d("Maratona com Sprints", "Fases lentas pontuadas por momentos intensos.", "ritmo", ["timed_rounds"], "Jogo da Vida", phase_contrast="alto"),

    "blefe_e_leitura":     _d("Blefe e Leitura", "Ler intenções e esconder as próprias.", "social", ["bluffing", "hidden_hand"], "Coup, Poker", social_deduction=True),
    "negociacao_continua": _d("Negociação Contínua", "Acordos e barganhas o tempo todo.", "social", ["trading", "alliances"], "Catan", table_talk=True),
    "pressao_social":      _d("Pressão Social", "Grupo influencia decisões individuais.", "social", ["auction_bidding"], "leilões", conformity="media"),
    "provocacao_amistosa": _d("Provocação Amistosa", "Zoeira leve incentivada pelas regras.", "social", ["take_that"], "Uno, Munchkin", banter=True),
    "lideranca_emergente": _d("Liderança Emergente", "Um jogador coordena naturalmente o grupo.", "social", ["coop_objective"], "Pandemic (alpha player)", mitigate_alpha=True),
    "voto_e_consenso":     _d("Voto e Consenso", "Decisões coletivas por votação.", "social", ["alliances"], "The Resistance", vote_type="aberto"),

    "exploracao":          _d("Exploração", "Descobrir gradualmente o desconhecido.", "descoberta", ["tile_placement", "point_to_point"], "Carcassonne, Betrayal", fog_of_war=True),
    "revelacao_de_segredo":_d("Revelação de Segredo", "Informações ocultas reveladas no momento certo.", "descoberta", ["clue_deduction", "hidden_hand"], "Cluedo", reveal_pacing="gradual"),
    "investigacao":        _d("Investigação", "Coletar e cruzar evidências.", "descoberta", ["clue_deduction"], "Sherlock Holmes DC", evidence_chains=True),
    "aha_moment":          _d("Momento Eureka", "Insight súbito resolve o problema.", "descoberta", ["sequencing", "classification"], "puzzles", insight_design=True),
    "curiosidade_guiada":  _d("Curiosidade Guiada", "Vontade de ver a próxima carta/casa.", "descoberta", ["random_events", "memory_pairs"], "Candy Land", anticipation=True),

    "otimizacao":          _d("Otimização", "Maximizar eficiência de cada ação.", "estrategia", ["action_points", "resource_mgmt"], "Agricola", depth="alta"),
    "planejamento_longo":  _d("Planejamento de Longo Prazo", "Decisões agora moldam o fim do jogo.", "estrategia", ["income_engine", "investment"], "Catan", horizon="longo"),
    "adaptacao":           _d("Adaptação", "Replanejar conforme o cenário muda.", "estrategia", ["random_events", "dice_allocation"], "Sagrada", flexibility=True),
    "gestao_de_risco":     _d("Gestão de Risco", "Pesar probabilidade vs. recompensa.", "estrategia", ["push_your_luck", "probability_mgmt"], "Can't Stop", risk_literacy=True),
    "trade_off":           _d("Trade-off", "Toda escolha tem custo de oportunidade.", "estrategia", ["card_drafting", "scarcity"], "7 Wonders", tension="alta"),
    "antecipacao_adversario":_d("Antecipação do Adversário", "Prever e contra-jogar o oponente.", "estrategia", ["pattern_movement", "programmed_actions"], "Xadrez, RoboRally", lookahead=2),
    "eficiencia_de_motor": _d("Eficiência de Motor", "Construir combos que se retroalimentam.", "estrategia", ["deck_building", "income_engine"], "Dominion", combo_depth=3),
    "controle_de_territorio":_d("Controle de Território", "Expandir e defender área de influência.", "estrategia", ["area_control", "blocking"], "Risk, Go", map_pressure=True),

    "dominio_progressivo": _d("Domínio Progressivo", "Maestria do conteúdo aumenta jogada a jogada.", "aprendizagem", ["trivia_questions", "category_wedges"], "Trivial Pursuit", scaffold=True),
    "repeticao_espaciada": _d("Repetição Espaçada", "Conceitos reaparecem em intervalos crescentes.", "aprendizagem", ["memory_pairs", "discard_pile"], "flashcards", spacing="crescente"),
    "erro_produtivo":      _d("Erro Produtivo", "Errar tem custo baixo e gera feedback rico.", "aprendizagem", ["trivia_questions"], "design pedagógico", feedback="imediato"),
    "transferencia":       _d("Transferência", "Aplicar conceito aprendido em contexto novo.", "aprendizagem", ["classification", "estimation"], "Concept", context_shift=True),
    "metacognicao":        _d("Metacognição", "Refletir sobre a própria estratégia.", "aprendizagem", ["programmed_actions"], "Xadrez", reflection_prompts=True),
    "avaliacao_por_pares": _d("Avaliação por Pares", "Jogadores julgam respostas uns dos outros.", "aprendizagem", ["estimation", "voto_e_consenso"], "Dixit (adaptado)", peer_review=True),
    "progressao_bloom":    _d("Progressão Bloom", "Desafios sobem na taxonomia ao longo do jogo.", "aprendizagem", ["trivia_questions", "classification"], "Endo-DSL", levels="1-6"),

    "economia_emergente":  _d("Economia Emergente", "Preços/valores flutuam pelas ações dos jogadores.", "economia", ["trading", "auction_bidding"], "Modern Art", market_dynamics=True),
    "inflacao_de_pontos":  _d("Inflação de Pontos", "Recompensas crescem ao longo da partida.", "economia", ["income_engine"], "Splendor", scaling=True),
    "monopolio":           _d("Monopólio", "Concentração de propriedade gera dominância.", "economia", ["property_ownership"], "Monopoly", concentration="alta"),
    "especulacao":         _d("Especulação", "Apostar na valorização futura de ativos.", "economia", ["investment"], "Acquire", volatility="media"),
    "orcamento_apertado":  _d("Orçamento Apertado", "Nunca há recursos para tudo.", "economia", ["scarcity", "action_points"], "Agricola", slack="baixo"),

    "ultima_chance":       _d("Última Chance", "Mecanismo final de virada para os atrás.", "drama", ["climax_final"], "Camel Up", drama="alto"),
    "morte_subita":        _d("Morte Súbita", "Desempate em jogada única decisiva.", "drama", ["battle_resolution"], "pênaltis", stakes="máximo"),
    "conta_regressiva":    _d("Contagem Regressiva", "Fim iminente visível pressiona decisões.", "drama", ["coop_objective", "timed_rounds"], "Pandemic", visibility="alta"),
}

# --------------------------------------------------------------------------- #
# ESTÉTICAS — 54 blocos
# Experiências sensoriais/emocionais; carregam um tema visual (CSS vars)
# aplicado ao HTML5 gerado.
# --------------------------------------------------------------------------- #

def _a(name, desc, category, inspired, primary, secondary, bg, surface, txt,
       font="system-ui", **params):
    return {"name": name, "desc": desc, "category": category,
            "inspired_by": inspired,
            "theme": {"primary": primary, "secondary": secondary, "bg": bg,
                      "surface": surface, "text": txt, "font": font},
            "params": params}


AESTHETICS_BLOCKS: Dict[str, Dict[str, Any]] = {
    # desafio
    "desafio_mental":      _a("Desafio Mental", "Sensação de quebra-cabeça digno do esforço.", "desafio", "Xadrez", "#1e3a8a", "#3b82f6", "#0f172a", "#1e293b", "#e2e8f0"),
    "superacao":           _a("Superação", "Vencer obstáculo antes impossível.", "desafio", "Dark Souls (analógico)", "#7c2d12", "#ea580c", "#1c1917", "#292524", "#fafaf9"),
    "maestria":            _a("Maestria", "Orgulho de dominar um sistema profundo.", "desafio", "Go", "#14532d", "#16a34a", "#f8fafc", "#ffffff", "#1e293b"),
    "pressao_do_tempo":    _a("Pressão do Tempo", "Urgência e adrenalina do relógio.", "desafio", "Boggle", "#991b1b", "#ef4444", "#fef2f2", "#ffffff", "#1f2937", pulse_animation=True),
    "risco_calculado":     _a("Risco Calculado", "Frio na barriga da aposta consciente.", "desafio", "Can't Stop", "#92400e", "#f59e0b", "#fffbeb", "#ffffff", "#1f2937"),

    # fantasia/narrativa
    "fantasia_medieval":   _a("Fantasia Medieval", "Castelos, cavaleiros e masmorras.", "fantasia", "Carcassonne, HeroQuest", "#5b21b6", "#8b5cf6", "#2e1065", "#4c1d95", "#ede9fe", font="Georgia, serif", border_style="ornate"),
    "exploracao_espacial": _a("Exploração Espacial", "Vastidão cósmica e descoberta.", "fantasia", "Twilight Imperium", "#1e1b4b", "#6366f1", "#020617", "#0f172a", "#c7d2fe", starfield=True),
    "mundo_subaquatico":   _a("Mundo Subaquático", "Profundezas misteriosas do oceano.", "fantasia", "Abyss", "#164e63", "#06b6d4", "#082f49", "#0c4a6e", "#cffafe"),
    "selva_aventura":      _a("Selva e Aventura", "Expedição por floresta exuberante.", "fantasia", "Lost Cities, Jumanji", "#14532d", "#22c55e", "#052e16", "#166534", "#dcfce7"),
    "deserto_misterioso":  _a("Deserto Misterioso", "Areias, oásis e ruínas antigas.", "fantasia", "Forbidden Desert", "#92400e", "#fbbf24", "#451a03", "#78350f", "#fef3c7"),
    "epoca_vitoriana":     _a("Época Vitoriana", "Mistério em ruas de gás e neblina.", "fantasia", "Sherlock, Cluedo", "#3f3f46", "#a1a1aa", "#18181b", "#27272a", "#e4e4e7", font="Georgia, serif"),
    "mitologia":           _a("Mitologia", "Deuses, heróis e criaturas lendárias.", "fantasia", "Santorini, Cyclades", "#0c4a6e", "#0ea5e9", "#f0f9ff", "#ffffff", "#0f172a", font="Georgia, serif"),
    "piratas":             _a("Piratas", "Tesouros, mapas e alto-mar.", "fantasia", "Jamaica", "#713f12", "#ca8a04", "#1c1917", "#292524", "#fef9c3"),
    "faroeste":            _a("Faroeste", "Duelo, poeira e saloons.", "fantasia", "Colt Express", "#7c2d12", "#c2410c", "#fef3c7", "#fffbeb", "#431407", font="Georgia, serif"),
    "contos_de_fada":      _a("Contos de Fada", "Encanto e magia de histórias clássicas.", "fantasia", "Candy Land", "#9d174d", "#ec4899", "#fdf2f8", "#ffffff", "#500724", rounded="extra"),
    "steampunk":           _a("Steampunk", "Engrenagens, vapor e latão.", "fantasia", "Brass", "#78350f", "#b45309", "#292524", "#44403c", "#fde68a"),
    "cyberpunk":           _a("Cyberpunk", "Neon, tecnologia e distopia urbana.", "fantasia", "Android: Netrunner", "#86198f", "#d946ef", "#09090b", "#18181b", "#f5d0fe", neon_glow=True),
    "pre_historia":        _a("Pré-História", "Dinossauros e primeiros humanos.", "fantasia", "Evolution", "#3f6212", "#84cc16", "#1a2e05", "#365314", "#ecfccb"),
    "egito_antigo":        _a("Egito Antigo", "Pirâmides, faraós e hieróglifos.", "fantasia", "Camel Up, Ra", "#a16207", "#eab308", "#fefce8", "#fef9c3", "#422006"),
    "laboratorio":         _a("Laboratório Científico", "Experimentos, fórmulas e descobertas.", "fantasia", "Compounded", "#0f766e", "#14b8a6", "#f0fdfa", "#ffffff", "#134e4a"),

    # social/diversão
    "festa_e_riso":        _a("Festa e Riso", "Leveza, gargalhada e descontração.", "social", "Pictionary", "#c026d3", "#f0abfc", "#fdf4ff", "#ffffff", "#4a044e", confetti=True),
    "rivalidade_saudavel": _a("Rivalidade Saudável", "Provocação esportiva entre amigos.", "social", "Uno, Mario Party", "#dc2626", "#f87171", "#fef2f2", "#ffffff", "#450a0a"),
    "uniao_de_equipe":     _a("União de Equipe", "Calor humano de vencer juntos.", "social", "Pandemic", "#0369a1", "#38bdf8", "#f0f9ff", "#ffffff", "#082f49"),
    "suspeita_e_intriga":  _a("Suspeita e Intriga", "Quem está mentindo?", "social", "Coup, Resistance", "#581c87", "#a855f7", "#1e1b4b", "#312e81", "#e9d5ff"),
    "nostalgia":           _a("Nostalgia", "Memória afetiva de jogos da infância.", "social", "Ludo, Memória", "#b45309", "#fbbf24", "#fffbeb", "#fef3c7", "#451a03", font="Georgia, serif"),
    "celebracao":          _a("Celebração", "Conquistas comemoradas com destaque.", "social", "Mario Party", "#15803d", "#4ade80", "#f0fdf4", "#ffffff", "#052e16", confetti=True),

    # sensorial/expressão
    "minimalismo":         _a("Minimalismo", "Clareza absoluta, zero ruído visual.", "sensorial", "Azul, Hive", "#334155", "#64748b", "#ffffff", "#f8fafc", "#0f172a"),
    "cores_vibrantes":     _a("Cores Vibrantes", "Paleta saturada e alegre.", "sensorial", "Uno, Camel Up", "#e11d48", "#fb923c", "#fff7ed", "#ffffff", "#1c1917", rainbow_accents=True),
    "elegancia_classica":  _a("Elegância Clássica", "Sobriedade de madeira e feltro.", "sensorial", "Xadrez, Gamão", "#44403c", "#78716c", "#fafaf9", "#f5f5f4", "#1c1917", font="Georgia, serif"),
    "papel_e_lapis":       _a("Papel e Lápis", "Charme artesanal de rabiscos.", "sensorial", "Pictionary", "#404040", "#737373", "#fefce8", "#fffbeb", "#262626", sketch_style=True),
    "mosaico_geometrico":  _a("Mosaico Geométrico", "Padrões e ladrilhos hipnóticos.", "sensorial", "Azul, Sagrada", "#0e7490", "#22d3ee", "#ecfeff", "#ffffff", "#164e63", pattern="azulejo"),
    "noite_e_neon":        _a("Noite e Neon", "Escuro elegante com brilhos pontuais.", "sensorial", "Tron (analógico)", "#0ea5e9", "#22d3ee", "#020617", "#0f172a", "#e0f2fe", neon_glow=True),
    "aquarela":            _a("Aquarela", "Suavidade de tintas diluídas.", "sensorial", "Dixit", "#7e22ce", "#c084fc", "#faf5ff", "#ffffff", "#3b0764", soft_edges=True),
    "alto_contraste":      _a("Alto Contraste", "Acessibilidade máxima de leitura.", "sensorial", "design inclusivo", "#000000", "#1d4ed8", "#ffffff", "#f8fafc", "#000000", a11y=True),
    "tabuleiro_de_madeira":_a("Tabuleiro de Madeira", "Textura quente de mesa clássica.", "sensorial", "Catan", "#854d0e", "#a16207", "#fef3c7", "#fde68a", "#422006"),
    "quadro_negro":        _a("Quadro Negro", "Sala de aula com giz e lousa.", "sensorial", "escola", "#e2e8f0", "#94a3b8", "#1e293b", "#334155", "#f1f5f9", chalk_style=True),

    # emoção/submissão
    "calma_e_foco":        _a("Calma e Foco", "Ambiente zen para concentração.", "emocao", "Calico, Patchwork", "#0d9488", "#5eead4", "#f0fdfa", "#ffffff", "#134e4a", animations="reduzidas"),
    "tensao_silenciosa":   _a("Tensão Silenciosa", "Quietude carregada antes da jogada.", "emocao", "Xadrez", "#1e293b", "#475569", "#f8fafc", "#ffffff", "#0f172a"),
    "euforia_de_vitoria":  _a("Euforia de Vitória", "Explosão celebratória ao vencer.", "emocao", "Mario Party", "#facc15", "#fde047", "#fefce8", "#ffffff", "#422006", confetti=True, fanfare=True),
    "misterio_e_arrepio":  _a("Mistério e Arrepio", "Suspense que prende a respiração.", "emocao", "Betrayal, Mysterium", "#4c1d95", "#7c3aed", "#0f0a1e", "#1e1b4b", "#ddd6fe", fog_overlay=True),
    "aconchego":           _a("Aconchego", "Conforto de tarde chuvosa com jogos.", "emocao", "Patchwork", "#9a3412", "#fb923c", "#fff7ed", "#ffedd5", "#431407"),
    "ambicao":             _a("Ambição", "Fome de construir um império.", "emocao", "Monopoly, Brass", "#065f46", "#10b981", "#f0fdf4", "#ffffff", "#022c22", gold_accents=True),
    "vertigem":            _a("Vertigem", "Sensação de aposta tudo-ou-nada.", "emocao", "cassino", "#881337", "#fb7185", "#1c1917", "#292524", "#ffe4e6"),

    # narrativa pedagógica
    "jornada_do_heroi":    _a("Jornada do Herói", "Progresso narrativo de aprendiz a mestre.", "pedagogica", "RPGs", "#6d28d9", "#a78bfa", "#f5f3ff", "#ffffff", "#2e1065", progress_narrative=True),
    "expedicao_cientifica":_a("Expedição Científica", "Aluno como cientista explorador.", "pedagogica", "Terra Mystica (adapt.)", "#0c4a6e", "#0284c7", "#f0f9ff", "#ffffff", "#082f49", field_journal=True),
    "detetive_do_saber":   _a("Detetive do Saber", "Resolver mistérios com conhecimento.", "pedagogica", "Cluedo", "#7f1d1d", "#dc2626", "#fef2f2", "#ffffff", "#450a0a", magnify_icons=True),
    "construtor_de_mundos":_a("Construtor de Mundos", "Criar e ver sua obra crescer.", "pedagogica", "Catan, Minecraft", "#166534", "#22c55e", "#f0fdf4", "#ffffff", "#052e16", build_visuals=True),
    "olimpiada_mental":    _a("Olimpíada Mental", "Espírito esportivo aplicado ao saber.", "pedagogica", "torneios", "#1d4ed8", "#60a5fa", "#eff6ff", "#ffffff", "#172554", medals=True),
    "museu_vivo":          _a("Museu Vivo", "Curadoria e apreciação de artefatos.", "pedagogica", "Museum", "#713f12", "#d97706", "#fffbeb", "#fef3c7", "#451a03", font="Georgia, serif"),
    "viagem_no_tempo":     _a("Viagem no Tempo", "Saltar entre épocas históricas.", "pedagogica", "Timeline", "#3730a3", "#818cf8", "#eef2ff", "#ffffff", "#1e1b4b", era_transitions=True),
    "horta_do_conhecimento":_a("Horta do Conhecimento", "Plantar e colher saberes.", "pedagogica", "Agricola (adapt.)", "#3f6212", "#a3e635", "#f7fee7", "#ffffff", "#1a2e05", growth_visuals=True),
    "oficina_maker":       _a("Oficina Maker", "Mão na massa, montar e testar.", "pedagogica", "FabLabs", "#c2410c", "#fb923c", "#fff7ed", "#ffffff", "#431407", tool_icons=True),
    "biblioteca_arcana":   _a("Biblioteca Arcana", "Saber como poder mágico.", "pedagogica", "Harry Potter (analógico)", "#581c87", "#9333ea", "#faf5ff", "#f3e8ff", "#3b0764", font="Georgia, serif"),
    "estacao_espacial":    _a("Estação Espacial", "Missão orbital de aprendizagem.", "pedagogica", "Space Station", "#0f172a", "#38bdf8", "#020617", "#1e293b", "#e0f2fe", starfield=True),
    "reino_dos_numeros":   _a("Reino dos Números", "Matemática como reino encantado.", "pedagogica", "Prime Climb", "#be185d", "#f472b6", "#fdf2f8", "#ffffff", "#500724", math_motifs=True),
}


# --------------------------------------------------------------------------- #
# Tipos de nó do editor de fluxo BPMN
# --------------------------------------------------------------------------- #
FLOW_NODE_TYPES: Dict[str, Dict[str, Any]] = {
    "start":    {"name": "Início",            "shape": "circle",  "desc": "Evento de início da partida (setup)."},
    "end":      {"name": "Fim",               "shape": "circle_bold", "desc": "Fim da partida (condição de vitória atingida)."},
    "phase":    {"name": "Fase",              "shape": "rect",    "desc": "Fase do turno; vincule blocos de mecânica."},
    "task":     {"name": "Ação do Jogador",   "shape": "rect",    "desc": "Ação concreta executada pelo jogador."},
    "gateway":  {"name": "Decisão (XOR)",     "shape": "diamond", "desc": "Desvio condicional do fluxo (sim/não, escolha)."},
    "parallel": {"name": "Paralelo (AND)",    "shape": "diamond_plus", "desc": "Ramos simultâneos (todos os jogadores agem)."},
    "loop":     {"name": "Laço de Turnos",    "shape": "rect_loop", "desc": "Repetição: próximo jogador, próxima rodada."},
    "event":    {"name": "Evento",            "shape": "circle_mid", "desc": "Evento intermediário (carta de evento, gatilho)."},
    "timer":    {"name": "Temporizador",      "shape": "circle_clock", "desc": "Limite de tempo de fase/rodada."},
    "score":    {"name": "Pontuação",         "shape": "rect_score", "desc": "Momento de cômputo de pontos."},
}


def get_catalogs() -> Dict[str, Any]:
    """Retorna os três catálogos + tipos de nó, prontos para serializar."""
    return {
        "mechanics": MECHANICS_BLOCKS,
        "dynamics": DYNAMICS_BLOCKS,
        "aesthetics": AESTHETICS_BLOCKS,
        "flow_node_types": FLOW_NODE_TYPES,
        "counts": {
            "mechanics": len(MECHANICS_BLOCKS),
            "dynamics": len(DYNAMICS_BLOCKS),
            "aesthetics": len(AESTHETICS_BLOCKS),
        },
    }
