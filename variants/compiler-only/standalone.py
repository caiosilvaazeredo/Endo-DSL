#!/usr/bin/env python3
"""Endo-DSL compiler — distribuição STANDALONE (arquivo único, sem banco de dados).

GERADO AUTOMATICAMENTE por variants/compiler-only/bundle.py — NÃO edite à mão.

Compila uma especificação .endo em um protótipo HTML5 jogável e autocontido,
usando apenas a biblioteca padrão do Python (>=3.10). Sem SQLite, sem servidor,
sem dependências externas.

Uso:
    python standalone.py entrada.endo -o saida.html
    python standalone.py entrada.endo --trace
    cat entrada.endo | python standalone.py -
"""

from __future__ import annotations

import sys
import types

# --------------------------------------------------------------------------- #
# Registra os módulos do compilador embutidos em sys.modules, na ordem de
# dependência, para que os ``import endo_dsl...`` internos resolvam sem o pacote
# instalado. Cada bloco abaixo é o código-fonte literal de um módulo real.
# --------------------------------------------------------------------------- #
def _shell(name: str) -> None:
    """Cria um objeto-pacote vazio (com __path__) registrado em sys.modules."""
    mod = types.ModuleType(name)
    mod.__file__ = "<bundled:%s>" % name
    mod.__path__ = []  # marca como pacote
    sys.modules[name] = mod
    if "." in name:
        parent, _, child = name.rpartition(".")
        setattr(sys.modules[parent], child, mod)


def _run(name: str, source: str) -> None:
    """Executa o código-fonte de um módulo dentro do seu namespace.

    Para pacotes, o shell já existe em sys.modules; para folhas, cria o módulo.
    """
    mod = sys.modules.get(name)
    if mod is None:
        mod = types.ModuleType(name)
        mod.__file__ = "<bundled:%s>" % name
        sys.modules[name] = mod
        if "." in name:
            parent, _, child = name.rpartition(".")
            setattr(sys.modules[parent], child, mod)
    exec(compile(source, mod.__file__, "exec"), mod.__dict__)


# --- shells de pacote (criados antes da execução dos __init__) ---
_shell('endo_dsl')
_shell('endo_dsl.dsl')
_shell('endo_dsl.compiler')

# === __init__: endo_dsl (raiz: __version__) ===
_run('endo_dsl', r'''"""Endo-DSL — plataforma de design e geração automática de jogos educacionais endógenos.

Quatro subsistemas integrados:

* ``endo_dsl.dsl``        — Motor da DSL (gramática formal, parser e validadores).
* ``endo_dsl.library``    — Biblioteca de componentes reutilizáveis (SQLite).
* ``endo_dsl.agents``     — Pipeline multi-agente LLM (recuperação, geração, validação).
* ``endo_dsl.compiler``   — Compilador DSL -> protótipo HTML5 jogável.
* ``endo_dsl.evaluation`` — Instrumento de avaliação e relatórios comparativos.

Proposta de pesquisa — Doutorado PESC/COPPE/UFRJ.
Caio Azeredo | Orientador: Prof. Geraldo Bonorino Xexéo.
"""

__version__ = "1.1.0"
__all__ = ["__version__"]
''')

# === módulo: endo_dsl.dsl.bloom ===
_run('endo_dsl.dsl.bloom', r'''"""Taxonomia de Bloom como construto de primeira classe (RF02).

Os seis níveis cognitivos são modelados como um ``IntEnum`` ordenado, de forma que
operações de comparação (``<``, ``>=``) expressem progressão cognitiva diretamente.

Os nomes canônicos são em português (conforme a proposta), mas o parser aceita
aliases em inglês para interoperabilidade.
"""

from __future__ import annotations

import difflib
from enum import IntEnum
from typing import List, Optional


class Bloom(IntEnum):
    """Os seis níveis da Taxonomia de Bloom (revisada), ordenados por demanda cognitiva."""

    LEMBRAR = 1
    COMPREENDER = 2
    APLICAR = 3
    ANALISAR = 4
    AVALIAR = 5
    CRIAR = 6

    @property
    def pt(self) -> str:
        """Nome canônico em português."""
        return _PT_NAMES[self]

    @property
    def en(self) -> str:
        """Nome em inglês."""
        return _EN_NAMES[self]

    @property
    def slug(self) -> str:
        """Identificador estável para uso em código/JSON/HTML (ex.: ``analisar``)."""
        return self.name.lower()

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.pt


BLOOM_ORDER: List[Bloom] = list(Bloom)

_PT_NAMES = {
    Bloom.LEMBRAR: "Lembrar",
    Bloom.COMPREENDER: "Compreender",
    Bloom.APLICAR: "Aplicar",
    Bloom.ANALISAR: "Analisar",
    Bloom.AVALIAR: "Avaliar",
    Bloom.CRIAR: "Criar",
}

_EN_NAMES = {
    Bloom.LEMBRAR: "Remember",
    Bloom.COMPREENDER: "Understand",
    Bloom.APLICAR: "Apply",
    Bloom.ANALISAR: "Analyze",
    Bloom.AVALIAR: "Evaluate",
    Bloom.CRIAR: "Create",
}

# Mapa de aliases aceitos pelo parser -> nível. Inclui português, inglês e
# variações ortográficas comuns (com/sem acento, grafia britânica).
_ALIASES = {}
for _level in Bloom:
    for _name in (_level.pt, _level.en, _level.name):
        _ALIASES[_name.lower()] = _level
_ALIASES.update(
    {
        "analyse": Bloom.ANALISAR,  # grafia britânica
        "remember": Bloom.LEMBRAR,
        "lembrar": Bloom.LEMBRAR,
        "compreender": Bloom.COMPREENDER,
        "entender": Bloom.COMPREENDER,
        "aplicar": Bloom.APLICAR,
        "analisar": Bloom.ANALISAR,
        "avaliar": Bloom.AVALIAR,
        "criar": Bloom.CRIAR,
    }
)


def parse_bloom(token: str) -> Optional[Bloom]:
    """Resolve um token textual para um nível de Bloom, ou ``None`` se inválido."""
    if token is None:
        return None
    return _ALIASES.get(token.strip().lower())


def suggest_bloom(token: str, n: int = 1) -> List[str]:
    """Sugere nomes de níveis próximos a um token inválido (para mensagens de erro)."""
    canonical = [level.pt for level in Bloom] + [level.en for level in Bloom]
    return difflib.get_close_matches(token, canonical, n=n, cutoff=0.4)


def all_names() -> List[str]:
    """Lista de nomes canônicos (pt) para autocompletar/documentação."""
    return [level.pt for level in Bloom]
''')

# === módulo: endo_dsl.dsl.limits ===
_run('endo_dsl.dsl.limits', r'''"""Limites formais da gramática — RF06.

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
''')

