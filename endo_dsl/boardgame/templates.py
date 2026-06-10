"""Templates de DSL para arcátipos de jogos de tabuleiro educacionais.

Cada template gera uma string DSL válida para o dialeto ``boardgame``
a partir de um dicionário de contexto pedagógico, servindo como ponto
de partida para o GDC canvas.

Context dict esperado:
    title          : str  — título do jogo
    domain         : str  — área do conhecimento (ex.: "Matemática")
    topic          : str  — tópico específico (ex.: "frações")
    bloom_target   : str  — nível de Bloom alvo (pt ou en)
    age_range      : str  — faixa etária (ex.: "10-11")
    players        : str  — faixa de jogadores (ex.: "2-4")
    duration       : int  — duração em minutos
    objective_text : str  — texto do objetivo pedagógico
"""

from __future__ import annotations

from typing import Any, Dict


# ---------------------------------------------------------------------------
# Utilitários de geração
# ---------------------------------------------------------------------------

def _ctx(context: Dict[str, Any], key: str, default: Any = "") -> Any:
    return context.get(key, default)


def _q(s: str) -> str:
    """Envolve em aspas duplas, escapando aspas internas."""
    return '"' + str(s).replace('"', '\\"') + '"'


def _bloom_for_mechanic(bloom_target: str) -> str:
    """Normaliza o nível de Bloom para uso no DSL."""
    mapping = {
        "lembrar": "Lembrar", "remember": "Lembrar",
        "compreender": "Compreender", "understand": "Compreender",
        "aplicar": "Aplicar", "apply": "Aplicar",
        "analisar": "Analisar", "analyze": "Analisar", "analyse": "Analisar",
        "avaliar": "Avaliar", "evaluate": "Avaliar",
        "criar": "Criar", "create": "Criar",
    }
    return mapping.get(bloom_target.lower(), "Aplicar")


# ---------------------------------------------------------------------------
# Template: trilha
# ---------------------------------------------------------------------------

