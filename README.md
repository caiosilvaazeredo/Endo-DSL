# Endo-DSL

**Plataforma de design de jogos educativos baseada em DSL e taxonomia de Bloom**

Endo-DSL é uma plataforma de pesquisa desenvolvida no PESC/COPPE/UFRJ para a geração
semi-automática de protótipos de jogos educativos HTML5 a partir de uma linguagem de
domínio específico (DSL) estruturada pela taxonomia revisada de Bloom.

O sistema integra recuperação de componentes pedagógicos (RAG), geração de código de jogo
por LLM opcional, compilação para HTML5 puro (zero dependências externas em runtime) e
avaliação multidimensional de protótipos.

---

## Requisitos

- Python 3.11 ou superior
- Nenhuma dependência externa obrigatória (stdlib apenas)
- Opcional: `anthropic>=0.25` para geração via Claude

---

## Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/caiosazeredo/Endo-DSL.git
cd Endo-DSL

# 2. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 3. Instale em modo editável (sem dependências externas)
pip install -e .

# 4. (Opcional) Instale suporte a LLM via Anthropic
pip install -e ".[llm]"
```

---

## Quick Start

### Interface web

```bash
# Inicializa o banco de dados e inicia o servidor
endo-dsl serve --host 0.0.0.0 --port 8000

# Acesse em: http://localhost:8000
```

### CLI — compilar um arquivo DSL

```bash
# Compila e gera um protótipo HTML5 em ./prototypes/
endo-dsl compile examples/fracoes.endo

# Compila com saída em diretório específico
endo-dsl compile examples/fracoes.endo --out ./meu-jogo/
```

### CLI — validar sintaxe e semântica

```bash
endo-dsl validate examples/fracoes.endo
```

### CLI — inicializar banco de dados

```bash
endo-dsl init-db
```

### CLI — popular biblioteca de componentes

```bash
endo-dsl seed-components
```

### CLI — executar curadoria de componentes

```bash
endo-dsl curate --status pending
```

---

## Fluxo do Studio (6 Fases)

```
Fase 1 → Contexto    : domínio, tópico, nível Bloom, faixa etária, duração
Fase 2 → Recuperação : busca de componentes pedagógicos na biblioteca (RAG)
Fase 3 → Geração     : geração da DSL com base no contexto + componentes
Fase 4 → Revisão     : edição manual da DSL com validação ao vivo
Fase 5 → Compilação  : geração do protótipo HTML5 e métricas
Fase 6 → Avaliação   : avaliação multidimensional do protótipo
```

Acesse `/studio` na interface web para percorrer o fluxo completo.

---

## Estrutura do Projeto

```
Endo-DSL/
├── endo_dsl/
│   ├── cli.py               # Ponto de entrada CLI
│   ├── db/
│   │   └── schema.sql       # Schema SQLite
│   ├── dsl/
│   │   ├── grammar.ebnf     # Gramática EBNF da DSL
│   │   ├── parser.py        # Parser recursivo descendente
│   │   └── validator.py     # Validação sintática e semântica
│   ├── rag/
│   │   └── retriever.py     # Recuperação por similaridade
│   ├── compiler/
│   │   └── html5.py         # Compilador DSL → HTML5
│   └── web/
│       ├── server.py        # Servidor HTTP (stdlib apenas)
│       ├── views.py         # Templates HTML
│       └── static/
│           ├── app.css      # Estilos da interface
│           ├── studio.js    # Lógica do studio (fases 1-6)
│           ├── curator.js   # Curadoria de componentes
│           └── evaluate.js  # Formulário de avaliação
├── examples/
│   └── fracoes.endo         # Exemplo: Comparando Frações (Bloom: Analisar)
├── pyproject.toml
└── README.md
```

---

## Sintaxe DSL — Resumo

```
game "<título>" {
  metadata {
    domain:    "<área>"
    topic:     "<tópico>"
    bloom:     Lembrar | Compreender | Aplicar | Analisar | Avaliar | Criar
    age_range: "<faixa>"
    duration:  <minutos>
  }

  objective <id> {
    description: "<descrição do objetivo de aprendizagem>"
    bloom:       <nível>
  }

  mechanic <id> {
    type:      quiz | classification | sequencing | matching | puzzle | comparison | ...
    bloom:     <nível>
    addresses: <objective_id>
    params { <chave>: <valor> ... }
  }

  loop <id> {
    bloom: <nível>
    steps {
      <mechanic_id> -> <mechanic_id>
    }
  }
}
```

---

## Níveis de Bloom Suportados

| Nível        | Cor        | Verbos típicos                          |
|--------------|------------|-----------------------------------------|
| Lembrar      | Azul       | identificar, reconhecer, listar         |
| Compreender  | Teal       | explicar, classificar, resumir          |
| Aplicar      | Verde      | usar, resolver, demonstrar              |
| Analisar     | Amarelo    | comparar, diferenciar, organizar        |
| Avaliar      | Laranja    | julgar, criticar, justificar            |
| Criar        | Vermelho   | construir, planejar, produzir           |

---

## API HTTP (servidor embutido)

| Método | Endpoint                        | Descrição                              |
|--------|---------------------------------|----------------------------------------|
| POST   | `/api/session`                  | Cria sessão com contexto               |
| POST   | `/api/retrieve`                 | Recupera componentes (RAG)             |
| POST   | `/api/generate`                 | Gera DSL                               |
| POST   | `/api/validate`                 | Valida DSL (sintaxe + semântica)       |
| POST   | `/api/compile`                  | Compila DSL → protótipo HTML5          |
| POST   | `/api/reparametrize`            | Reparametriza protótipo existente      |
| POST   | `/api/evaluate`                 | Registra avaliação de protótipo        |
| POST   | `/api/curate`                   | Ação de curadoria em componente        |
| GET    | `/prototype/<pid>`              | Jogo HTML5 compilado                   |
| GET    | `/prototype/<pid>/traceability` | Rastreabilidade pedagógica             |
| GET    | `/evaluate/<pid>`               | Formulário de avaliação                |

---

## Pesquisa

Este sistema é parte da dissertação de mestrado desenvolvida no
**Programa de Engenharia de Sistemas e Computação (PESC)**,
**COPPE/Universidade Federal do Rio de Janeiro (UFRJ)**.

- Instituição: COPPE/UFRJ — PESC
- Contato: caiosazeredo@cos.ufrj.br

---

## Licença

MIT License — veja o arquivo `LICENSE` para detalhes.
