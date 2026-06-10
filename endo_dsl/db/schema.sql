-- ====================================================================== --
-- Esquema do banco de dados SQLite da plataforma Endo-DSL.
--
-- Cobre a persistência exigida pelos requisitos funcionais:
--   Biblioteca de componentes ......... RF07–RF12
--   Pipeline multi-agente (logs) ...... RF17, RF18
--   Sessões / especificações / protótipos (jornada, RF19, RF21, RF23)
--   Avaliação e comparação ............ RF24, RF25, RF26
--
-- Todas as datas são ISO-8601 (texto). Campos *_json guardam JSON serializado.
-- ====================================================================== --

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------- --
-- Módulo 2 — Biblioteca de Componentes Reutilizáveis
-- ---------------------------------------------------------------------- --

-- RF07 / RF12 — componente reutilizável; status distingue canônico x experimental.
CREATE TABLE IF NOT EXISTS components (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    key             TEXT NOT NULL UNIQUE,            -- slug estável
    name            TEXT NOT NULL,
    current_version INTEGER NOT NULL DEFAULT 1,
    dsl_signature   TEXT NOT NULL,                   -- assinatura formal na DSL (RF07)
    bloom_level     TEXT NOT NULL,                   -- nível de Bloom endereçado (RF07)
    mechanic_type   TEXT NOT NULL,                   -- tipo de mecânica endógena (RF07)
    description     TEXT NOT NULL,                   -- descrição em linguagem natural (RF07)
    params_json     TEXT NOT NULL DEFAULT '{}',      -- parâmetros configuráveis (RF07)
    domain          TEXT,                            -- área de conhecimento (RF09)
    context         TEXT,                            -- formal | informal (RF09)
    age_range       TEXT,                            -- faixa etária (RF09)
    modality        TEXT,                            -- modalidade (RF09)
    status          TEXT NOT NULL DEFAULT 'experimental'
                       CHECK (status IN ('canonical','experimental','rejected')),
    author          TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_components_bloom  ON components(bloom_level);
CREATE INDEX IF NOT EXISTS idx_components_mech   ON components(mechanic_type);
CREATE INDEX IF NOT EXISTS idx_components_status ON components(status);

-- RF10 — versionamento: histórico completo de cada versão de um componente.
CREATE TABLE IF NOT EXISTS component_versions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id  INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    version       INTEGER NOT NULL,
    dsl_signature TEXT NOT NULL,
    params_json   TEXT NOT NULL DEFAULT '{}',
    description   TEXT NOT NULL,
    change_note   TEXT,
    created_at    TEXT NOT NULL,
    UNIQUE (component_id, version)
);

-- RF08 — enriquecimento opcional (estudos de caso, avaliações de especialistas, refs).
CREATE TABLE IF NOT EXISTS component_enrichment (
    component_id        INTEGER PRIMARY KEY REFERENCES components(id) ON DELETE CASCADE,
    case_studies_json   TEXT NOT NULL DEFAULT '[]',
    expert_eval_json    TEXT NOT NULL DEFAULT '[]',
    references_json     TEXT NOT NULL DEFAULT '[]',
    updated_at          TEXT NOT NULL
);

-- RF11 — avaliações atribuídas pelos usuários a um componente.
CREATE TABLE IF NOT EXISTS component_ratings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id  INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    evaluator     TEXT,
    score         REAL NOT NULL CHECK (score >= 0 AND score <= 5),
    comment       TEXT,
    created_at    TEXT NOT NULL
);

-- RF11 — métricas de uso: cada instanciação do componente em uma geração/protótipo.
CREATE TABLE IF NOT EXISTS component_usage (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id      INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    component_version INTEGER,
    session_id        INTEGER REFERENCES design_sessions(id) ON DELETE SET NULL,
    prototype_id      INTEGER REFERENCES prototypes(id) ON DELETE SET NULL,
    compiled_ok       INTEGER,    -- 1/0/NULL (taxa de sucesso na compilação)
    created_at        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_usage_component ON component_usage(component_id);

-- RF12 / jornada secundária — trilha de curadoria (submissão, aprovação, rejeição).
CREATE TABLE IF NOT EXISTS curation_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id  INTEGER NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    action        TEXT NOT NULL CHECK (action IN
                     ('submit','approve','reject','request_changes')),
    curator       TEXT,
    justification TEXT,
    created_at    TEXT NOT NULL
);