# === módulo: endo_dsl.dsl.ast ===
_run('endo_dsl.dsl.ast', r'''"""Árvore de Sintaxe Abstrata (AST) da Endo-DSL.

Cada nó carrega informação de posição (linha/coluna) para que validadores e o
compilador possam reportar problemas com precisão (RF03, RF04, RF20).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from endo_dsl.dsl.bloom import Bloom


@dataclass
class Node:
    """Nó base com posição no código-fonte."""

    line: int = 0
    col: int = 0


@dataclass
class Params(Node):
    """Bloco ``params { ... }`` — parâmetros configuráveis (conteúdo, dificuldade, domínio)."""

    values: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)


@dataclass
class Metadata(Node):
    """Bloco ``metadata { ... }`` — contexto educacional do jogo."""

    values: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)


@dataclass
class Objective(Node):
    """Objetivo pedagógico declarado (RF01)."""

    name: str = ""
    description: str = ""
    bloom: Optional[Bloom] = None


@dataclass
class Mechanic(Node):
    """Mecânica de jogo endógena (RF01) vinculada a um nível de Bloom (RF02)."""

    name: str = ""
    type: str = ""
    bloom: Optional[Bloom] = None
    addresses: List[str] = field(default_factory=list)  # nomes de objetivos
    params: Params = field(default_factory=Params)
    description: str = ""
    # Referência opcional ao componente da biblioteca que originou a mecânica
    # (preenchida pelo pipeline de geração — RF15 / jornada Fase 3).
    source_component: Optional[str] = None


@dataclass
class Transition(Node):
    """Transição ``origem -> destino`` dentro de um loop de jogabilidade."""

    src: str = ""
    dst: str = ""


@dataclass
class GameplayLoop(Node):
    """Loop de jogabilidade (RF01)."""

    name: str = ""
    bloom: Optional[Bloom] = None
    description: str = ""
    transitions: List[Transition] = field(default_factory=list)


@dataclass
class Choice(Node):
    """Escolha do jogador em uma ramificação narrativa."""

    text: str = ""
    target: str = ""


@dataclass
class Branch(Node):
    """Ramo de uma narrativa (RF01)."""

    name: str = ""
    bloom: Optional[Bloom] = None
    text: str = ""
    description: str = ""
    choices: List[Choice] = field(default_factory=list)


@dataclass
class Narrative(Node):
    """Narrativa ramificada (RF01)."""

    name: str = ""
    branches: List[Branch] = field(default_factory=list)


@dataclass
class GameSpec(Node):
    """Raiz da AST: a especificação completa de um jogo educacional endógeno."""

    title: str = ""
    metadata: Metadata = field(default_factory=Metadata)
    objectives: List[Objective] = field(default_factory=list)
    mechanics: List[Mechanic] = field(default_factory=list)
    loops: List[GameplayLoop] = field(default_factory=list)
    narratives: List[Narrative] = field(default_factory=list)

    # ------------------------------------------------------------------ #
    # Conveniências de consulta usadas por validadores / compilador.
    # ------------------------------------------------------------------ #
    def objective(self, name: str) -> Optional[Objective]:
        return next((o for o in self.objectives if o.name == name), None)

    def mechanic(self, name: str) -> Optional[Mechanic]:
        return next((m for m in self.mechanics if m.name == name), None)

    @property
    def bloom_levels(self) -> List[Bloom]:
        """Conjunto ordenado de níveis de Bloom presentes na especificação."""
        levels = set()
        for o in self.objectives:
            if o.bloom is not None:
                levels.add(o.bloom)
        for m in self.mechanics:
            if m.bloom is not None:
                levels.add(m.bloom)
        return sorted(levels)

    def to_dict(self) -> Dict[str, Any]:
        """Serialização leve da AST (usada em metadados/rastreabilidade — RF21, RF23)."""
        return {
            "title": self.title,
            "metadata": dict(self.metadata.values),
            "objectives": [
                {
                    "name": o.name,
                    "description": o.description,
                    "bloom": o.bloom.pt if o.bloom else None,
                }
                for o in self.objectives
            ],
            "mechanics": [
                {
                    "name": m.name,
                    "type": m.type,
                    "bloom": m.bloom.pt if m.bloom else None,
                    "addresses": list(m.addresses),
                    "params": dict(m.params.values),
                    "description": m.description,
                    "source_component": m.source_component,
                }
                for m in self.mechanics
            ],
            "loops": [
                {
                    "name": l.name,
                    "bloom": l.bloom.pt if l.bloom else None,
                    "description": l.description,
                    "transitions": [
                        {"src": t.src, "dst": t.dst} for t in l.transitions
                    ],
                }
                for l in self.loops
            ],
            "narratives": [
                {
                    "name": n.name,
                    "branches": [
                        {
                            "name": b.name,
                            "bloom": b.bloom.pt if b.bloom else None,
                            "text": b.text,
                            "description": b.description,
                            "choices": [
                                {"text": c.text, "target": c.target} for c in b.choices
                            ],
                        }
                        for b in n.branches
                    ],
                }
                for n in self.narratives
            ],
        }
''')

# === módulo: endo_dsl.dsl.tokenizer ===
_run('endo_dsl.dsl.tokenizer', r'''"""Analisador léxico (tokenizer) da Endo-DSL.

Produz uma sequência de ``Token`` com linha/coluna preservadas, base para
mensagens de erro descritivas (RF03). Suporta comentários ``//`` e ``/* */``,
strings entre aspas duplas com escapes, números inteiros/decimais, ranges
(``10..11``), o operador de transição ``->`` e a pontuação estrutural.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Token:
    kind: str  # IDENT, STRING, NUMBER, RANGE, BOOL, LBRACE, RBRACE, COLON, COMMA, ARROW, EOF
    value: object
    line: int
    col: int
    raw: str = ""

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Token({self.kind}, {self.value!r}, {self.line}:{self.col})"


class LexError(Exception):
    """Erro léxico com posição. Convertido em ParseError descritivo pelo parser."""

    def __init__(self, message: str, line: int, col: int):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col


_PUNCT = {
    "{": "LBRACE",
    "}": "RBRACE",
    ":": "COLON",
    ",": "COMMA",
}


def tokenize(source: str) -> List[Token]:
    """Converte ``source`` em lista de tokens, terminando com um token EOF."""
    tokens: List[Token] = []
    i = 0
    line = 1
    col = 1
    n = len(source)

    def advance(count: int = 1) -> None:
        nonlocal i, line, col
        for _ in range(count):
            if i < n and source[i] == "\n":
                line += 1
                col = 1
            else:
                col += 1
            i += 1

    while i < n:
        ch = source[i]

        # Espaços em branco
        if ch in " \t\r\n":
            advance()
            continue

        # Comentário de linha //
        if ch == "/" and i + 1 < n and source[i + 1] == "/":
            while i < n and source[i] != "\n":
                advance()
            continue

        # Comentário de bloco /* ... */
        if ch == "/" and i + 1 < n and source[i + 1] == "*":
            start_line, start_col = line, col
            advance(2)
            closed = False
            while i < n:
                if source[i] == "*" and i + 1 < n and source[i + 1] == "/":
                    advance(2)
                    closed = True
                    break
                advance()
            if not closed:
                raise LexError("comentário de bloco '/* */' não fechado", start_line, start_col)
            continue

        # Operador de transição ->
        if ch == "-" and i + 1 < n and source[i + 1] == ">":
            tokens.append(Token("ARROW", "->", line, col, "->"))
            advance(2)
            continue

        # Pontuação simples
        if ch in _PUNCT:
            tokens.append(Token(_PUNCT[ch], ch, line, col, ch))
            advance()
            continue

        # String
        if ch == '"':
            start_line, start_col = line, col
            advance()  # consome aspa inicial
            buf = []
            closed = False
            while i < n:
                c = source[i]
                if c == "\\" and i + 1 < n:
                    nxt = source[i + 1]
                    buf.append({"n": "\n", "t": "\t", '"': '"', "\\": "\\"}.get(nxt, nxt))
                    advance(2)
                    continue
                if c == '"':
                    advance()
                    closed = True
                    break
                if c == "\n":
                    raise LexError("string não fechada antes do fim da linha", start_line, start_col)
                buf.append(c)
                advance()
            if not closed:
                raise LexError("string não fechada", start_line, start_col)
            tokens.append(Token("STRING", "".join(buf), start_line, start_col, '"' + "".join(buf) + '"'))
            continue

        # Número ou range (123, 1.5, 10..11)
        if ch.isdigit() or (ch == "-" and i + 1 < n and source[i + 1].isdigit()):
            start_line, start_col = line, col
            start = i
            if ch == "-":
                advance()
            while i < n and source[i].isdigit():
                advance()
            # Range 10..11
            if i + 1 < n and source[i] == "." and source[i + 1] == ".":
                advance(2)
                range_start = source[start:i - 2]
                rs2 = i
                while i < n and source[i].isdigit():
                    advance()
                range_end = source[rs2:i]
                tokens.append(
                    Token("RANGE", (int(range_start), int(range_end)), start_line, start_col,
                          source[start:i])
                )
                continue
            # Decimal
            is_float = False
            if i < n and source[i] == ".":
                is_float = True
                advance()
                while i < n and source[i].isdigit():
                    advance()
            raw = source[start:i]
            value: object = float(raw) if is_float else int(raw)
            tokens.append(Token("NUMBER", value, start_line, start_col, raw))
            continue

        # Identificador / palavra-chave / booleano
        if ch.isalpha() or ch == "_":
            start_line, start_col = line, col
            start = i
            while i < n and (source[i].isalnum() or source[i] in "_."):
                advance()
            raw = source[start:i]
            if raw in ("true", "false"):
                tokens.append(Token("BOOL", raw == "true", start_line, start_col, raw))
            else:
                tokens.append(Token("IDENT", raw, start_line, start_col, raw))
            continue

        # Caractere inesperado
        raise LexError(f"caractere inesperado {ch!r}", line, col)

    tokens.append(Token("EOF", None, line, col, ""))
    return tokens
''')

# === módulo: endo_dsl.dsl.semantic ===
_run('endo_dsl.dsl.semantic', r'''"""Validação semântica da Endo-DSL — RF04.

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
''')