def _template_trilha(ctx: Dict[str, Any]) -> str:
    title = _ctx(ctx, "title", "Trilha Educativa")
    domain = _ctx(ctx, "domain", "Geral")
    topic = _ctx(ctx, "topic", "conteúdo")
    bloom = _bloom_for_mechanic(_ctx(ctx, "bloom_target", "Aplicar"))
    age = _ctx(ctx, "age_range", "8-12")
    players = _ctx(ctx, "players", "2-4")
    duration = int(_ctx(ctx, "duration", 30))
    obj_text = _ctx(ctx, "objective_text", f"Praticar {topic}")

    return f"""\
boardgame {_q(title)} {{

  metadata {{
    domain: {_q(domain)}
    topic: {_q(topic)}
    age_range: {_q(age)}
    players: {_q(players)}
    duration: {duration}
    template: "trilha"
  }}

  objective OBJ_principal {{
    description: {_q(obj_text)}
    bloom: {bloom}
  }}

  mechanic trilha_principal {{
    type: quiz
    bloom: {bloom}
    addresses: OBJ_principal
    description: {_q(f"Trilha linear com perguntas de {topic}")}
    params {{
      track_length: 40
      dice_count: 1
      dice_sides: 6
    }}
  }}

  mechanic perguntas {{
    type: quiz
    bloom: {bloom}
    addresses: OBJ_principal
    description: {_q(f"Cartas de pergunta sobre {topic}")}
    params {{
      question_count: 30
      time_limit: 30
      feedback_on_error: true
    }}
  }}

  loop turno_trilha {{
    bloom: {bloom}
    description: {_q("Rolar dado, mover peça, responder pergunta da casa")}
    steps {{
      rolar_dado -> mover_peca
      mover_peca -> verificar_casa
      verificar_casa -> responder_pergunta
      responder_pergunta -> proxima_vez
      proxima_vez -> rolar_dado
    }}
  }}

  board {{
    type: "track"
    spaces: 40
    space inicio {{
      position: 0
      type: "start"
      label: {_q("Início")}
      color: "green"
    }}
    space fim {{
      position: 39
      type: "end"
      label: {_q("Chegada!")}
      color: "gold"
    }}
    space pergunta_5 {{
      position: 5
      type: "special"
      label: {_q("Pergunta!")}
      color: "blue"
      trigger: "quiz_challenge"
    }}
    space pergunta_10 {{
      position: 10
      type: "special"
      label: {_q("Pergunta!")}
      color: "blue"
      trigger: "quiz_challenge"
    }}
    space bonus_15 {{
      position: 15
      type: "bonus"
      label: {_q("Avance 3")}
      color: "yellow"
    }}
    space penalty_20 {{
      position: 20
      type: "penalty"
      label: {_q("Volte 2")}
      color: "red"
    }}
    space pergunta_25 {{
      position: 25
      type: "special"
      label: {_q("Pergunta Difícil!")}
      color: "purple"
      trigger: "quiz_challenge"
    }}
    space pergunta_30 {{
      position: 30
      type: "special"
      label: {_q("Pergunta!")}
      color: "blue"
      trigger: "quiz_challenge"
    }}
    space bonus_35 {{
      position: 35
      type: "bonus"
      label: {_q("Avance 2")}
      color: "yellow"
    }}
  }}

  pieces {{
    piece peao {{
      name: {_q("Peão")}
      per_player: 1
      shared: false
      visual: "⬤"
    }}
  }}

  rules {{
    turn_order: clockwise
    win_condition: {_q("Primeiro a chegar na casa final vence")}
    dice: "1d6"
    players: {_q(players)}
    duration: {duration}
  }}

  deck perguntas_deck {{
    name: {_q(f"Perguntas de {topic}")}
    card p01 {{
      text: {_q(f"Pergunta 1 sobre {topic}")}
      effect: {_q("Avance 1 casa se acertar")}
      bloom: {bloom}
      category: {_q(topic)}
    }}
    card p02 {{
      text: {_q(f"Pergunta 2 sobre {topic}")}
      effect: {_q("Avance 1 casa se acertar")}
      bloom: {bloom}
      category: {_q(topic)}
    }}
    card p03 {{
      text: {_q(f"Pergunta difícil sobre {topic}")}
      effect: {_q("Avance 2 casas se acertar")}
      bloom: Analisar
      category: {_q(topic)}
    }}
  }}

}}
"""


# ---------------------------------------------------------------------------
# Template: quiz_battle
# ---------------------------------------------------------------------------

def _template_quiz_battle(ctx: Dict[str, Any]) -> str:
    title = _ctx(ctx, "title", "Batalha de Quiz")
    domain = _ctx(ctx, "domain", "Geral")
    topic = _ctx(ctx, "topic", "conteúdo")
    bloom = _bloom_for_mechanic(_ctx(ctx, "bloom_target", "Compreender"))
    age = _ctx(ctx, "age_range", "10-14")
    players = _ctx(ctx, "players", "2-6")
    duration = int(_ctx(ctx, "duration", 30))
    obj_text = _ctx(ctx, "objective_text", f"Avaliar conhecimento em {topic}")

    return f"""\
boardgame {_q(title)} {{

  metadata {{
    domain: {_q(domain)}
    topic: {_q(topic)}
    age_range: {_q(age)}
    players: {_q(players)}
    duration: {duration}
    template: "quiz_battle"
  }}

  objective OBJ_avaliar {{
    description: {_q(obj_text)}
    bloom: {bloom}
  }}

  mechanic quiz_perguntas {{
    type: quiz
    bloom: {bloom}
    addresses: OBJ_avaliar
    description: {_q(f"Perguntas de múltipla escolha sobre {topic}")}
    params {{
      question_count: 40
      choices_count: 4
      time_limit: 30
      feedback_on_error: true
    }}
  }}

  mechanic pontuacao {{
    type: quiz
    bloom: {bloom}
    addresses: OBJ_avaliar
    description: {_q("Sistema de pontuação por acertos e velocidade")}
    params {{
      points_per_correct: 10
      speed_bonus: true
    }}
  }}

  loop rodada_quiz {{
    bloom: {bloom}
    description: {_q("Ler pergunta, dar resposta, pontuar ou eliminar")}
    steps {{
      distribuir_carta -> ler_pergunta
      ler_pergunta -> responder
      responder -> verificar_resposta
      verificar_resposta -> pontuar
      pontuar -> verificar_eliminacao
      verificar_eliminacao -> proxima_rodada
      proxima_rodada -> distribuir_carta
    }}
  }}

  board {{
    type: "cards_only"
  }}

  rules {{
    turn_order: clockwise
    win_condition: {_q("Jogador com mais pontos após todas as rodadas vence")}
    players: {_q(players)}
    duration: {duration}
  }}

  deck perguntas_batalha {{
    name: {_q(f"Batalha de {topic}")}
    card q01 {{
      text: {_q(f"Pergunta fácil sobre {topic}")}
      effect: {_q("+10 pontos")}
      bloom: Lembrar
      category: {_q(topic)}
    }}
    card q02 {{
      text: {_q(f"Pergunta média sobre {topic}")}
      effect: {_q("+20 pontos")}
      bloom: Compreender
      category: {_q(topic)}
    }}
    card q03 {{
      text: {_q(f"Pergunta difícil sobre {topic}")}
      effect: {_q("+30 pontos")}
      bloom: {bloom}
      category: {_q(topic)}
    }}
  }}

}}
"""