-- ---------------------------------------------------------------------- --
-- Jornada — Sessões de design
-- ---------------------------------------------------------------------- --

-- RF13 — entrada estruturada do contexto educacional (Fase 1 da jornada).
CREATE TABLE IF NOT EXISTS design_sessions (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    name                 TEXT NOT NULL,
    domain               TEXT,                    -- área de conhecimento
    learning_objective   TEXT,                    -- objetivo de aprendizagem
    bloom_target         TEXT,                    -- nível cognitivo desejado
    learner_profile_json TEXT NOT NULL DEFAULT '{}',  -- faixa etária, escolaridade, contexto
    constraints_json     TEXT NOT NULL DEFAULT '{}',  -- tempo, plataforma, etc.
    status               TEXT NOT NULL DEFAULT 'open',
    created_at           TEXT NOT NULL
);

-- ---------------------------------------------------------------------- --
-- Módulo 3 — Pipeline Multi-Agente (logs e métricas)
-- ---------------------------------------------------------------------- --

-- RF17 — registro de TODA tentativa de geração (válida ou inválida).
CREATE TABLE IF NOT EXISTS generation_attempts (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id             INTEGER REFERENCES design_sessions(id) ON DELETE CASCADE,
    attempt_no             INTEGER NOT NULL DEFAULT 1,
    prompt                 TEXT,                  -- prompt utilizado
    selected_components_json TEXT NOT NULL DEFAULT '[]',  -- componentes selecionados
    generated_dsl          TEXT,
    syntactic_ok           INTEGER,
    semantic_ok            INTEGER,
    pedagogical_ok         INTEGER,
    params_ok              INTEGER,               -- consistência com parâmetros de entrada
    valid                  INTEGER NOT NULL DEFAULT 0,
    errors_json            TEXT NOT NULL DEFAULT '[]',  -- erros de validação
    backend                TEXT,                  -- backend LLM utilizado
    created_at             TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts_session ON generation_attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_attempts_valid   ON generation_attempts(valid);

-- ---------------------------------------------------------------------- --
-- Módulo 4 — Especificações e Protótipos
-- ---------------------------------------------------------------------- --

CREATE TABLE IF NOT EXISTS specifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER REFERENCES design_sessions(id) ON DELETE SET NULL,
    title       TEXT,
    dsl_source  TEXT NOT NULL,
    origin      TEXT NOT NULL DEFAULT 'manual'
                   CHECK (origin IN ('manual','auto','hybrid')),
    parsed_ok   INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);

-- RF19 / RF21 / RF23 — protótipo compilado e seus metadados rastreáveis.
CREATE TABLE IF NOT EXISTS prototypes (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    spec_id           INTEGER REFERENCES specifications(id) ON DELETE SET NULL,
    session_id        INTEGER REFERENCES design_sessions(id) ON DELETE SET NULL,
    title             TEXT,
    html_path         TEXT,                       -- caminho do protótipo HTML5
    traceability_json TEXT NOT NULL DEFAULT '{}', -- objetivos -> mecânicas (RF23)
    bloom_levels_json TEXT NOT NULL DEFAULT '[]', -- níveis preservados (RF21)
    origin            TEXT NOT NULL DEFAULT 'manual'
                         CHECK (origin IN ('manual','auto','hybrid')),
    compiled_ok       INTEGER NOT NULL DEFAULT 0,
    created_at        TEXT NOT NULL
);

-- ---------------------------------------------------------------------- --
-- Módulo 5 — Avaliação e Comparação
-- ---------------------------------------------------------------------- --

-- RF24 / RF25 — registro estruturado de avaliações de qualidade pedagógica.
CREATE TABLE IF NOT EXISTS evaluations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    prototype_id        INTEGER REFERENCES prototypes(id) ON DELETE CASCADE,
    origin              TEXT NOT NULL DEFAULT 'auto'   -- origem do protótipo avaliado
                           CHECK (origin IN ('manual','auto','hybrid')),
    evaluator           TEXT,
    bloom_level         TEXT,                          -- nível cognitivo declarado
    domain              TEXT,
    components_used_json TEXT NOT NULL DEFAULT '[]',   -- componentes utilizados
    scores_json         TEXT NOT NULL DEFAULT '{}',    -- pontuações por dimensão
    comments            TEXT,
    instrument_version  TEXT,
    created_at          TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_eval_prototype ON evaluations(prototype_id);
CREATE INDEX IF NOT EXISTS idx_eval_origin    ON evaluations(origin);