# === módulo: endo_dsl.dsl.parser ===
_run('endo_dsl.dsl.parser', r'''"""Analisador sintático (parser) da Endo-DSL — RF01, RF02, RF03.

Implementa um parser de descida recursiva que produz a AST de
:mod:`endo_dsl.dsl.ast`. Erros sintáticos são reportados via :class:`ParseError`
com linha, coluna, token encontrado, o que era esperado e — quando possível —
uma sugestão de correção (campo desconhecido, nível de Bloom mal grafado, etc.).

A gramática formal correspondente está documentada em ``endo_dsl/dsl/grammar.ebnf``.
"""

from __future__ import annotations

import difflib
from typing import Any, List, Optional

from endo_dsl.dsl.ast import (
    Branch,
    Choice,
    GameSpec,
    GameplayLoop,
    Mechanic,
    Metadata,
    Narrative,
    Objective,
    Params,
    Transition,
)
from endo_dsl.dsl.bloom import Bloom, parse_bloom, suggest_bloom
from endo_dsl.dsl.tokenizer import LexError, Token, tokenize


class ParseError(Exception):
    """Erro sintático/léxico descritivo (RF03)."""

    def __init__(
        self,
        message: str,
        line: int,
        col: int,
        token: Optional[str] = None,
        suggestion: Optional[str] = None,
    ):
        self.message = message
        self.line = line
        self.col = col
        self.token = token
        self.suggestion = suggestion
        super().__init__(self.format())

    def format(self) -> str:
        parts = [f"Erro de sintaxe (linha {self.line}, coluna {self.col}): {self.message}"]
        if self.token is not None:
            parts.append(f"  token inválido: {self.token!r}")
        if self.suggestion:
            parts.append(f"  sugestão: {self.suggestion}")
        return "\n".join(parts)

    def to_dict(self) -> dict:
        return {
            "line": self.line,
            "col": self.col,
            "message": self.message,
            "token": self.token,
            "suggestion": self.suggestion,
            "kind": "syntactic",
        }


# Campos permitidos por bloco — usados para sugerir correções de digitação.
_MECHANIC_FIELDS = ["type", "bloom", "addresses", "params", "description"]
_OBJECTIVE_FIELDS = ["description", "bloom"]
_LOOP_FIELDS = ["bloom", "description", "steps"]
_BRANCH_FIELDS = ["bloom", "text", "description", "choice"]


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    # ------------------------------------------------------------------ #
    # Utilidades de fluxo
    # ------------------------------------------------------------------ #
    @property
    def cur(self) -> Token:
        return self.tokens[self.pos]

    def at_end(self) -> bool:
        return self.cur.kind == "EOF"

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if tok.kind != "EOF":
            self.pos += 1
        return tok

    def check(self, kind: str) -> bool:
        return self.cur.kind == kind

    def _describe(self, tok: Token) -> str:
        if tok.kind == "EOF":
            return "fim do arquivo"
        return tok.raw or str(tok.value)

    def expect(self, kind: str, what: str, suggestion: Optional[str] = None) -> Token:
        if self.cur.kind != kind:
            raise ParseError(
                f"esperava {what}",
                self.cur.line,
                self.cur.col,
                token=self._describe(self.cur),
                suggestion=suggestion,
            )
        return self.advance()

    def expect_keyword(self, word: str) -> Token:
        if self.cur.kind != "IDENT" or self.cur.value != word:
            raise ParseError(
                f"esperava a palavra-chave '{word}'",
                self.cur.line,
                self.cur.col,
                token=self._describe(self.cur),
            )
        return self.advance()

    # ------------------------------------------------------------------ #
    # Regras da gramática
    # ------------------------------------------------------------------ #
    def parse_spec(self) -> GameSpec:
        # Permite comentários/linhas em branco antes do bloco game (já tratados no lexer).
        if not (self.check("IDENT") and self.cur.value == "game"):
            raise ParseError(
                "a especificação deve começar com a declaração 'game'",
                self.cur.line,
                self.cur.col,
                token=self._describe(self.cur),
                suggestion='comece com: game "Título do Jogo" { ... }',
            )
        game_tok = self.advance()
        title_tok = self.expect("STRING", 'um título entre aspas para o jogo',
                                suggestion='ex.: game "Comparando Frações" { ... }')
        spec = GameSpec(line=game_tok.line, col=game_tok.col, title=str(title_tok.value))
        self.expect("LBRACE", "'{' para abrir o corpo do jogo")

        while not self.check("RBRACE") and not self.at_end():
            if not self.check("IDENT"):
                raise ParseError(
                    "esperava uma declaração (metadata, objective, mechanic, loop, narrative)",
                    self.cur.line,
                    self.cur.col,
                    token=self._describe(self.cur),
                )
            kw = self.cur.value
            if kw == "metadata":
                spec.metadata = self.parse_metadata()
            elif kw == "objective":
                spec.objectives.append(self.parse_objective())
            elif kw == "mechanic":
                spec.mechanics.append(self.parse_mechanic())
            elif kw == "loop":
                spec.loops.append(self.parse_loop())
            elif kw == "narrative":
                spec.narratives.append(self.parse_narrative())
            else:
                suggestion = self._suggest(
                    kw, ["metadata", "objective", "mechanic", "loop", "narrative"]
                )
                raise ParseError(
                    "declaração desconhecida no corpo do jogo",
                    self.cur.line,
                    self.cur.col,
                    token=kw,
                    suggestion=suggestion,
                )

        self.expect("RBRACE", "'}' para fechar o corpo do jogo")
        return spec

    def parse_metadata(self) -> Metadata:
        tok = self.expect_keyword("metadata")
        meta = Metadata(line=tok.line, col=tok.col)
        self.expect("LBRACE", "'{' após 'metadata'")
        while not self.check("RBRACE") and not self.at_end():
            key = self.expect("IDENT", "um nome de campo de metadados").value
            self.expect("COLON", f"':' após o campo '{key}'")
            meta.values[key] = self.parse_value()
        self.expect("RBRACE", "'}' para fechar o bloco 'metadata'")
        return meta

    def parse_objective(self) -> Objective:
        tok = self.expect_keyword("objective")
        name = self.expect("IDENT", "um identificador para o objetivo",
                           suggestion='ex.: objective OBJ_comparar { ... }').value
        obj = Objective(line=tok.line, col=tok.col, name=name)
        self.expect("LBRACE", f"'{{' após 'objective {name}'")
        while not self.check("RBRACE") and not self.at_end():
            field = self.expect("IDENT", "um campo do objetivo").value
            self.expect("COLON", f"':' após '{field}'")
            if field == "description":
                obj.description = str(self.parse_value())
            elif field == "bloom":
                obj.bloom = self.parse_bloom_value()
            else:
                raise ParseError(
                    "campo desconhecido em 'objective'",
                    self.cur.line, self.cur.col, token=field,
                    suggestion=self._suggest(field, _OBJECTIVE_FIELDS),
                )
        self.expect("RBRACE", "'}' para fechar o objetivo")
        return obj

    def parse_mechanic(self) -> Mechanic:
        tok = self.expect_keyword("mechanic")
        name = self.expect("IDENT", "um identificador para a mecânica").value
        mech = Mechanic(line=tok.line, col=tok.col, name=name)
        self.expect("LBRACE", f"'{{' após 'mechanic {name}'")
        while not self.check("RBRACE") and not self.at_end():
            field_tok = self.expect("IDENT", "um campo da mecânica")
            field = field_tok.value
            if field == "params":
                # bloco aninhado (sem ':')
                mech.params = self.parse_params()
                continue
            self.expect("COLON", f"':' após '{field}'")
            if field == "type":
                mech.type = str(self.parse_value())
            elif field == "bloom":
                mech.bloom = self.parse_bloom_value()
            elif field == "addresses":
                mech.addresses = self.parse_ident_list()
            elif field == "description":
                mech.description = str(self.parse_value())
            elif field == "source_component":
                mech.source_component = str(self.parse_value())
            else:
                raise ParseError(
                    "campo desconhecido em 'mechanic'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, _MECHANIC_FIELDS),
                )
        self.expect("RBRACE", "'}' para fechar a mecânica")
        return mech

    def parse_params(self) -> Params:
        # 'params' já consumido como IDENT pelo chamador
        tok = self.cur
        params = Params(line=tok.line, col=tok.col)
        self.expect("LBRACE", "'{' após 'params'")
        while not self.check("RBRACE") and not self.at_end():
            key = self.expect("IDENT", "um nome de parâmetro").value
            self.expect("COLON", f"':' após o parâmetro '{key}'")
            params.values[key] = self.parse_value()
        self.expect("RBRACE", "'}' para fechar o bloco 'params'")
        return params

    def parse_loop(self) -> GameplayLoop:
        tok = self.expect_keyword("loop")
        name = self.expect("IDENT", "um identificador para o loop").value
        loop = GameplayLoop(line=tok.line, col=tok.col, name=name)
        self.expect("LBRACE", f"'{{' após 'loop {name}'")
        while not self.check("RBRACE") and not self.at_end():
            field_tok = self.expect("IDENT", "um campo do loop")
            field = field_tok.value
            if field == "steps":
                loop.transitions = self.parse_steps()
                continue
            self.expect("COLON", f"':' após '{field}'")
            if field == "bloom":
                loop.bloom = self.parse_bloom_value()
            elif field == "description":
                loop.description = str(self.parse_value())
            else:
                raise ParseError(
                    "campo desconhecido em 'loop'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, _LOOP_FIELDS),
                )
        self.expect("RBRACE", "'}' para fechar o loop")
        return loop

    def parse_steps(self) -> List[Transition]:
        self.expect("LBRACE", "'{' após 'steps'")
        transitions: List[Transition] = []
        while not self.check("RBRACE") and not self.at_end():
            src_tok = self.expect("IDENT", "o estado de origem de uma transição")
            self.expect("ARROW", "'->' entre os estados da transição",
                        suggestion="use a forma: estado_origem -> estado_destino")
            dst_tok = self.expect("IDENT", "o estado de destino de uma transição")
            transitions.append(
                Transition(line=src_tok.line, col=src_tok.col,
                           src=str(src_tok.value), dst=str(dst_tok.value))
            )
        self.expect("RBRACE", "'}' para fechar o bloco 'steps'")
        return transitions

    def parse_narrative(self) -> Narrative:
        tok = self.expect_keyword("narrative")
        name = self.expect("IDENT", "um identificador para a narrativa").value
        narrative = Narrative(line=tok.line, col=tok.col, name=name)
        self.expect("LBRACE", f"'{{' após 'narrative {name}'")
        while not self.check("RBRACE") and not self.at_end():
            if self.check("IDENT") and self.cur.value == "branch":
                narrative.branches.append(self.parse_branch())
            else:
                raise ParseError(
                    "esperava uma declaração 'branch' dentro da narrativa",
                    self.cur.line, self.cur.col, token=self._describe(self.cur),
                    suggestion='ex.: branch inicio { text: "..." choice "Opção" -> outro_ramo }',
                )
        self.expect("RBRACE", "'}' para fechar a narrativa")
        return narrative

    def parse_branch(self) -> Branch:
        tok = self.expect_keyword("branch")
        name = self.expect("IDENT", "um identificador para o ramo").value
        branch = Branch(line=tok.line, col=tok.col, name=name)
        self.expect("LBRACE", f"'{{' após 'branch {name}'")
        while not self.check("RBRACE") and not self.at_end():
            field_tok = self.expect("IDENT", "um campo do ramo narrativo")
            field = field_tok.value
            if field == "choice":
                text_tok = self.expect("STRING", "o texto da escolha entre aspas")
                self.expect("ARROW", "'->' após o texto da escolha")
                target_tok = self.expect("IDENT", "o ramo de destino da escolha")
                branch.choices.append(
                    Choice(line=text_tok.line, col=text_tok.col,
                           text=str(text_tok.value), target=str(target_tok.value))
                )
                continue
            self.expect("COLON", f"':' após '{field}'")
            if field == "bloom":
                branch.bloom = self.parse_bloom_value()
            elif field == "text":
                branch.text = str(self.parse_value())
            elif field == "description":
                branch.description = str(self.parse_value())
            else:
                raise ParseError(
                    "campo desconhecido em 'branch'",
                    field_tok.line, field_tok.col, token=field,
                    suggestion=self._suggest(field, _BRANCH_FIELDS),
                )
        self.expect("RBRACE", "'}' para fechar o ramo")
        return branch

    # ------------------------------------------------------------------ #
    # Valores
    # ------------------------------------------------------------------ #
    def parse_value(self) -> Any:
        tok = self.cur
        if tok.kind in ("STRING", "NUMBER", "BOOL"):
            self.advance()
            return tok.value
        if tok.kind == "RANGE":
            self.advance()
            return list(tok.value)  # [start, end]
        if tok.kind == "IDENT":
            self.advance()
            return tok.value
        raise ParseError(
            "esperava um valor (texto, número, intervalo, booleano ou identificador)",
            tok.line, tok.col, token=self._describe(tok),
        )

    def parse_bloom_value(self) -> Bloom:
        tok = self.cur
        if tok.kind not in ("IDENT", "STRING"):
            raise ParseError(
                "esperava um nível da Taxonomia de Bloom",
                tok.line, tok.col, token=self._describe(tok),
                suggestion="níveis válidos: Lembrar, Compreender, Aplicar, Analisar, Avaliar, Criar",
            )
        self.advance()
        level = parse_bloom(str(tok.value))
        if level is None:
            sugg = suggest_bloom(str(tok.value))
            suggestion = (
                f"você quis dizer '{sugg[0]}'?"
                if sugg
                else "níveis válidos: Lembrar, Compreender, Aplicar, Analisar, Avaliar, Criar"
            )
            raise ParseError(
                "nível de Bloom inválido",
                tok.line, tok.col, token=str(tok.value), suggestion=suggestion,
            )
        return level

    def parse_ident_list(self) -> List[str]:
        idents = [str(self.expect("IDENT", "um identificador").value)]
        while self.check("COMMA"):
            self.advance()
            idents.append(str(self.expect("IDENT", "um identificador após ','").value))
        return idents

    # ------------------------------------------------------------------ #
    @staticmethod
    def _suggest(word: str, options: List[str]) -> Optional[str]:
        match = difflib.get_close_matches(word, options, n=1, cutoff=0.5)
        if match:
            return f"você quis dizer '{match[0]}'?"
        return f"campos válidos: {', '.join(options)}"


def parse(source: str) -> GameSpec:
    """Tokeniza e analisa ``source``, retornando a :class:`GameSpec`.

    Levanta :class:`ParseError` (com linha, coluna e sugestão) em caso de erro.
    """
    try:
        tokens = tokenize(source)
    except LexError as exc:
        raise ParseError(exc.message, exc.line, exc.col) from exc
    parser = Parser(tokens)
    spec = parser.parse_spec()
    if not parser.at_end():
        tok = parser.cur
        raise ParseError(
            "conteúdo inesperado após o fim da especificação",
            tok.line, tok.col, token=parser._describe(tok),
        )
    return spec
''')