# ---------------------------------------------------------------------------
# Template: memory_match
# ---------------------------------------------------------------------------

def _template_memory_match(ctx: Dict[str, Any]) -> str:
    title = _ctx(ctx, "title", "Jogo da Memória Temático")
    domain = _ctx(ctx, "domain", "Geral")
    topic = _ctx(ctx, "topic", "conteúdo")
    bloom = "Lembrar"
    age = _ctx(ctx, "age_range", "6-10")
    players = _ctx(ctx, "players", "2-4")
    duration = int(_ctx(ctx, "duration", 20))
    obj_text = _ctx(ctx, "objective_text", f"Memorizar conceitos de {topic}")

    return f"""\
boardgame {_q(title)} {{

  metadata {{
    domain: {_q(domain)}
    topic: {_q(topic)}
    age_range: {_q(age)}
    players: {_q(players)}
    duration: {duration}
    template: "memory_match"
  }}

  objective OBJ_memorizar {{
    description: {_q(obj_text)}
    bloom: {bloom}
  }}

  mechanic memoria {{
    type: matching
    bloom: {bloom}
    addresses: OBJ_memorizar
    description: {_q(f"Encontrar pares de cartas temáticas de {topic}")}
    params {{
      card_pairs: 20
      flips_per_turn: 2
      face_down_start: true
    }}
  }}

  loop turno_memoria {{
    bloom: {bloom}
    description: {_q("Virar duas cartas, verificar par, recolher ou virar de volta")}
    steps {{
      virar_carta_1 -> virar_carta_2
      virar_carta_2 -> verificar_par
      verificar_par -> recolher_par
      recolher_par -> proxima_vez
      proxima_vez -> virar_carta_1
    }}
  }}

  board {{
    type: "cards_only"
    rows: 4
    cols: 10
  }}

  rules {{
    turn_order: clockwise
    win_condition: {_q("Jogador com mais pares vence")}
    players: {_q(players)}
    duration: {duration}
  }}

}}
"""


# ---------------------------------------------------------------------------
# Template: word_race
# ---------------------------------------------------------------------------

