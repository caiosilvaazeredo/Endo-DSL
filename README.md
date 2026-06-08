# Endo-DSL

**Plataforma de design de jogos educativos** baseada em DSL declarativa e taxonomia de Bloom.

Desenvolvida como parte da pesquisa de doutorado no PESC/COPPE/UFRJ — Caio Azeredo.

---

## Visão Geral

A Endo-DSL permite que designers educacionais e educadores criem especificações formais de jogos sérios usando uma linguagem de domínio específico (DSL) alinhada à Taxonomia de Bloom. A plataforma automatiza:

- Recuperação semântica de componentes pedagógicos reutilizáveis
- Geração de especificações DSL via pipeline multi-agente (com LLM opcional)
- Compilação para protótipos HTML5 jogáveis (zero dependências externas)
- Avaliação pedagógica multidimensional com relatórios comparativos
- Curadoria colaborativa da biblioteca de componentes

---

## Requisitos

- Python 3.11+
- Sem dependências obrigatórias (stdlib apenas)
- Opcional: `anthropic` para geração via LLM

---

## Instalação

```bash
git clone https://github.com/caiosilvaazeredo/endo-dsl.git
cd endo-dsl
pip install -e .

# Com suporte a LLM (Claude API):
pip install -e ".[llm]"
export ANTHROPIC_API_KEY=sk-...
```

---

## Uso Rápido

### Interface Web

```bash
endo-dsl serve
# Acesse http://localhost:8000
```

### Demonstração completa (linha de comando)

```bash
endo-dsl demo
```

### Compilar um arquivo `.endo`

```bash
endo-dsl compile examples/fracoes.endo
# Gera: prototypes/<uuid>/index.html
```

### Validar sintaxe e semântica

```bash
endo-dsl validate examples/fracoes.endo
```

### Biblioteca de componentes

```bash
endo-dsl library                        # lista todos
endo-dsl library --bloom Analisar       # filtrar por Bloom
endo-dsl library --type quiz            # filtrar por tipo
```

---

## Linguagem DSL

A DSL segue a gramática EBNF em `endo_dsl/dsl/grammar.ebnf`.

```endo
game "Nome do Jogo" {
  metadata {
    domain: "Matemática"
    bloom: Analisar
    age_range: "10-11"
    duration: 15
  }

  objective "Descreva o objetivo de aprendizagem"

  mechanic nome_mecanica {
    type: quiz          // quiz | classify | order | match | ...
    bloom: Lembrar
    params {
      questions: 5
      attempts: 2
    }
  }

  loop {
    start -> nome_mecanica
    nome_mecanica -> end
  }
}
```

### Tipos de mecânicas suportados

| Tipo | Bloom afins |
|------|------------|
| `quiz` | Lembrar, Compreender |
| `classify` | Analisar |
| `order` | Aplicar, Analisar |
| `match` | Compreender, Aplicar |
| `simulation` | Aplicar, Criar |
| `debate` | Avaliar, Criar |
| `portfolio` | Criar |
| ... | |

---

## Arquitetura

```
endo_dsl/
├── dsl/           # Parser, validador semântico, AST, gramática
├── db/            # SQLite (schema.sql, Database)
├── library/       # Repositório de componentes, busca, curadoria
├── agents/        # Pipeline multi-agente (recuperação → geração → validação)
├── compiler/      # Compilador → HTML5, rastreabilidade, reparametrização
├── evaluation/    # Instrumento Likert 7D, relatórios comparativos
├── web/           # Servidor HTTP (stdlib), views HTML, assets estáticos
├── platform.py    # Fachada unificada da plataforma
├── cli.py         # Interface de linha de comando
└── demo.py        # Demonstração ponta-a-ponta
```

---

## Requisitos Funcionais Implementados

| RF | Descrição |
|----|-----------|
| RF01 | Gramática EBNF formal |
| RF02 | Taxonomia de Bloom como construto de primeira classe |
| RF03 | Parser com mensagens de erro descritivas |
| RF04 | Validador semântico (coerência Bloom × tipo de mecânica) |
| RF05 | Estúdio web com validação em tempo real |
| RF06 | Documentação de limites da gramática |
| RF07–RF12 | Biblioteca de componentes com CRUD, busca, versionamento, curadoria |
| RF13 | Estruturação do contexto de design (DesignContext) |
| RF14 | Recuperação semântica por similaridade |
| RF15–RF16 | Geração de DSL via pipeline multi-agente |
| RF17 | Loop iterativo de refinamento com histórico |
| RF18 | Métricas de geração |
| RF19–RF21 | Compilação para protótipo HTML5 jogável |
| RF22 | Reparametrização de domínio |
| RF23 | Rastreabilidade (DSL → protótipo) |
| RF24 | Instrumento de avaliação pedagógica (7 dimensões) |
| RF25 | Armazenamento e exportação de avaliações |
| RF26 | Relatórios comparativos (auto × manual, Bloom, domínio) |

---

## Licença

MIT — veja [LICENSE](LICENSE) para detalhes.