# === módulo: endo_dsl.compiler.traceability ===
_run('endo_dsl.compiler.traceability', r'''"""Documento de rastreabilidade objetivo -> mecânica (RF23).

Gera, automaticamente a partir da AST, um documento que vincula cada objetivo de
aprendizagem declarado às mecânicas que o implementam, com seus níveis de Bloom.
Disponível em JSON (estruturado), Markdown (leitura) e HTML (visualização).
"""

from __future__ import annotations

from typing import Any, Dict

from endo_dsl.dsl.ast import GameSpec


def build(spec: GameSpec) -> Dict[str, Any]:
    """Documento de rastreabilidade estruturado (RF23)."""
    objectives = []
    for o in spec.objectives:
        mechs = [m for m in spec.mechanics if o.name in m.addresses]
        objectives.append({
            "objective": o.name,
            "description": o.description or o.name,
            "bloom": o.bloom.pt if o.bloom else None,
            "mechanics": [
                {
                    "name": m.name,
                    "type": m.type,
                    "bloom": m.bloom.pt if m.bloom else None,
                    "source_component": m.source_component,
                }
                for m in mechs
            ],
            "covered": bool(mechs),
        })
    # Mecânicas que não endereçam objetivo algum (lacuna de rastreabilidade).
    orphan = [m.name for m in spec.mechanics if not m.addresses]
    return {
        "title": spec.title,
        "domain": spec.metadata.get("domain"),
        "objectives": objectives,
        "orphan_mechanics": orphan,
        "coverage": _coverage(objectives),
    }


def _coverage(objectives) -> Dict[str, Any]:
    total = len(objectives)
    covered = sum(1 for o in objectives if o["covered"])
    return {
        "objectives_total": total,
        "objectives_covered": covered,
        "ratio": round(covered / total, 3) if total else None,
    }


def as_markdown(spec: GameSpec) -> str:
    doc = build(spec)
    lines = [
        f"# Rastreabilidade pedagógica — {doc['title']}",
        "",
        f"Domínio: **{doc['domain'] or '—'}**  ",
        f"Cobertura de objetivos: **{doc['coverage']['objectives_covered']}/"
        f"{doc['coverage']['objectives_total']}**",
        "",
        "| Objetivo | Nível de Bloom | Mecânicas que o implementam |",
        "|----------|----------------|------------------------------|",
    ]
    for o in doc["objectives"]:
        mechs = ", ".join(
            f"`{m['name']}` ({m['type']}, {m['bloom']})" for m in o["mechanics"]
        ) or "_— nenhuma —_"
        lines.append(f"| {o['description']} | {o['bloom'] or '—'} | {mechs} |")
    if doc["orphan_mechanics"]:
        lines += ["", "## Mecânicas sem objetivo vinculado",
                  ", ".join(f"`{m}`" for m in doc["orphan_mechanics"])]
    return "\n".join(lines)


def as_html(spec: GameSpec) -> str:
    doc = build(spec)
    rows = ""
    for o in doc["objectives"]:
        mechs = "<br>".join(
            f"<code>{m['name']}</code> <span style='color:#888'>({m['type']}, {m['bloom']})</span>"
            for m in o["mechanics"]
        ) or "<em>— nenhuma —</em>"
        rows += (f"<tr><td>{_esc(o['description'])}</td><td>{o['bloom'] or '—'}</td>"
                 f"<td>{mechs}</td></tr>")
    cov = doc["coverage"]
    return (
        "<!doctype html><meta charset='utf-8'>"
        f"<title>Rastreabilidade — {_esc(doc['title'])}</title>"
        "<style>body{font-family:system-ui;max-width:800px;margin:40px auto;padding:0 16px}"
        "table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:8px;"
        "text-align:left;vertical-align:top}th{background:#f4f6fb}</style>"
        f"<h1>Rastreabilidade pedagógica — {_esc(doc['title'])}</h1>"
        f"<p>Domínio: <b>{_esc(doc['domain'] or '—')}</b> · Cobertura: "
        f"<b>{cov['objectives_covered']}/{cov['objectives_total']}</b></p>"
        "<table><tr><th>Objetivo</th><th>Bloom</th><th>Mecânicas</th></tr>"
        f"{rows}</table>"
    )


def _esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
''')