def _template_word_race(ctx: Dict[str, Any]) -> str:
    title = _ctx(ctx, "title", "Corrida de Palavras")
    domain = _ctx(ctx, "domain", "Língua Portuguesa")
    topic = _ctx(ctx, "topic", "vocabulário")
    bloom = _bloom_for_mechanic(_ctx(ctx, "bloom_target", "Aplicar"))
    age = _ctx(ctx, "age_range", "9-14")
    players = _ctx(ctx, "players", "2-4")
    duration = int(_ctx(ctx, "duration", 45))
    obj_text = _ctx(ctx, "objective_text", f"Expandir vocabulário de {topic}")

    return f"""\
boardgame {_q(title)} {{

  metadata {{
    domain: {_q(domain)}
    topic: {_q(topic)}
    age_range: {_q(age)}
    players: {_q(players)}
    duration: {duration}
    template: "word_race"
  }}

  objective OBJ_vocabulario {{
    description: {_q(obj_text)}
    bloom: {bloom}
  }}

  mechanic formacao_palavras {{
    type: puzzle
    bloom: {bloom}
    addresses: OBJ_vocabulario
    description: {_q("Formar palavras com letras disponíveis no tabuleiro")}
    params {{
      min_word_length: 3
      dictionary: "pt_BR"
      bonus_tiles: true
    }}
  }}

  loop turno_palavras {{
    bloom: {bloom}
    description: {_q("Pegar letras, formar palavra, pontuar, repor letras")}
    steps {{
      pegar_letras -> formar_palavra
      formar_palavra -> validar_palavra
      validar_palavra -> pontuar
      pontuar -> repor_letras
      repor_letras -> pegar_letras
    }}
  }}

  board {{
    type: "grid"
    rows: 15
    cols: 15
  }}

  rules {{
    turn_order: clockwise
    win_condition: {_q("Maior pontuação quando acabarem as letras")}
    players: {_q(players)}
    duration: {duration}
  }}

}}
"""


# ---------------------------------------------------------------------------
# Template: strategy_grid
# ---------------------------------------------------------------------------

def _template_strategy_grid(ctx: Dict[str, Any]) -> str:
    title = _ctx(ctx, "title", "Grade Estratégica")
    domain = _ctx(ctx, "domain", "Raciocínio Lógico")
    topic = _ctx(ctx, "topic", "estratégia")
    bloom = _bloom_for_mechanic(_ctx(ctx, "bloom_target", "Analisar"))
    age = _ctx(ctx, "age_range", "10-14")
    players = "2"
    duration = int(_ctx(ctx, "duration", 30))
    obj_text = _ctx(ctx, "objective_text", f"Desenvolver raciocínio estratégico com {topic}")

    return f"""\
boardgame {_q(title)} {{

  metadata {{
    domain: {_q(domain)}
    topic: {_q(topic)}
    age_range: {_q(age)}
    players: {_q(players)}
    duration: {duration}
    template: "strategy_grid"
  }}

  objective OBJ_estrategia {{
    description: {_q(obj_text)}
    bloom: {bloom}
  }}

  mechanic movimento_grade {{
    type: strategy
    bloom: {bloom}
    addresses: OBJ_estrategia
    description: {_q("Mover peças em grade 8x8 com regras direcionais")}
    params {{
      grid_rows: 8
      grid_cols: 8
      move_directions: "all"
    }}
  }}

  loop turno_estrategico {{
    bloom: {bloom}
    description: {_q("Analisar posição, escolher peça, executar movimento")}
    steps {{
      analisar_posicao -> escolher_peca
      escolher_peca -> executar_movimento
      executar_movimento -> verificar_captura
      verificar_captura -> analisar_posicao
    }}
  }}

  board {{
    type: "grid"
    rows: 8
    cols: 8
    space s00 {{
      position: 0
      type: "normal"
      color: "white"
    }}
  }}

  pieces {{
    piece peca_branca {{
      name: {_q("Peça Branca")}
      per_player: 12
      shared: false
      visual: "○"
      move {{
        direction: "diagonal"
        steps: 1
      }}
    }}
    piece peca_preta {{
      name: {_q("Peça Preta")}
      per_player: 12
      shared: false
      visual: "●"
      move {{
        direction: "diagonal"
        steps: 1
      }}
    }}
  }}

  rules {{
    turn_order: clockwise
    win_condition: {_q("Eliminar todas as peças do adversário")}
    players: {_q(players)}
    duration: {duration}
  }}

}}
"""


# ---------------------------------------------------------------------------
# Template: cooperative_quest
# ---------------------------------------------------------------------------

def _template_cooperative_quest(ctx: Dict[str, Any]) -> str:
    title = _ctx(ctx, "title", "Missão Cooperativa")
    domain = _ctx(ctx, "domain", "Ciências")
    topic = _ctx(ctx, "topic", "ecossistemas")
    bloom = _bloom_for_mechanic(_ctx(ctx, "bloom_target", "Avaliar"))
    age = _ctx(ctx, "age_range", "11-14")
    players = _ctx(ctx, "players", "2-5")
    duration = int(_ctx(ctx, "duration", 60))
    obj_text = _ctx(ctx, "objective_text", f"Resolver desafios cooperativos sobre {topic}")

    return f"""\
boardgame {_q(title)} {{

  metadata {{
    domain: {_q(domain)}
    topic: {_q(topic)}
    age_range: {_q(age)}
    players: {_q(players)}
    duration: {duration}
    template: "cooperative_quest"
  }}

  objective OBJ_cooperar {{
    description: {_q(obj_text)}
    bloom: {bloom}
  }}

  mechanic cooperacao {{
    type: role_play
    bloom: {bloom}
    addresses: OBJ_cooperar
    description: {_q("Papéis especializados colaboram para resolver a missão")}
    params {{
      roles: true
      threat_level: "normal"
      hidden_info: false
    }}
  }}

  mechanic recursos {{
    type: strategy
    bloom: {bloom}
    addresses: OBJ_cooperar
    description: {_q("Gerir recursos do grupo para avançar na missão")}
    params {{
      resource_types: "acao, conhecimento, energia"
      storage_limit: 5
    }}
  }}

  loop rodada_cooperativa {{
    bloom: {bloom}
    description: {_q("Planejar em grupo, executar ações, enfrentar evento")}
    steps {{
      planejar -> alocar_trabalhadores
      alocar_trabalhadores -> executar_acoes
      executar_acoes -> evento_do_jogo
      evento_do_jogo -> verificar_vitoria
      verificar_vitoria -> planejar
    }}
  }}

  board {{
    type: "map"
    rows: 6
    cols: 8
  }}

  rules {{
    turn_order: simultaneous
    win_condition: {_q("O grupo completa todos os objetivos da missão")}
    players: {_q(players)}
    duration: {duration}
  }}

}}
"""


# ---------------------------------------------------------------------------
# Template: auction_economy
# ---------------------------------------------------------------------------

def _template_auction_economy(ctx: Dict[str, Any]) -> str:
    title = _ctx(ctx, "title", "Economia e Leilão")
    domain = _ctx(ctx, "domain", "Matemática Financeira")
    topic = _ctx(ctx, "topic", "economia")
    bloom = _bloom_for_mechanic(_ctx(ctx, "bloom_target", "Analisar"))
    age = _ctx(ctx, "age_range", "12-16")
    players = _ctx(ctx, "players", "3-6")
    duration = int(_ctx(ctx, "duration", 60))
    obj_text = _ctx(ctx, "objective_text", f"Compreender conceitos de {topic}")

    return f"""\
boardgame {_q(title)} {{

  metadata {{
    domain: {_q(domain)}
    topic: {_q(topic)}
    age_range: {_q(age)}
    players: {_q(players)}
    duration: {duration}
    template: "auction_economy"
  }}

  objective OBJ_economia {{
    description: {_q(obj_text)}
    bloom: {bloom}
  }}

  mechanic leilao {{
    type: decision
    bloom: {bloom}
    addresses: OBJ_economia
    description: {_q("Lances abertos por propriedades e recursos")}
    params {{
      starting_money: 1500
      auction_type: "open"
      minimum_bid: 10
    }}
  }}

  mechanic gestao_recursos {{
    type: strategy
    bloom: {bloom}
    addresses: OBJ_economia
    description: {_q("Administrar dinheiro e propriedades ao longo do jogo")}
    params {{
      resource_types: "dinheiro, propriedades"
      production_per_turn: 200
    }}
  }}

  loop rodada_economica {{
    bloom: {bloom}
    description: {_q("Rolar dado, mover, pagar ou comprar, leiloar")}
    steps {{
      rolar_dado -> mover_peao
      mover_peao -> resolver_casa
      resolver_casa -> leiloar_se_necessario
      leiloar_se_necessario -> proxima_vez
      proxima_vez -> rolar_dado
    }}
  }}

  board {{
    type: "track"
    spaces: 40
    space partida {{
      position: 0
      type: "start"
      label: {_q("Partida")}
      color: "green"
    }}
  }}

  rules {{
    turn_order: clockwise
    win_condition: {_q("Último jogador solvente vence")}
    players: {_q(players)}
    duration: {duration}
  }}

}}
"""