# === módulo: endo_dsl.compiler.engine ===
_run('endo_dsl.compiler.engine', r'''"""Engine HTML5/JS dos protótipos gerados (RF19, RF21, RF22).

O protótipo é um único arquivo HTML autocontido (CSS + JS embutidos, sem
dependências externas — RF19). A jogabilidade é dirigida por um *content pack*
(JSON embutido em ``window.ENDO_GAME``), de modo que a **estrutura** (mecânicas,
níveis de Bloom, interações) fica separada do **conteúdo** (itens jogáveis),
permitindo reparametrização de domínio sem recompilar (RF22).

Os níveis de Bloom de cada mecânica são preservados no content pack e expostos
como atributos ``data-bloom`` no DOM (RF21).
"""

from __future__ import annotations

import json
from typing import Any, Dict

# --------------------------------------------------------------------------- #
# CSS — tema escuro sóbrio, responsivo, sem dependências.
# --------------------------------------------------------------------------- #
_CSS = """
:root{
  --bg:#0f1320; --panel:#1a2034; --panel2:#222a44; --ink:#e8ecf6; --muted:#9aa6c4;
  --accent:#5b8cff; --good:#37c98b; --bad:#ff6b6b; --warn:#ffc857;
  --b1:#7b61ff;--b2:#3aa0ff;--b3:#23c4a8;--b4:#ffb020;--b5:#ff7a59;--b6:#ff5d8f;
}
*{box-sizing:border-box}
body{margin:0;font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
  background:linear-gradient(160deg,#0c1020,#141a2e);color:var(--ink);min-height:100vh}
.wrap{max-width:820px;margin:0 auto;padding:24px}
header.game{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
h1{margin:0;font-size:1.7rem;letter-spacing:.3px}
.sub{color:var(--muted);font-size:.95rem}
.card{background:var(--panel);border:1px solid #2a3354;border-radius:16px;
  padding:22px;box-shadow:0 10px 30px rgba(0,0,0,.25);margin-bottom:18px}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}
.badge{font-size:.72rem;font-weight:700;padding:4px 10px;border-radius:999px;
  text-transform:uppercase;letter-spacing:.4px;color:#0b0f1c}
.bloom-1{background:var(--b1);color:#fff}.bloom-2{background:var(--b2);color:#fff}
.bloom-3{background:var(--b3)}.bloom-4{background:var(--b4)}
.bloom-5{background:var(--b5)}.bloom-6{background:var(--b6);color:#fff}
.tag{background:var(--panel2);color:var(--muted);font-size:.72rem;padding:4px 10px;
  border-radius:999px;border:1px solid #313b60}
.prompt{font-size:1.15rem;margin:6px 0 16px;line-height:1.45}
.options{display:grid;gap:10px}
button.opt,button.chip{font:inherit;text-align:left;background:var(--panel2);color:var(--ink);
  border:1px solid #38426c;border-radius:12px;padding:13px 16px;cursor:pointer;
  transition:.12s transform,.12s background}
button.opt:hover,button.chip:hover{background:#2c365a;transform:translateY(-1px)}
button.opt.correct{background:rgba(55,201,139,.22);border-color:var(--good)}
button.opt.wrong{background:rgba(255,107,107,.18);border-color:var(--bad)}
button.opt:disabled,button.chip:disabled{cursor:default;opacity:.85}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.col h4{margin:.2rem 0 .6rem;color:var(--muted);font-weight:600;font-size:.85rem}
.chip.sel{outline:2px solid var(--accent);background:#33406e}
.chip.done{opacity:.45}
.buckets{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-top:12px}
.bucket{background:var(--panel2);border:1px dashed #46517e;border-radius:12px;padding:12px;min-height:70px}
.bucket h4{margin:0 0 8px;font-size:.85rem;color:var(--muted)}
.bucket .item{background:#33406e;border-radius:8px;padding:6px 10px;margin:4px 0;font-size:.9rem}
.seq{display:flex;flex-direction:column;gap:8px}
.slot{display:flex;gap:8px;align-items:center}
.slot .n{width:26px;height:26px;border-radius:50%;background:var(--accent);color:#fff;
  display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.8rem}
.bar{height:8px;background:#222a44;border-radius:999px;overflow:hidden;margin:14px 0}
.bar > i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--b3));width:0;transition:.4s}
.feedback{margin-top:14px;padding:12px 14px;border-radius:12px;font-size:.95rem;display:none}
.feedback.show{display:block}
.feedback.ok{background:rgba(55,201,139,.15);border:1px solid var(--good)}
.feedback.no{background:rgba(255,107,107,.13);border:1px solid var(--bad)}
.row{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}
.btn{background:var(--accent);color:#fff;border:none;border-radius:12px;padding:12px 22px;
  font:inherit;font-weight:700;cursor:pointer}
.btn:hover{filter:brightness(1.08)}
.btn.ghost{background:transparent;border:1px solid #3a456e;color:var(--ink)}
.muted{color:var(--muted)}
.kv{display:flex;gap:8px;flex-wrap:wrap;font-size:.85rem;color:var(--muted)}
.kv b{color:var(--ink);font-weight:600}
.score{font-size:2.4rem;font-weight:800}
table.trace{width:100%;border-collapse:collapse;font-size:.9rem}
table.trace th,table.trace td{border-bottom:1px solid #2a3354;padding:8px;text-align:left;vertical-align:top}
table.trace th{color:var(--muted);font-weight:600}
footer{color:var(--muted);font-size:.78rem;text-align:center;margin:24px 0}
"""

# --------------------------------------------------------------------------- #
# JS — engine de jogabilidade. Lê window.ENDO_GAME e renderiza estágios.
# Sem dependências externas. Interações: choose, order, match, classify, info.
# --------------------------------------------------------------------------- #
_JS = r"""
(function(){
  const G = window.ENDO_GAME;
  const app = document.getElementById('app');
  let stageIdx = 0, totalScore = 0, maxScore = 0;
  const bloomVisited = new Set();

  const el = (t,c,txt)=>{const e=document.createElement(t); if(c)e.className=c; if(txt!=null)e.textContent=txt; return e;};
  const bloomBadge = (b)=>{ if(!b) return null; const e=el('span','badge bloom-'+b.level, b.name); e.setAttribute('data-bloom', b.name); return e; };

  function shuffle(a){a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}

  function header(){
    const h = el('header','game');
    h.appendChild(el('h1', G.title));
    const sub = el('div','sub', (G.meta.domain? G.meta.domain+' · ':'') + (G.meta.audience||''));
    h.appendChild(sub);
    return h;
  }

  function progress(){
    const bar = el('div','bar'); const i = el('i'); bar.appendChild(i);
    requestAnimationFrame(()=>{ i.style.width = Math.round(100*stageIdx/G.stages.length)+'%'; });
    return bar;
  }

  function start(){
    app.innerHTML=''; app.appendChild(header());
    const c = el('div','card');
    c.appendChild(el('div','muted','Protótipo educacional endógeno gerado pela Endo-DSL'));
    const badges = el('div','badges');
    (G.bloom_levels||[]).forEach(b=>{const x=bloomBadge(b); if(x)badges.appendChild(x);});
    c.appendChild(badges);
    const ul = el('div','kv');
    ul.innerHTML = '<span><b>Objetivos:</b> '+G.objectives.length+'</span>'+
                   '<span><b>Mecânicas:</b> '+G.stages.length+'</span>'+
                   '<span><b>Duração estimada:</b> '+(G.meta.duration||'—')+' min</span>';
    c.appendChild(ul);
    if(G.objectives.length){
      const list = el('ul'); list.style.color='var(--muted)';
      G.objectives.forEach(o=>{const li=el('li'); li.innerHTML='<b style="color:var(--ink)">'+o.bloom_name+':</b> '+o.description; list.appendChild(li);});
      c.appendChild(list);
    }
    const btn = el('button','btn','▶ Começar'); btn.onclick=()=>{stageIdx=0;totalScore=0;maxScore=0;bloomVisited.clear();renderStage();};
    const row = el('div','row'); row.appendChild(btn);
    const tbtn = el('button','btn ghost','Ver rastreabilidade'); tbtn.onclick=showTrace; row.appendChild(tbtn);
    c.appendChild(row);
    app.appendChild(c);
  }

  function renderStage(){
    if(stageIdx>=G.stages.length){ return finish(); }
    const s = G.stages[stageIdx];
    if(s.bloom) bloomVisited.add(s.bloom.name);
    app.innerHTML=''; app.appendChild(header()); app.appendChild(progress());
    const c = el('div','card'); c.setAttribute('data-mechanic', s.mechanic);
    if(s.bloom) c.setAttribute('data-bloom', s.bloom.name);
    const top = el('div','row');
    const tags = el('div','badges');
    const bb = bloomBadge(s.bloom); if(bb) tags.appendChild(bb);
    tags.appendChild(el('span','tag', s.type_label||s.mechanic));
    top.appendChild(tags);
    top.appendChild(el('span','muted','Etapa '+(stageIdx+1)+'/'+G.stages.length));
    c.appendChild(top);
    if(s.description){ const d=el('div','muted'); d.style.margin='6px 0 4px'; d.textContent=s.description; c.appendChild(d); }
    app.appendChild(c);
    const host = el('div'); c.appendChild(host);
    const render = INTERACTIONS[s.interaction] || INTERACTIONS.info;
    render(host, s, (gained, max)=>{ totalScore+=gained; maxScore+=max; });
  }

  function nextButton(host, label){
    const row = el('div','row'); row.style.marginTop='14px';
    const b = el('button','btn', label||'Continuar →');
    b.onclick=()=>{ stageIdx++; renderStage(); };
    row.appendChild(b); host.appendChild(row); return b;
  }

  // ---- Interações ----
  const INTERACTIONS = {
    info: function(host, s, score){
      const p = el('div','prompt', (s.content && s.content.text) || 'Reflita sobre o desafio proposto.');
      host.appendChild(p);
      score(1,1);
      nextButton(host);
    },

    choose: function(host, s, score){
      const items = s.content.items||[]; let idx=0; let gained=0;
      const promptEl = el('div','prompt'); host.appendChild(promptEl);
      const opts = el('div','options'); host.appendChild(opts);
      const fb = el('div','feedback'); host.appendChild(fb);
      function step(){
        if(idx>=items.length){ score(gained, items.length); return nextButton(host); }
        const it = items[idx];
        promptEl.textContent = it.prompt;
        opts.innerHTML=''; fb.className='feedback';
        const order = it.shuffle===false? it.options.map((o,i)=>i) : shuffle(it.options.map((o,i)=>i));
        order.forEach(oi=>{
          const b = el('button','opt', it.options[oi]);
          b.onclick=()=>{
            Array.from(opts.children).forEach(x=>x.disabled=true);
            const correct = oi===it.correct;
            if(correct){ b.classList.add('correct'); gained++; }
            else { b.classList.add('wrong'); const cb=opts.children[order.indexOf(it.correct)]; if(cb)cb.classList.add('correct'); }
            fb.className='feedback show '+(correct?'ok':'no');
            fb.textContent = (correct?'✓ ':'✗ ') + (it.explanation || (correct?'Correto!':'Resposta correta destacada.'));
            const nb = el('button','btn', idx+1>=items.length?'Concluir etapa →':'Próximo →');
            nb.style.marginTop='12px'; nb.onclick=()=>{idx++; step();}; fb.appendChild(document.createElement('br')); fb.appendChild(nb);
          };
          opts.appendChild(b);
        });
      }
      step();
    },

    order: function(host, s, score){
      const correct = s.content.items||[]; const pool = shuffle(correct.map((t,i)=>({t,i})));
      host.appendChild(el('div','prompt', s.content.prompt||'Coloque os itens na ordem correta:'));
      const chips = el('div','options'); host.appendChild(chips);
      const seq = el('div','seq'); seq.style.marginTop='12px'; host.appendChild(seq);
      const fb = el('div','feedback'); host.appendChild(fb);
      const chosen=[];
      function redraw(){
        seq.innerHTML='';
        chosen.forEach((c,n)=>{const slot=el('div','slot'); slot.appendChild(el('span','n', (n+1))); slot.appendChild(el('span',null,c.t)); seq.appendChild(slot);});
      }
      pool.forEach(p=>{
        const b=el('button','chip', p.t);
        b.onclick=()=>{ if(b.classList.contains('done'))return; b.classList.add('done'); b.disabled=true; chosen.push(p); redraw();
          if(chosen.length===correct.length){ check(); } };
        chips.appendChild(b);
      });
      function check(){
        let ok=0; chosen.forEach((c,n)=>{ if(c.i===n) ok++; });
        const perfect = ok===correct.length;
        fb.className='feedback show '+(perfect?'ok':'no');
        fb.textContent=(perfect?'✓ Ordem correta!':'✗ '+ok+'/'+correct.length+' nas posições certas. Ordem correta: '+correct.join(' → '));
        score(ok, correct.length); nextButton(host);
      }
    },

    match: function(host, s, score){
      const pairs = s.content.pairs||[];
      host.appendChild(el('div','prompt', s.content.prompt||'Associe os pares correspondentes:'));
      const cols = el('div','cols'); host.appendChild(cols);
      const left = el('div','col'); left.appendChild(el('h4','Coluna A'));
      const right = el('div','col'); right.appendChild(el('h4','Coluna B'));
      cols.appendChild(left); cols.appendChild(right);
      const fb = el('div','feedback'); host.appendChild(fb);
      let sel=null, matched=0, errors=0;
      pairs.forEach((p,i)=>{ const b=el('button','chip',p.a); b.dataset.k=i; b.onclick=()=>{ if(b.disabled)return; clearSel(); sel=b; b.classList.add('sel'); }; left.appendChild(b); });
      shuffle(pairs.map((p,i)=>({t:p.b,k:i}))).forEach(r=>{ const b=el('button','chip',r.t); b.dataset.k=r.k;
        b.onclick=()=>{ if(!sel||b.disabled)return; if(b.dataset.k===sel.dataset.k){ b.disabled=sel.disabled=true; b.classList.add('done'); sel.classList.remove('sel'); sel.classList.add('done'); matched++; if(matched===pairs.length)done(); }
          else { errors++; flash(b); flash(sel); } clearSel(); };
        right.appendChild(b); });
      function clearSel(){ if(sel){sel.classList.remove('sel'); sel=null;} }
      function flash(b){ b.classList.add('wrong'); setTimeout(()=>b.classList.remove('wrong'),300); }
      function done(){ fb.className='feedback show ok'; fb.textContent='✓ Todos os pares associados ('+errors+' tentativas erradas).'; score(Math.max(0,pairs.length-errors), pairs.length); nextButton(host); }
    },

    classify: function(host, s, score){
      const cats = s.content.categories||[]; const items = shuffle((s.content.items||[]).slice());
      host.appendChild(el('div','prompt', s.content.prompt||'Classifique cada item na categoria correta:'));
      const itemRow = el('div','options'); host.appendChild(itemRow);
      const buckets = el('div','buckets'); host.appendChild(buckets);
      const fb = el('div','feedback'); host.appendChild(fb);
      let sel=null, placed=0, correct=0;
      const bucketEls={};
      cats.forEach(cat=>{ const bk=el('div','bucket'); bk.appendChild(el('h4',cat)); bk.onclick=()=>{ if(!sel)return; const it=sel.__item;
          const ok = it.category===cat; placed++; if(ok)correct++;
          const tag=el('div','item', it.text + (ok?' ✓':' ✗ ('+it.category+')')); bk.appendChild(tag);
          sel.disabled=true; sel.classList.add('done'); sel=null;
          if(placed===items.length){ fb.className='feedback show '+(correct===items.length?'ok':'no'); fb.textContent=(correct===items.length?'✓ ':'✗ ')+correct+'/'+items.length+' classificados corretamente.'; score(correct, items.length); nextButton(host);} };
        bucketEls[cat]=bk; buckets.appendChild(bk); });
      items.forEach(it=>{ const b=el('button','chip', it.text); b.__item=it; b.onclick=()=>{ if(b.disabled)return; if(sel)sel.classList.remove('sel'); sel=b; b.classList.add('sel'); }; itemRow.appendChild(b); });
    }
  };

  function finish(){
    app.innerHTML=''; app.appendChild(header());
    const c = el('div','card');
    const pct = maxScore? Math.round(100*totalScore/maxScore):0;
    c.appendChild(el('div','muted','Protótipo concluído'));
    c.appendChild(el('div','score', pct+'%'));
    c.appendChild(el('div',null,'Pontuação: '+totalScore+' de '+maxScore));
    const badges = el('div','badges'); badges.style.marginTop='12px';
    badges.appendChild(el('span','muted','Níveis de Bloom exercitados: '));
    (G.bloom_levels||[]).forEach(b=>{ if(bloomVisited.has(b.name)){ const x=bloomBadge(b); if(x)badges.appendChild(x);} });
    c.appendChild(badges);
    const row=el('div','row'); row.style.marginTop='10px';
    const again=el('button','btn','↻ Jogar de novo'); again.onclick=()=>{stageIdx=0;totalScore=0;maxScore=0;bloomVisited.clear();renderStage();};
    const tb=el('button','btn ghost','Ver rastreabilidade'); tb.onclick=showTrace;
    row.appendChild(again); row.appendChild(tb); c.appendChild(row);
    app.appendChild(c);
  }

  function showTrace(){
    app.innerHTML=''; app.appendChild(header());
    const c = el('div','card');
    c.appendChild(el('h1','Rastreabilidade pedagógica'));
    c.appendChild(el('div','muted','Vínculo entre objetivos de aprendizagem e mecânicas (RF23).'));
    const t = el('table','trace');
    t.innerHTML='<tr><th>Objetivo</th><th>Bloom</th><th>Mecânicas que o endereçam</th></tr>';
    (G.traceability.links||[]).forEach(L=>{
      const tr=el('tr');
      tr.innerHTML='<td>'+L.objective_description+'</td><td>'+L.bloom+'</td><td>'+
        (L.mechanics.map(m=>m.name+' <span class="muted">('+m.type+', '+m.bloom+')</span>').join('<br>')||'<span class="muted">— nenhuma —</span>')+'</td>';
      t.appendChild(tr);
    });
    c.appendChild(t);
    const back=el('button','btn ghost','← Voltar'); back.style.marginTop='14px'; back.onclick=start; c.appendChild(back);
    app.appendChild(c);
  }

  start();
})();
"""

_HTML_SHELL = """<!doctype html>
<html lang="pt-br" data-endo-dsl="1" data-bloom-levels="__BLOOM_DATA__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="generator" content="Endo-DSL Compiler v__VERSION__">
<meta name="endo-dsl:bloom-levels" content="__BLOOM_META__">
<title>__TITLE__</title>
<style>__CSS__</style>
</head>
<body>
<div class="wrap"><div id="app"></div>
<footer>Gerado por <b>Endo-DSL</b> · protótipo educacional endógeno · níveis de Bloom rastreáveis (data-bloom)</footer>
</div>
<!-- ENDO-DSL CONTENT PACK: estrutura (mecânicas/Bloom) separada do conteúdo, permitindo reparametrização (RF22) -->
<script id="endo-content" type="application/json">__CONTENT_PACK__</script>
<script>window.ENDO_GAME = JSON.parse(document.getElementById('endo-content').textContent);</script>
<script>__JS__</script>
</body>
</html>
"""


def render_html(content_pack: Dict[str, Any], version: str = "1.0.0") -> str:
    """Monta o arquivo HTML autocontido a partir do *content pack*."""
    bloom_names = [b["name"] for b in content_pack.get("bloom_levels", [])]
    pack_json = json.dumps(content_pack, ensure_ascii=False)
    # Evita que '</script>' no conteúdo quebre o documento.
    pack_json = pack_json.replace("</", "<\\/")
    html = _HTML_SHELL
    html = html.replace("__CSS__", _CSS)
    html = html.replace("__JS__", _JS)
    html = html.replace("__TITLE__", _escape(content_pack.get("title", "Protótipo Endo-DSL")))
    html = html.replace("__CONTENT_PACK__", pack_json)
    html = html.replace("__VERSION__", version)
    html = html.replace("__BLOOM_META__", _escape(", ".join(bloom_names)))
    html = html.replace("__BLOOM_DATA__", _escape(json.dumps(bloom_names, ensure_ascii=False)))
    return html


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
''')