# ---------------------------------------------------------------------------
# Template: deduction_mystery
# ---------------------------------------------------------------------------

def _template_deduction_mystery(ctx: Dict[str, Any]) -> str:
    title = _ctx(ctx, "title", "Mistério e Dedução")
    domain = _ctx(ctx, "domain", "Raciocínio Lógico")
    topic = _ctx(ctx, "topic", "lógica dedutiva")
    bloom = _bloom_for_mechanic(_ctx(ctx, "bloom_target", "Analisar"))
    age = _ctx(ctx, "age_range", "11-15")
    players = _ctx(ctx, "players", "3-6")
    duration = int(_ctx(ctx, "duration", 45))
    obj_text = _ctx(ctx, "objective_text", f"Desenvolver raciocínio dedutivo com {topic}")

    return f"""\
boardgame {_q(title)} {{

  metadata {{
    domain: {_q(domain)}
    topic: {_q(topic)}
    age_range: {_q(age)}
    players: {_q(players)}
    duration: {duration}
    template: "deduction_mystery"
  }}

  objective OBJ_deducao {{
    description: {_q(obj_text)}
    bloom: {bloom}
  }}

  mechanic deducao {{
    type: decision
    bloom: {bloom}
    addresses: OBJ_deducao
    description: {_q("Coletar pistas e eliminar suspeitos por lógica")}
    params {{
      clue_types: 3
      solution_categories: 3
      note_sheet: true
    }}
  }}

  mechanic deducao_social {{
    type: debate
    bloom: {bloom}
    addresses: OBJ_deducao
    description: {_q("Observar comportamento dos outros jogadores")}
    params {{
      roles: true
      night_phase: false
    }}
  }}

  loop investigacao {{
    bloom: {bloom}
    description: {_q("Mover, coletar pista, questionar suspeito, anotar")}
    steps {{
      mover_detetive -> coletar_pista
      coletar_pista -> questionar_suspeito
      questionar_suspeito -> anotar_deducao
      anotar_deducao -> acusar_ou_continuar
      acusar_ou_continuar -> mover_detetive
    }}
  }}

  board {{
    type: "map"
    rows: 5
    cols: 6
  }}

  rules {{
    turn_order: clockwise
    win_condition: {_q("Acusar corretamente o suspeito, arma e local")}
    players: {_q(players)}
    duration: {duration}
  }}

}}
"""


# ---------------------------------------------------------------------------
# Dispatcher público
# ---------------------------------------------------------------------------

_TEMPLATE_FUNCTIONS = {
    "trilha": _template_trilha,
    "quiz_battle": _template_quiz_battle,
    "memory_match": _template_memory_match,
    "word_race": _template_word_race,
    "strategy_grid": _template_strategy_grid,
    "cooperative_quest": _template_cooperative_quest,
    "auction_economy": _template_auction_economy,
    "deduction_mystery": _template_deduction_mystery,
}

AVAILABLE_TEMPLATES = list(_TEMPLATE_FUNCTIONS.keys())


def generate_template(template_id: str, context: Dict[str, Any]) -> str:
    """Gera uma string DSL válida para o template e contexto fornecidos.

    Args:
        template_id: Identificador do template (ver AVAILABLE_TEMPLATES).
        context: Dicionário com metadados pedagógicos (title, domain, topic, etc.).

    Returns:
        String DSL válida para o dialeto ``boardgame``.

    Raises:
        ValueError: Se template_id não for reconhecido.
    """
    fn = _TEMPLATE_FUNCTIONS.get(template_id)
    if fn is None:
        available = ", ".join(sorted(_TEMPLATE_FUNCTIONS))
        raise ValueError(
            f"Template desconhecido: {template_id!r}. "
            f"Templates disponíveis: {available}"
        )
    return fn(context)