# === módulo: endo_dsl.compiler.content ===
_run('endo_dsl.compiler.content', r'''"""Construção do *content pack* dos protótipos (RF21, RF22).

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
''')

# === módulo: endo_dsl.compiler.compiler ===
_run('endo_dsl.compiler.compiler', r'''"""Compilador Endo-DSL -> protótipo HTML5 jogável (RF19–RF23).

Fluxo:
    fonte DSL --parse--> AST --valida--> content pack --render--> HTML autocontido

Garante:
* RF19 — saída HTML5 executável no navegador sem dependências externas;
* RF20 — erros de compilação descritivos, com sugestões referenciando a biblioteca;
* RF21 — níveis de Bloom preservados (no content pack e em ``data-bloom``);
* RF22 — reparametrização de conteúdo sem recompilar a estrutura;
* RF23 — documento de rastreabilidade gerado automaticamente.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from endo_dsl import __version__
from endo_dsl.compiler import content as content_mod
from endo_dsl.compiler import engine, traceability
from endo_dsl.dsl.ast import GameSpec
from endo_dsl.dsl.parser import ParseError, parse
from endo_dsl.dsl.semantic import MECHANIC_TYPES, validate_semantics


class CompileError(Exception):
    """Erro de compilação com mensagens descritivas e sugestões (RF20)."""

    def __init__(self, messages: List[Dict[str, Any]]):
        self.messages = messages
        super().__init__("; ".join(m.get("message", "") for m in messages))

    def to_dict(self) -> Dict[str, Any]:
        return {"errors": self.messages}


@dataclass
class CompileResult:
    """Resultado bem-sucedido da compilação."""

    html: str
    content_pack: Dict[str, Any]
    traceability: Dict[str, Any]
    bloom_levels: List[str] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)
    spec: Optional[GameSpec] = None

    def write(self, out_dir: str | Path, *, basename: str = "prototype") -> Dict[str, str]:
        """Escreve protótipo, rastreabilidade e content pack em ``out_dir``.

        Retorna os caminhos gerados.
        """
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        html_path = out / f"{basename}.html"
        trace_path = out / f"{basename}.traceability.html"
        trace_json = out / f"{basename}.traceability.json"
        content_path = out / f"{basename}.content.json"

        html_path.write_text(self.html, encoding="utf-8")
        if self.spec is not None:
            trace_path.write_text(traceability.as_html(self.spec), encoding="utf-8")
        trace_json.write_text(
            json.dumps(self.traceability, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        content_path.write_text(
            json.dumps(self.content_pack, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return {
            "html": str(html_path),
            "traceability_html": str(trace_path),
            "traceability_json": str(trace_json),
            "content_pack": str(content_path),
        }


def _suggest_from_library(mech_type: str) -> Optional[str]:
    """RF20 — sugere construtos equivalentes na biblioteca (catálogo de mecânicas)."""
    import difflib
    match = difflib.get_close_matches(mech_type, list(MECHANIC_TYPES), n=1, cutoff=0.4)
    if match:
        m = MECHANIC_TYPES[match[0]]
        return (f"a biblioteca oferece a mecânica '{match[0]}' ({m.label}); "
                f"considere usá-la.")
    return f"tipos de mecânica disponíveis na biblioteca: {', '.join(sorted(MECHANIC_TYPES))}"


def compile_spec(spec: GameSpec, *,
                 content_overrides: Optional[Dict[str, Any]] = None,
                 strict: bool = True) -> CompileResult:
    """Compila uma AST já validada em protótipo HTML5 (RF19).

    Se ``strict`` (padrão), erros semânticos abortam a compilação com mensagens
    descritivas (RF20). Warnings nunca abortam, mas são retornados.
    """
    issues = validate_semantics(spec)
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i.to_dict() for i in issues if i.severity == "warning"]

    if errors and strict:
        messages = []
        for e in errors:
            d = e.to_dict()
            # Enriquecimento de sugestão referenciando a biblioteca (RF20).
            if e.code in ("E_BAD_TYPE", "E_NO_TYPE"):
                mech_type = _extract_type_token(e.message)
                lib = _suggest_from_library(mech_type)
                if lib:
                    d["suggestion"] = (d.get("suggestion") or "") + " " + lib
            messages.append(d)
        raise CompileError(messages)

    pack = content_mod.build_content_pack(spec, content_overrides=content_overrides)
    html = engine.render_html(pack, version=__version__)
    trace = traceability.build(spec)
    bloom_levels = [b.pt for b in spec.bloom_levels]
    return CompileResult(
        html=html,
        content_pack=pack,
        traceability=trace,
        bloom_levels=bloom_levels,
        warnings=warnings,
        spec=spec,
    )


def _extract_type_token(message: str) -> str:
    m = re.search(r"'([^']+)'", message)
    return m.group(1) if m else ""


def compile_source(source: str, *,
                   content_overrides: Optional[Dict[str, Any]] = None,
                   strict: bool = True) -> CompileResult:
    """Compila a partir do texto-fonte DSL (parse + semântica + render).

    Erros de sintaxe (RF03) e de compilação (RF20) são levantados como
    :class:`CompileError` com mensagens estruturadas.
    """
    try:
        spec = parse(source)
    except ParseError as exc:
        raise CompileError([exc.to_dict()]) from exc
    return compile_spec(spec, content_overrides=content_overrides, strict=strict)


# --------------------------------------------------------------------------- #
# RF22 — Reparametrização de conteúdo independente de estrutura.
# --------------------------------------------------------------------------- #
def reparametrize_content(html: str, *,
                          domain: Optional[str] = None,
                          topic: Optional[str] = None,
                          content_pack: Optional[Dict[str, Any]] = None) -> str:
    """Troca o domínio/conteúdo de um protótipo JÁ compilado **sem recompilar** (RF22).

    A estrutura (mecânicas, interações, níveis de Bloom) é preservada; apenas o
    conteúdo embutido é substituído. Pode-se passar um ``content_pack`` pronto ou
    pedir a re-resolução do banco por ``domain``/``topic``.
    """
    current = _extract_content_pack(html)
    if current is None:
        raise ValueError("HTML não contém um content pack Endo-DSL válido.")

    if content_pack is not None:
        new_pack = content_pack
    else:
        bank = content_mod.resolve_bank(domain, topic)
        new_pack = dict(current)
        new_pack["domain"] = domain or current.get("domain")
        # Reescreve o conteúdo de cada estágio preservando a estrutura.
        new_stages = []
        for stage in current["stages"]:
            st = dict(stage)
            interaction = st.get("interaction", "choose")
            if interaction == "choose":
                st["content"] = {"items": [dict(i) for i in bank.get("choose", [])]} or st["content"]
            elif interaction in bank:
                st["content"] = dict(bank[interaction])
            new_stages.append(st)
        new_pack["stages"] = new_stages

    pack_json = json.dumps(new_pack, ensure_ascii=False).replace("</", "<\\/")
    return re.sub(
        r'(<script id="endo-content" type="application/json">).*?(</script>)',
        lambda m: m.group(1) + pack_json + m.group(2),
        html,
        count=1,
        flags=re.DOTALL,
    )


def _extract_content_pack(html: str) -> Optional[Dict[str, Any]]:
    m = re.search(
        r'<script id="endo-content" type="application/json">(.*?)</script>',
        html, flags=re.DOTALL,
    )
    if not m:
        return None
    raw = m.group(1).replace("<\\/", "</")
    try:
        return json.loads(raw)
    except ValueError:
        return None
''')

# === módulo: endo_dsl.compiler_cli ===
_run('endo_dsl.compiler_cli', r'''"""CLI mínima do compilador Endo-DSL — ``endo-dslc`` (sem banco de dados).

Expõe APENAS o caminho de compilação DSL -> HTML5 (RF19–RF23). Nenhuma
dependência de SQLite, agentes LLM ou biblioteca web é importada aqui — toda a
cadeia (:mod:`endo_dsl.compiler.compiler`) é livre de banco de dados.

Uso::

    endo-dslc entrada.endo                 # compila, escreve ./<base>.html
    endo-dslc entrada.endo -o jogo.html    # define o arquivo de saída
    cat entrada.endo | endo-dslc -         # lê da entrada padrão
    endo-dslc entrada.endo --trace         # também grava rastreabilidade (RF23)
    endo-dslc entrada.endo --check         # apenas valida, não escreve nada

Esta CLI é o ponto de entrada da distribuição "compiler-only" e da build nativa.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Importa SOMENTE o compilador (caminho livre de banco de dados).
from endo_dsl import __version__
from endo_dsl.compiler.compiler import CompileError, compile_source
from endo_dsl.compiler import traceability


def _read_source(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def _format_errors(exc: CompileError) -> str:
    lines = ["Falha de compilação Endo-DSL:"]
    for m in exc.messages:
        loc = ""
        if m.get("line"):
            loc = f" (linha {m['line']}, coluna {m.get('col', 0)})"
        lines.append(f"  - [{m.get('code', m.get('kind', 'erro'))}]{loc} {m.get('message', '')}")
        if m.get("suggestion"):
            lines.append(f"    sugestão: {m['suggestion']}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="endo-dslc",
        description="Compilador Endo-DSL: .endo -> protótipo HTML5 jogável "
                    "(sem banco de dados, sem servidor).",
    )
    p.add_argument("input", help="arquivo .endo de entrada (ou '-' para stdin)")
    p.add_argument("-o", "--output", help="arquivo HTML de saída "
                                          "(padrão: <base>.html ao lado da entrada)")
    p.add_argument("--trace", action="store_true",
                   help="também grava o documento de rastreabilidade HTML (RF23)")
    p.add_argument("--check", action="store_true",
                   help="apenas valida (parse + semântica), não escreve saída")
    p.add_argument("--no-strict", action="store_true",
                   help="não aborta em erros semânticos (gera mesmo com inconsistências)")
    p.add_argument("--version", action="version",
                   version=f"endo-dslc (Endo-DSL {__version__})")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        source = _read_source(args.input)
    except OSError as exc:
        print(f"Não foi possível ler a entrada: {exc}", file=sys.stderr)
        return 2

    try:
        result = compile_source(source, strict=not args.no_strict)
    except CompileError as exc:
        print(_format_errors(exc), file=sys.stderr)
        return 1

    for w in result.warnings:
        print(f"aviso [{w.get('code')}]: {w.get('message')}", file=sys.stderr)

    if args.check:
        print(f"OK — especificação válida ({len(result.bloom_levels)} níveis de Bloom, "
              f"{len(result.content_pack.get('stages', []))} mecânicas).", file=sys.stderr)
        return 0

    if args.output:
        out_path = Path(args.output)
    elif args.input == "-":
        out_path = Path("prototype.html")
    else:
        out_path = Path(args.input).with_suffix(".html")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result.html, encoding="utf-8")
    print(f"HTML5 gerado: {out_path}", file=sys.stderr)

    if args.trace and result.spec is not None:
        trace_path = out_path.with_suffix(".traceability.html")
        trace_path.write_text(traceability.as_html(result.spec), encoding="utf-8")
        print(f"Rastreabilidade gerada: {trace_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''')

# === __init__: endo_dsl.dsl ===
_run('endo_dsl.dsl', r'''"""Módulo 1 — Motor da DSL: gramática formal, parser e validadores.

Cobre RF01–RF06.
"""

from endo_dsl.dsl.bloom import Bloom, BLOOM_ORDER
from endo_dsl.dsl.ast import (
    GameSpec,
    Metadata,
    Objective,
    Mechanic,
    GameplayLoop,
    Transition,
    Narrative,
    Branch,
    Choice,
    Params,
)
from endo_dsl.dsl.parser import parse, ParseError
from endo_dsl.dsl.semantic import (
    validate_semantics,
    SemanticIssue,
    MECHANIC_TYPES,
    mechanic_bloom_affinity,
)

__all__ = [
    "Bloom",
    "BLOOM_ORDER",
    "GameSpec",
    "Metadata",
    "Objective",
    "Mechanic",
    "GameplayLoop",
    "Transition",
    "Narrative",
    "Branch",
    "Choice",
    "Params",
    "parse",
    "ParseError",
    "validate_semantics",
    "SemanticIssue",
    "MECHANIC_TYPES",
    "mechanic_bloom_affinity",
]
''')

# === __init__: endo_dsl.compiler ===
_run('endo_dsl.compiler', r'''"""Módulo 4 — Compilador e Gerador de Protótipos (RF19–RF23)."""

from endo_dsl.compiler.compiler import (
    CompileResult,
    CompileError,
    compile_source,
    compile_spec,
    reparametrize_content,
)

__all__ = [
    "CompileResult",
    "CompileError",
    "compile_source",
    "compile_spec",
    "reparametrize_content",
]
''')


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    from endo_dsl.compiler_cli import main  # type: ignore  # noqa: E402
    raise SystemExit(main())
