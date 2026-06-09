# Manual de Comandos — Endo-DSL

> **Referência completa da interface de linha de comando (CLI) da plataforma Endo-DSL**,
> desenvolvida no PESC/COPPE/UFRJ. Cobre todos os comandos implementados, flags globais,
> variáveis de ambiente, códigos de saída, receitas de uso e a invocação via `python -m endo_dsl`.

A CLI é instalada via `pip install -e .` e expõe o executável `endo-dsl`. Também pode ser
invocada como módulo Python (`python -m endo_dsl`) quando o pacote não está no `PATH`.

---

## Sumário

1. [Tabela de referência rápida](#1-tabela-de-referência-rápida)
2. [Flags globais](#2-flags-globais)
3. [Variáveis de ambiente](#3-variáveis-de-ambiente)
4. [Invocação como módulo Python](#4-invocação-como-módulo-python)
5. [Completion de shell](#5-completion-de-shell)
6. [Referência detalhada dos comandos](#6-referência-detalhada-dos-comandos)
   - 6.1 `validate`
   - 6.2 `compile`
   - 6.3 `generate`
   - 6.4 `library`
   - 6.5 `curate`
   - 6.6 `reparametrize`
   - 6.7 `report`
   - 6.8 `grammar`
   - 6.9 `limits`
   - 6.10 `serve`
   - 6.11 `demo`
   - 6.12 `init-db`
   - 6.13 `seed-components`
   - 6.14 `new`
   - 6.15 `lint`
   - 6.16 `fmt`
   - 6.17 `stats`
   - 6.18 `export`
   - 6.19 `import`
   - 6.20 `config`
   - 6.21 `theme`
   - 6.22 `watch`
   - 6.23 `doctor`
7. [Compilador avulso — `endo-dslc`](#7-compilador-avulso--endo-dslc)
8. [Cenários de uso típico](#8-cenários-de-uso-típico)
   - 8.1 Professor elaborando quiz para aula
   - 8.2 Pesquisador exportando biblioteca em lote
   - 8.3 Curador revisando e aprovando componentes

---

## 1. Tabela de referência rápida

### 1.1 Comandos de criação e validação de especificações

| Comando | Descrição resumida | RF |
|---------|--------------------|-----|
| `endo-dsl validate <arquivo>` | Valida sintaxe e semântica de um `.endo` | RF03/RF04 |
| `endo-dsl compile <arquivo>` | Compila DSL → protótipo HTML5 autocontido | RF19–RF23 |
| `endo-dsl generate …` | Pipeline multi-agente: recupera, gera e valida DSL | RF13–RF18 |
| `endo-dsl new <nome>` | Cria um arquivo `.endo` a partir de um modelo | — |
| `endo-dsl lint <arquivo>` | Linting com severidades (erros + avisos de estilo) | RF03/RF04 |
| `endo-dsl fmt <arquivo>` | Formata canonicamente um arquivo `.endo` | — |
| `endo-dsl watch <arquivo>` | Recompila ao detectar alteração no arquivo | RF19 |

### 1.2 Comandos da biblioteca de componentes

| Comando | Descrição resumida | RF |
|---------|--------------------|-----|
| `endo-dsl library list` | Lista componentes com filtros | RF07–RF09 |
| `endo-dsl library search` | Sinônimo de `list` com filtros de texto | RF09 |
| `endo-dsl library seed` | Cadastra os componentes canônicos de referência | RF07 |
| `endo-dsl library show <chave>` | Exibe um componente em JSON | RF08 |
| `endo-dsl seed-components` | Atalho ergonômico para `library seed` | RF07 |
| `endo-dsl curate list` | Lista a fila de curadoria | RF12 |
| `endo-dsl curate approve <id>` | Promove componente a canônico | RF12 |
| `endo-dsl curate reject <id>` | Rejeita componente experimental | RF12 |
| `endo-dsl export` | Exporta a biblioteca para JSON | RF07 |
| `endo-dsl import` | Importa componentes de um JSON | RF07 |

### 1.3 Comandos de configuração e diagnóstico

| Comando | Descrição resumida | RF |
|---------|--------------------|-----|
| `endo-dsl config get <chave>` | Lê uma configuração (chave pontilhada) | — |
| `endo-dsl config set <chave> <valor>` | Define uma configuração persistente | — |
| `endo-dsl config list` | Lista todas as configurações efetivas | — |
| `endo-dsl config reset` | Restaura configurações para os padrões | — |
| `endo-dsl config path` | Imprime o caminho do arquivo de configuração | — |
| `endo-dsl theme list` | Lista os temas disponíveis | — |
| `endo-dsl theme show <nome>` | Exibe o CSS de um tema | — |
| `endo-dsl theme set <nome>` | Define o tema ativo | — |
| `endo-dsl doctor` | Diagnóstico do ambiente de instalação | — |
| `endo-dsl stats` | Métricas de uso da plataforma | — |

### 1.4 Comandos de infraestrutura e relatórios

| Comando | Descrição resumida | RF |
|---------|--------------------|-----|
| `endo-dsl init-db` | Inicializa/cria o banco de dados SQLite | — |
| `endo-dsl serve` | Inicia o servidor web embutido | — |
| `endo-dsl demo` | Executa demonstração fim-a-fim da plataforma | — |
| `endo-dsl report` | Relatório comparativo automático × manual | RF24–RF26 |
| `endo-dsl reparametrize <id>` | Troca domínio de protótipo sem recompilar | RF22 |
| `endo-dsl grammar` | Imprime a gramática EBNF da DSL | RF01/RF02 |
| `endo-dsl limits` | Imprime os limites formais da gramática | RF06 |

---

## 2. Flags globais

As flags globais vêm **sempre antes** do subcomando:
```
endo-dsl [FLAGS GLOBAIS] <subcomando> [opções do subcomando]
```

| Flag | Tipo | Padrão | Descrição |
|------|------|--------|-----------|
| `--version` | flag | — | Imprime `Endo-DSL <versão>` e sai |
| `--db <caminho>` | string | (ver env) | Caminho explícito do banco SQLite. Sobrepõe `ENDO_DSL_DB` e `config.db_path`. Use `:memory:` para banco temporário em memória |
| `--theme <nome>` | string | (ver config) | Tema de interface a usar. Sobrepõe `ENDO_DSL_THEME` e `config.theme`. Valores: `endo`, `light`, `dark`, `solarized`, `high-contrast` |
| `--backend <nome>` | escolha | (ver config) | Backend LLM. Valores: `template` (heurístico, sem rede), `claude` (requer `ANTHROPIC_API_KEY`). Sobrepõe `ENDO_DSL_BACKEND` |
| `--config <caminho>` | string | (ver env) | Caminho explícito do arquivo de configuração JSON do usuário. Sobrepõe `ENDO_DSL_CONFIG` |
| `--quiet` | flag | falso | Suprime todas as mensagens informativas; apenas erros vão para `stderr` |
| `--json` | flag | falso | Quando implementado pelo subcomando, emite saída JSON estruturada em vez de texto legível. Útil para scripts e CI |
| `-h`, `--help` | flag | — | Ajuda do comando ou subcomando |

**Exemplos:**

```bash
# Usar banco isolado para experimento
endo-dsl --db /tmp/exp.sqlite3 compile meu_jogo.endo

# Backend Claude com saída silenciosa (apenas erros saem)
endo-dsl --backend claude --quiet generate --objective "…" --domain "…" --bloom Criar

# Saída JSON para integração com script Python
endo-dsl --json stats | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['prototypes'])"
```

---

## 3. Variáveis de ambiente

Variáveis de ambiente têm **precedência** sobre o arquivo de configuração para as chaves correspondentes, mas são sobrepesadas pelos flags globais de linha de comando.

| Variável | Chave de config equivalente | Descrição |
|----------|---------------------------|-----------|
| `ENDO_DSL_DB` | `db_path` | Caminho-padrão do banco SQLite quando `--db` não é informado. Ex.: `/home/usuario/.endo/endo.sqlite3` |
| `ENDO_DSL_BACKEND` | `backend` | Backend LLM padrão (`template` ou `claude`). Quando `ANTHROPIC_API_KEY` está presente e este não é definido, o sistema promove automaticamente para `claude` |
| `ENDO_DSL_THEME` | `theme` | Tema visual da interface web. Valores aceitos: `endo`, `light`, `dark`, `solarized`, `high-contrast` |
| `ANTHROPIC_API_KEY` | — | Chave de API da Anthropic. Quando presente, habilita o backend `claude` automaticamente (a menos que `ENDO_DSL_BACKEND=template` seja forçado) |
| `ENDO_DSL_CONFIG` | — | Caminho explícito do arquivo de configuração JSON. Sobrepõe a lógica de resolução XDG |
| `XDG_CONFIG_HOME` | — | Diretório-base XDG para arquivos de configuração. Quando definido, o arquivo de configuração fica em `$XDG_CONFIG_HOME/endo-dsl/config.json`. Padrão: `~/.config` |
| `ANTHROPIC_MODEL` | `model` | Nome do modelo Claude a usar. Padrão: `claude-sonnet-4-20250514` |

**Configuração típica para ambiente de pesquisa:**

```bash
# ~/.bashrc ou ~/.zshrc
export ENDO_DSL_DB="$HOME/.endo/pesquisa.sqlite3"
export ANTHROPIC_API_KEY="sk-ant-api03-…"
export ENDO_DSL_BACKEND="claude"
export ENDO_DSL_THEME="dark"
```

**Configuração para CI/CD (sem LLM):**

```bash
export ENDO_DSL_BACKEND=template
export ENDO_DSL_DB=":memory:"
endo-dsl validate examples/fracoes.endo
endo-dsl compile examples/fracoes.endo
```

---

## 4. Invocação como módulo Python

Quando o pacote é importado mas o `endo-dsl` não está no `PATH` (ex.: ambiente virtual não ativado), use a invocação como módulo — funcionalmente idêntica:

```bash
python -m endo_dsl <subcomando> [opções]
```

**Exemplos equivalentes:**

```bash
# Via executável instalado
endo-dsl validate examples/fracoes.endo

# Via módulo Python (não requer PATH)
python -m endo_dsl validate examples/fracoes.endo

# Com interpretador explícito (útil em scripts de automação)
/usr/bin/python3.11 -m endo_dsl --db /tmp/test.db compile arquivo.endo

# Em um script de CI que não ativa o venv
.venv/bin/python -m endo_dsl doctor
```

**Verificação da instalação:**

```bash
python -m endo_dsl --version
# Endo-DSL 1.1.0
```

---

## 5. Completion de shell

A CLI usa `argparse`; é possível gerar completion automático com ferramentas de terceiros:

**Bash (via `argcomplete`):**

```bash
pip install argcomplete
eval "$(register-python-argcomplete endo-dsl)"
# Para persistir: adicione a linha acima ao ~/.bashrc
```

**Zsh (via `argcomplete`):**

```bash
pip install argcomplete
autoload -U bashcompinit && bashcompinit
eval "$(register-python-argcomplete endo-dsl)"
```

**Fish:** Use `fish_complete` com o wrapper de argparse ou configure manualmente em `~/.config/fish/completions/endo-dsl.fish`.

Após a configuração, `endo-dsl <Tab>` lista os subcomandos e `endo-dsl validate <Tab>` mostra arquivos `.endo` disponíveis.

---

## 6. Referência detalhada dos comandos

> **Convenção de códigos de saída**
> - `0` — sucesso
> - `1` — falha de validação, compilação, dado ausente ou erro recuperável
> - `2` — uso incorreto da CLI (argumentos inválidos, tratados pelo `argparse`)
> - `130` — interrupção por `Ctrl+C`

---

### 6.1 `validate` — validação sintática e semântica (RF03/RF04)

**Sinopse:**
```
endo-dsl [--db DB] [--json] validate <arquivo.endo>
```

**Descrição.** Lê o arquivo `.endo`, executa o *parser* recursivo descendente (RF03) e depois
a validação semântica completa (RF04): verificação de coerência cognitiva Bloom×mecânica,
referências de objetivos, tipos de mecânica, alvos de transição em loops, alvos de escolhas
em narrativas. Não gera nenhum artefato de saída. Erros vão para `stderr`; avisos (warnings)
que não impedem o sucesso vão para `stdout` e não alteram o código de saída.

**Flags específicas:** nenhuma além das globais. O único argumento posicional é o caminho do arquivo.

**Exemplo 1 — especificação válida com aviso pedagógico:**
```bash
$ endo-dsl validate examples/fracoes.endo
✓ Especificação válida: 'Comparando Frações' (Bloom: Analisar, Lembrar)
  1 aviso(s):
  [WARNING] mecânica 'revisao' (Lembrar) está abaixo do nível-alvo da sessão (Analisar)
         → considere uma mecânica com afinidade a Analisar: classification, comparison
```

**Exemplo 2 — erro de tipo de mecânica desconhecido:**
```bash
$ endo-dsl validate meu_jogo_quebrado.endo
✗ Especificação inválida:
  [ERROR] mecânica 'desafio1' tem tipo desconhecido 'adventure' (linha 18, col 12)
         → tipos disponíveis na biblioteca: classification, comparison, matching,
           narrative_branch, puzzle, quiz, sequencing, sorting
```

**Exemplo 3 — saída JSON para script de CI:**
```bash
$ endo-dsl --json validate examples/fracoes.endo
{
  "file": "examples/fracoes.endo",
  "ok": true,
  "issues": [
    {
      "severity": "warning",
      "message": "mecânica 'revisao' (Lembrar) abaixo do nível-alvo (Analisar)",
      "suggestion": "considere classification ou comparison"
    }
  ]
}
```

**Códigos de saída:** `0` — válido (com ou sem avisos) · `1` — inválido (com erros)

---

### 6.2 `compile` — compilação DSL → HTML5 (RF19–RF23)

**Sinopse:**
```
endo-dsl [--db DB] [--quiet] [--json] compile <arquivo.endo> [--origin {manual,auto,hybrid}]
```

**Descrição.** Compila a especificação DSL em um protótipo HTML5 **autocontido** (zero
dependências externas em runtime — RF19). O processo: (1) *parse* do arquivo; (2) validação
semântica; (3) construção do *content pack*; (4) renderização HTML5 com as mecânicas; (5)
geração do documento de rastreabilidade pedagógica (RF23); (6) persistência da especificação
e do protótipo no banco SQLite; (7) escrita dos artefatos em `<workspace>/proto_<id>/`.

Artefatos gerados:

| Arquivo | Descrição |
|---------|-----------|
| `prototype.html` | Jogo HTML5 jogável no navegador |
| `prototype.traceability.html` | Rastreabilidade pedagógica (objetivo → mecânica → Bloom) |
| `prototype.traceability.json` | Rastreabilidade em JSON estruturado |
| `prototype.content.json` | *Content pack* para reparametrização (RF22) |

**Flags específicas:**

| Flag | Tipo | Padrão | Descrição |
|------|------|--------|-----------|
| `--origin` | escolha | `manual` | Origem registrada do protótipo. Valores: `manual` (escrito pelo usuário), `auto` (gerado pelo pipeline), `hybrid` (gerado e editado). Usado na comparação auto×manual do relatório (RF26) |

**Exemplo 1 — compilação bem-sucedida:**
```bash
$ endo-dsl compile examples/fracoes.endo
✓ Protótipo #17 compilado: Comparando Frações
                html: /home/usuario/.endo/prototypes/proto_17/prototype.html
   traceability_html: /home/usuario/.endo/prototypes/proto_17/prototype.traceability.html
   traceability_json: /home/usuario/.endo/prototypes/proto_17/prototype.traceability.json
        content_pack: /home/usuario/.endo/prototypes/proto_17/prototype.content.json
  1 aviso(s) pedagógico(s):
  [WARNING] mecânica 'revisao' (Lembrar) abaixo do nível-alvo (Analisar)

  Abra no navegador: file:///home/usuario/.endo/prototypes/proto_17/prototype.html
```

**Exemplo 2 — compilação de protótipo automático (para fins de avaliação comparativa):**
```bash
$ endo-dsl compile saida_gerada.endo --origin auto
✓ Protótipo #18 compilado: Jogando com Probabilidades
                html: /home/usuario/.endo/prototypes/proto_18/prototype.html
   traceability_html: /home/usuario/.endo/prototypes/proto_18/prototype.traceability.html
   traceability_json: /home/usuario/.endo/prototypes/proto_18/prototype.traceability.json
        content_pack: /home/usuario/.endo/prototypes/proto_18/prototype.content.json

  Abra no navegador: file:///home/usuario/.endo/prototypes/proto_18/prototype.html
```

**Exemplo 3 — falha de compilação com sugestão de biblioteca (RF20):**
```bash
$ endo-dsl compile sem_tipo.endo
✗ Falha de compilação:
  [ERROR] mecânica 'm_principal' não declara campo 'type' (linha 12, col 3)
         → a biblioteca oferece 'quiz' (Quiz) com afinidade a Lembrar, Compreender;
           tipos disponíveis: classification, comparison, matching, puzzle, quiz,
           sequencing, sorting, narrative_branch
```

**Códigos de saída:** `0` — compilado · `1` — erro de compilação ou sintaxe

---

### 6.3 `generate` — pipeline multi-agente (RF13–RF18)

**Sinopse:**
```
endo-dsl [--db DB] [--backend BACKEND] [--quiet] [--json] generate
    --objective <texto>
    --domain <área>
    --bloom <nível>
    [--topic <tópico>]
    [--age <faixa>]
    [--level <escolaridade>]
    [--duration <minutos>]
    [--name <nome_da_sessão>]
    [--components <chave1,chave2,...>]
    [--from-scratch]
    [--compile]
    [--out <arquivo.endo>]
```

**Descrição.** Executa o pipeline multi-agente completo:
1. **Fase 1 — Contexto:** cria uma sessão de design no banco com os parâmetros informados.
2. **Fase 2 — Recuperação (RAG):** busca componentes pedagógicos afins na biblioteca por similaridade (bloom + tipo de mecânica + domínio). Ignorado se `--from-scratch`.
3. **Fase 3 — Geração:** o backend LLM (heurístico ou Claude) gera a especificação DSL usando o contexto e os componentes recuperados como guias.
4. **Fase 4 — Validação + refinamento:** valida sintaticamente e semanticamente; se inválida, tenta gerar novamente (até 3 tentativas).
5. **(Opcional)** Compilação direta com `--compile`.

O backend heurístico (`template`) não requer rede nem chave de API e é **determinístico** — adequado para experimentos reprodutíveis.

**Flags específicas:**

| Flag | Obrigatória | Tipo | Descrição |
|------|:-----------:|------|-----------|
| `--objective` | **sim** | string | Objetivo de aprendizagem em linguagem natural. Ex.: `"comparar frações com denominadores diferentes"` |
| `--domain` | **sim** | string | Área de conhecimento. Ex.: `"Matemática"`, `"Ciências"`, `"História"` |
| `--bloom` | **sim** | string | Nível de Bloom alvo. Valores: `Lembrar`, `Compreender`, `Aplicar`, `Analisar`, `Avaliar`, `Criar` |
| `--topic` | não | string | Tópico específico dentro do domínio. Padrão: igual ao domínio |
| `--age` | não | string | Faixa etária. Ex.: `"10-11"`, `"12-14"` |
| `--level` | não | string | Nível de escolaridade. Ex.: `"5º ano"`, `"Ensino Médio"` |
| `--duration` | não | inteiro | Duração estimada em minutos |
| `--name` | não | string | Nome descritivo para a sessão de design. Padrão: `"Sessão: <domínio>"` |
| `--components` | não | string | Chaves de componentes específicos a usar, separadas por vírgula. Ex.: `"quiz.basic.recall,classification.fractions"` |
| `--from-scratch` | não | flag | Gera sem recuperar nem usar componentes da biblioteca |
| `--compile` | não | flag | Se a DSL gerada for válida, compila imediatamente e imprime o caminho do HTML |
| `--out` | não | caminho | Salva a DSL gerada em um arquivo `.endo` |

**Exemplo 1 — geração completa com biblioteca e compilação automática:**
```bash
$ endo-dsl generate \
    --objective "comparar frações com denominadores diferentes" \
    --domain "Matemática" \
    --bloom Analisar \
    --age "10-11" \
    --level "5º ano" \
    --duration 15 \
    --compile \
    --out saidas/fracoes_auto.endo

Sessão #4 criada. Backend LLM: template
Geração ✓ válida em 1 tentativa(s) — 2 mecânicas, 1 loop, 0 erros
Componentes usados: classification.fractions, quiz.basic.recall

--- Especificação DSL gerada ---
game "Comparando Frações" {
  metadata {
    domain: "Matemática"
    topic: "frações"
    bloom: Analisar
    age_range: "10-11"
    duration: 15
  }
  objective obj_principal {
    description: "Comparar frações com denominadores diferentes usando equivalência"
    bloom: Analisar
  }
  ...
}

Salvo em saidas/fracoes_auto.endo

✓ Compilado: /home/usuario/.endo/prototypes/proto_5/prototype.html

Métricas de geração: {
  "session_id": 4,
  "attempts": 1,
  "valid": true,
  "components_used": 2,
  "backend": "template"
}
```

**Exemplo 2 — geração do zero com backend Claude:**
```bash
$ endo-dsl --backend claude generate \
    --objective "avaliar argumentos em debate científico" \
    --domain "Ciências" \
    --bloom Avaliar \
    --age "14-15" \
    --from-scratch \
    --out saidas/debate_ciencias.endo

Sessão #7 criada. Backend LLM: claude
Geração ✓ válida em 2 tentativa(s) — 3 mecânicas, 1 loop, 0 erros

--- Especificação DSL gerada ---
game "Debatendo Ciências" {
  metadata { ... }
  ...
}

Salvo em saidas/debate_ciencias.endo

Métricas de geração: {
  "session_id": 7,
  "attempts": 2,
  "valid": true,
  "components_used": 0,
  "backend": "claude"
}
```

**Exemplo 3 — geração com componentes específicos selecionados:**
```bash
$ endo-dsl generate \
    --objective "identificar tipos de solo" \
    --domain "Ciências" \
    --bloom Lembrar \
    --components "quiz.basic.recall,matching.categories"

Sessão #9 criada. Backend LLM: template
Geração ✓ válida em 1 tentativa(s) — 2 mecânicas, 1 loop, 0 erros
Componentes usados: quiz.basic.recall, matching.categories
...
```

**Códigos de saída:** `0` — DSL gerada e válida · `1` — inválida após todas as tentativas

---

### 6.4 `library` — biblioteca de componentes (RF07–RF12)

**Sinopse:**
```
endo-dsl [--db DB] [--json] library {list|search|seed|show} [chave]
    [--text <texto>]
    [--bloom <nível>]
    [--type <tipo>]
    [--domain <domínio>]
    [--status {canonical,experimental}]
    [--force]
```

**Descrição.** Gerencia o catálogo de componentes pedagógicos reutilizáveis. Os componentes
são a unidade de reúso da plataforma: cada um contém uma assinatura DSL, metadados de Bloom,
tipo de mecânica, parâmetros configuráveis, referências bibliográficas (RF08), histórico de
versões (RF10) e métricas de uso/qualidade (RF11).

| Ação | Efeito |
|------|--------|
| `list` | Lista todos os componentes, opcionalmente filtrados |
| `search` | Sinônimo de `list` (alias mais intuitivo para busca textual) |
| `seed` | Cadastra ou recria os componentes canônicos de referência no banco |
| `show <chave>` | Imprime o componente identificado por `<chave>` em JSON |

**Flags de filtro** (para `list`/`search`):

| Flag | Descrição |
|------|-----------|
| `--text` | Filtro textual (busca em nome e descrição) |
| `--bloom` | Filtra por nível de Bloom. Ex.: `Analisar` |
| `--type` | Filtra por tipo de mecânica. Ex.: `classification` |
| `--domain` | Filtra por domínio de conhecimento. Ex.: `Matemática` |
| `--status` | Filtra por status: `canonical` ou `experimental` |
| `--force` | (somente `seed`) Recria componentes mesmo que já existam |

**Exemplo 1 — popular e listar por nível de Bloom:**
```bash
$ endo-dsl library seed
14 componente(s) canônico(s) cadastrado(s).

$ endo-dsl library list --bloom Analisar
3 componente(s):
  ★ classification.fractions          Analisar     classification  ⟨4.2⟩
  ★ comparison.pairs                  Analisar     comparison      ⟨3.9⟩
  ○ sorting.timeline                  Analisar     sorting

  ★ canônico · ○ experimental
```

**Exemplo 2 — busca textual e por domínio:**
```bash
$ endo-dsl library search --text "quiz" --domain "Matemática" --status canonical
2 componente(s):
  ★ quiz.basic.recall                 Lembrar      quiz            ⟨4.0⟩
  ★ quiz.applied.math                 Aplicar      quiz            ⟨3.7⟩

  ★ canônico · ○ experimental
```

**Exemplo 3 — detalhes completos de um componente:**
```bash
$ endo-dsl library show quiz.basic.recall
{
  "id": 3,
  "key": "quiz.basic.recall",
  "name": "Quiz de Fixação — Nível Básico",
  "bloom_level": "Lembrar",
  "mechanic_type": "quiz",
  "status": "canonical",
  "current_version": 2,
  "description": "Quiz de múltipla escolha para fixação de conceitos factuais.",
  "dsl_signature": "mechanic m { type: quiz; bloom: Lembrar; params { questions: 5 } }",
  "params": { "questions": 5, "attempts": 2 },
  "domain": "genérico",
  "author": "endo-dsl-core",
  "references": ["Anderson & Krathwohl (2001)", "Lopes et al. (2023)"],
  "metrics": {
    "instantiations": 42,
    "avg_rating": 4.0,
    "rating_count": 11,
    "compile_success_rate": 0.97
  }
}
```

**Códigos de saída:** `0` — sucesso · `1` — componente não encontrado (em `show`)

---

### 6.5 `curate` — curadoria de componentes (RF12)

**Sinopse:**
```
endo-dsl [--db DB] curate {list|approve|reject} [id]
    [--curator <nome/email>]
    [--note <justificativa>]
```

**Descrição.** Materializa a **jornada do curador**: revisa componentes experimentais submetidos
pela comunidade e os promove a canônicos ou os rejeita, registrando curador e justificativa
numa trilha de curadoria auditável (RF12). Componentes canônicos são priorizados pelo Agente
de Recuperação (RF14).

| Ação | Efeito |
|------|--------|
| `list` | Lista os componentes experimentais aguardando revisão |
| `approve <id>` | Promove o componente `<id>` ao status `canonical` |
| `reject <id>` | Muda o status para `rejected` e registra a justificativa |

**Flags:**

| Flag | Descrição |
|------|-----------|
| `--curator` | Identificador do curador (nome ou e-mail). Registrado na trilha auditável |
| `--note` | Justificativa da decisão (aprovação ou rejeição) |

**Exemplo 1 — listar a fila de curadoria:**
```bash
$ endo-dsl curate list
4 componente(s) na fila de curadoria:
  #18 classification.fractions.adv   Analisar     classification  (instâncias: 6)
  #21 puzzle.build.open              Criar        puzzle          (instâncias: 4)
  #23 matching.synonyms.pt           Compreender  matching        (instâncias: 2)
  #27 sequencing.water.cycle         Aplicar      sequencing      (instâncias: 1)
```

**Exemplo 2 — aprovar componente com justificativa:**
```bash
$ endo-dsl curate approve 18 \
    --curator "ana.silva@cos.ufrj.br" \
    --note "Alinhamento Bloom verificado em 6 instâncias; params bem documentados"
✓ componente #18 promovido a canônico.
```

**Exemplo 3 — rejeitar componente com motivo:**
```bash
$ endo-dsl curate reject 27 \
    --curator "joao.santos@pesc.ufrj.br" \
    --note "Tipo de mecânica inconsistente com Bloom Aplicar; nível correto seria Lembrar"
✗ componente #27 rejeitado.
```

**Códigos de saída:** `0` — sucesso · `2` — ação não reconhecida

---

### 6.6 `reparametrize` — troca de domínio sem recompilar (RF22)

**Sinopse:**
```
endo-dsl [--db DB] reparametrize <prototype_id> --domain <domínio> [--topic <tópico>]
```

**Descrição.** Substitui o conteúdo embutido de um protótipo **já compilado**, preservando
integralmente a estrutura (mecânicas, interações, fluxo, níveis de Bloom) e alterando apenas
o domínio de conhecimento. O resultado é um novo arquivo `prototype.reparam.html` ao lado do
original. Permite reutilizar um mesmo design pedagógico em múltiplos domínios curriculares
(RF22).

**Mecanismo técnico:** o compilador emite um bloco `<script id="endo-content" type="application/json">`
com o *content pack* do jogo. A reparametrização extrai e reescreve esse bloco JSON com
conteúdo de outro domínio, sem reprocessar a estrutura DSL.

**Flags:**

| Flag | Obrigatória | Descrição |
|------|:-----------:|-----------|
| `--domain` | **sim** | Novo domínio de conhecimento |
| `--topic` | não | Tópico específico no novo domínio |

**Exemplo 1 — migrar jogo de Matemática para Ciências:**
```bash
$ endo-dsl reparametrize 17 --domain "Ciências" --topic "classificação de rochas"
✓ Protótipo #17 reparametrizado para 'Ciências'.
  /home/usuario/.endo/prototypes/proto_17/prototype.reparam.html
```

**Exemplo 2 — migrar para História:**
```bash
$ endo-dsl reparametrize 17 --domain "História" --topic "períodos históricos do Brasil"
✓ Protótipo #17 reparametrizado para 'História'.
  /home/usuario/.endo/prototypes/proto_17/prototype.reparam.html
```

**Exemplo 3 — verificar o resultado abrindo no navegador:**
```bash
$ endo-dsl reparametrize 17 --domain "Português" --topic "classes gramaticais"
✓ Protótipo #17 reparametrizado para 'Português'.
  /home/usuario/.endo/prototypes/proto_17/prototype.reparam.html
$ xdg-open /home/usuario/.endo/prototypes/proto_17/prototype.reparam.html
```

**Códigos de saída:** `0` — sucesso · `1` — protótipo não encontrado

---

### 6.7 `report` — relatório comparativo (RF24–RF26)

**Sinopse:**
```
endo-dsl [--db DB] report [--csv]
```

**Descrição.** Gera e imprime o relatório comparativo entre protótipos **automáticos** e
**manuais** nas sete dimensões do instrumento `endo-eval-1.0` (RF24). O relatório mostra:
médias gerais e por dimensão, deltas auto−manual, desagregação por nível de Bloom e por
domínio, e uma interpretação textual gerada automaticamente.

Com `--csv`, exporta as avaliações brutas em CSV (RF25) para análise estatística externa
(ex.: t-test ou Mann-Whitney no R/Python).

**Flags:**

| Flag | Descrição |
|------|-----------|
| `--csv` | Exporta as avaliações em CSV para `stdout` (RF25) |

**Exemplo 1 — relatório textual completo:**
```bash
$ endo-dsl report
RELATÓRIO COMPARATIVO  (auto n=12 · manual n=9)
══════════════════════════════════════════════════════════
Média geral:  auto 3.86  ·  manual 4.12  ·  Δ -0.26
Interpretação: protótipos automáticos aproximam-se dos manuais;
               diferença pequena, possivelmente não significativa.

Por dimensão:
  Alinhamento pedagógico       auto 3.90  manual 4.20  Δ -0.30
  Coerência cognitiva (Bloom)  auto 4.30  manual 4.10  Δ +0.20
  Endogeneidade                auto 3.70  manual 4.00  Δ -0.30
  Clareza instrucional         auto 3.80  manual 4.15  Δ -0.35
  Adequação ao público         auto 4.00  manual 4.25  Δ -0.25
  Potencial de engajamento     auto 3.65  manual 4.00  Δ -0.35
  Adaptabilidade de conteúdo   auto 4.10  manual 4.20  Δ -0.10

Por nível de Bloom:
  Analisar  auto 3.95 (n=5)  manual 4.18 (n=4)
  Lembrar   auto 3.75 (n=4)  manual 4.05 (n=3)
  Criar     auto 3.88 (n=3)  manual 4.12 (n=2)

Por domínio:
  Matemática  auto 3.92 (n=6)  manual 4.20 (n=5)
  Ciências    auto 3.78 (n=4)  manual 4.00 (n=3)
  Português   auto 3.85 (n=2)  manual 4.05 (n=1)
```

**Exemplo 2 — exportação para análise estatística:**
```bash
$ endo-dsl report --csv > dados/avaliacoes_$(date +%Y%m%d).csv
$ head -2 dados/avaliacoes_20260609.csv
prototype_id,origin,evaluator,bloom_level,domain,pedagogical_alignment,bloom_coherence,endogeneity,instructional_clarity,audience_fit,engagement_potential,content_adaptability,overall_weighted,created_at
17,auto,ana.silva,Analisar,Matemática,4,5,3,4,4,3,4,3.91,2026-06-09T14:23:11
```

**Exemplo 3 — análise rápida com Python:**
```bash
$ endo-dsl report --csv | python3 -c "
import csv, sys
rows = list(csv.DictReader(sys.stdin))
auto   = [float(r['overall_weighted']) for r in rows if r['origin']=='auto']
manual = [float(r['overall_weighted']) for r in rows if r['origin']=='manual']
print(f'Auto: {sum(auto)/len(auto):.2f} | Manual: {sum(manual)/len(manual):.2f}')
"
Auto: 3.86 | Manual: 4.12
```

**Códigos de saída:** `0` sempre

---

### 6.8 `grammar` — gramática formal (RF01/RF02)

**Sinopse:**
```
endo-dsl grammar
```

**Descrição.** Imprime para `stdout` a gramática EBNF completa da Endo-DSL, diretamente do
arquivo `endo_dsl/dsl/grammar.ebnf`. Útil para referência rápida, para incluir em documentos
acadêmicos ou para verificar qual versão da gramática está instalada.

**Exemplo 1 — exibir gramática completa:**
```bash
$ endo-dsl grammar
(* ===================================================================== *)
(* Gramática formal da Endo-DSL  —  RF01, RF02                            *)
(* ... *)
spec            = game_decl ;
game_decl       = "game" , string , "{" , { game_member } , "}" ;
...
```

**Exemplo 2 — extrair para arquivo e incluir no LaTeX:**
```bash
$ endo-dsl grammar > docs/grammar.ebnf
$ wc -l docs/grammar.ebnf
82 docs/grammar.ebnf
```

**Exemplo 3 — verificar o não-terminal `bloom`:**
```bash
$ endo-dsl grammar | grep "bloom"
bloom           = "Lembrar" | "Compreender" | "Aplicar"
                | "Analisar" | "Avaliar"    | "Criar" ;
```

**Códigos de saída:** `0` sempre

---

### 6.9 `limits` — limites da formalização (RF06)

**Sinopse:**
```
endo-dsl limits
```

**Descrição.** Imprime em Markdown os **limites formais** da gramática: quais construtos do
Endo-GDC são diretamente formalizáveis e verificáveis pela gramática, quais são parcialmente
formalizáveis (estrutura sim, qualidade não) e quais dependem deliberadamente de interpretação
humana. Responde à Questão de Pesquisa QP1.

**Exemplo 1 — exibir limites:**
```bash
$ endo-dsl limits
# Limites Formais da Gramática Endo-DSL (RF06)

Resposta à Questão de Pesquisa **Q1**: *quais construtos do Endo-GDC são
formalizáveis numa gramática computacional e quais dependem de interpretação humana?*

## Formalizados (verificáveis pela gramática)
- **Mecânicas de jogo (tipo)** — O tipo de mecânica é um enum fechado e verificável ...
- **Objetivos pedagógicos** — Declarados como entidades nomeadas com nível de Bloom ...
...

## Parcialmente formalizados (estrutura sim, qualidade não)
- **Coerência pedagógica mecânica-objetivo** — A gramática verifica alinhamento ...
...

## Não formalizados (controle humano deliberado)
- **Engajamento percebido** — É um constructo psicológico subjetivo ...
...
```

**Exemplo 2 — usar como referência em relatório:**
```bash
$ endo-dsl limits >> relatorio_tecnico.md
```

**Códigos de saída:** `0` sempre

---

### 6.10 `serve` — interface web

**Sinopse:**
```
endo-dsl [--db DB] [--theme TEMA] serve [--host HOST] [--port PORTA]
```

**Descrição.** Inicia o servidor HTTP embutido (stdlib pura, sem Flask/Django) que serve a
interface web completa da plataforma nas rotas: `/` (dashboard), `/studio`, `/library`,
`/component/<chave>`, `/curator`, `/report`, `/docs`, `/prototype/<id>`, `/evaluate/<id>`.
O servidor usa o banco SQLite especificado (ou o padrão) e inicializa a biblioteca de
componentes canônicos se ainda não existirem.

**Flags:**

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--host` | `127.0.0.1` | Interface de rede a escutar. Use `0.0.0.0` para acesso externo/rede local |
| `--port` | `8000` | Porta TCP |

**Exemplo 1 — servidor local padrão:**
```bash
$ endo-dsl serve
Endo-DSL servindo em http://127.0.0.1:8000  (Ctrl+C para parar)
Backend LLM: template  ·  banco: /home/usuario/.endo/endo_dsl.sqlite3
```

**Exemplo 2 — servidor acessível na rede local:**
```bash
$ endo-dsl serve --host 0.0.0.0 --port 8080
Endo-DSL servindo em http://0.0.0.0:8080  (Ctrl+C para parar)
Backend LLM: claude  ·  banco: /home/usuario/.endo/endo_dsl.sqlite3
```

**Exemplo 3 — servidor com banco isolado para experimento:**
```bash
$ endo-dsl --db /tmp/experimento_06.sqlite3 serve --port 9001
Endo-DSL servindo em http://127.0.0.1:9001  (Ctrl+C para parar)
Backend LLM: template  ·  banco: /tmp/experimento_06.sqlite3
```

**Códigos de saída:** `0` ao encerrar (Ctrl+C) · `130` interrupção por sinal

---

### 6.11 `demo` — demonstração fim-a-fim

**Sinopse:**
```
endo-dsl [--db DB] demo
```

**Descrição.** Executa uma demonstração completa automatizada percorrendo todas as seis fases
da plataforma: cria sessão, recupera componentes, gera DSL, valida, compila e registra
avaliação. Útil para verificar a instalação e para apresentações.

**Exemplo:**
```bash
$ endo-dsl demo
[1/6] Criando sessão de design ... ✓ (#1)
[2/6] Recuperando componentes (RAG) ... ✓ (3 componentes)
[3/6] Gerando especificação DSL (backend: template) ... ✓ em 1 tentativa
[4/6] Validando ... ✓ 0 erros, 1 aviso
[5/6] Compilando protótipo HTML5 ... ✓ /home/usuario/.endo/prototypes/proto_1/prototype.html
[6/6] Registrando avaliação de demonstração ... ✓

Demonstração concluída com êxito.
Abra no navegador: file:///home/usuario/.endo/prototypes/proto_1/prototype.html
```

**Códigos de saída:** `0` — demo bem-sucedida · `1` — falha em alguma fase

---

### 6.12 `init-db` — inicialização do banco de dados

**Sinopse:**
```
endo-dsl [--db DB] [--quiet] [--json] init-db [--force]
```

**Descrição.** Cria e inicializa o schema SQLite de forma explícita e idempotente. Normalmente
o banco é inicializado automaticamente na primeira execução de qualquer comando que acesse o
banco; este comando serve para inicializar explicitamente (ex.: em scripts de provisionamento
de ambiente de pesquisa) ou recriar do zero.

**Flags:**

| Flag | Descrição |
|------|-----------|
| `--force` | Remove o arquivo de banco existente e recria do zero. **Atenção:** apaga todos os dados |

**Exemplo 1 — inicialização padrão (idempotente):**
```bash
$ endo-dsl init-db
✓ Banco inicializado em /home/usuario/.endo/endo_dsl.sqlite3
```

**Exemplo 2 — recriar banco do zero:**
```bash
$ endo-dsl init-db --force
Banco anterior removido: /home/usuario/.endo/endo_dsl.sqlite3
✓ Banco inicializado em /home/usuario/.endo/endo_dsl.sqlite3
```

**Exemplo 3 — saída JSON para scripts de provisionamento:**
```bash
$ endo-dsl --json init-db
{
  "db_path": "/home/usuario/.endo/endo_dsl.sqlite3",
  "initialized": true
}
```

**Códigos de saída:** `0` — sucesso

---

### 6.13 `seed-components` — população inicial de componentes

**Sinopse:**
```
endo-dsl [--db DB] [--quiet] [--json] seed-components [--reset]
```

**Descrição.** Atalho ergonômico para cadastrar os componentes canônicos de referência da
plataforma. Equivalente a `library seed` mas com melhor interface de linha de comando e
suporte a `--reset` para limpeza prévia.

**Flags:**

| Flag | Descrição |
|------|-----------|
| `--reset` | Remove todos os componentes existentes antes de repovoar |

**Exemplo 1 — popular biblioteca vazia:**
```bash
$ endo-dsl seed-components
✓ 14 componente(s) cadastrado(s); 14 no total.
```

**Exemplo 2 — reiniciar biblioteca:**
```bash
$ endo-dsl seed-components --reset
Componentes anteriores removidos.
✓ 14 componente(s) cadastrado(s); 14 no total.
```

**Exemplo 3 — saída JSON:**
```bash
$ endo-dsl --json seed-components
{
  "created": 14,
  "total": 14
}
```

**Códigos de saída:** `0` — sucesso

---

### 6.14 `new` — scaffold de arquivo `.endo`

**Sinopse:**
```
endo-dsl [--quiet] [--json] new <nome>
    [--bloom <nível>]
    [--domain <área>]
    [--type <tipo_de_mecânica>]
    [--topic <tópico>]
    [-o <arquivo_de_saída>]
```

**Descrição.** Cria um arquivo `.endo` preenchido com um modelo (template) inicial coerente
com o nível de Bloom, domínio e tipo de mecânica informados. O arquivo gerado contém
comentários e estrutura mínima válida (um objetivo, uma mecânica, um loop), pronto para
edição. Facilita o início do fluxo manual sem partir do zero.

**Flags:**

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--bloom` | config `default_bloom` (padrão: `Analisar`) | Nível de Bloom inicial |
| `--domain` | config `default_domain` (padrão: `Matemática`) | Área de conhecimento |
| `--type` | `classification` | Tipo de mecânica da mecânica inicial |
| `--topic` | igual ao domínio | Tópico específico |
| `-o` / `--output` | `<nome_normalizado>.endo` no diretório atual | Caminho de saída |

**Exemplo 1 — scaffold básico:**
```bash
$ endo-dsl new "Classificando Animais" --bloom Compreender --domain Ciências --type classification
✓ Arquivo criado: classificando_animais.endo
```

**Exemplo 2 — scaffold com saída específica:**
```bash
$ endo-dsl new "Ordenando Eventos" --bloom Analisar --domain História \
    --type sequencing -o projetos/historia/eventos.endo
✓ Arquivo criado: projetos/historia/eventos.endo
```

**Exemplo 3 — conteúdo do arquivo gerado:**
```bash
$ cat classificando_animais.endo
// Classificando Animais — Bloom: Compreender — Domínio: Ciências
// Gerado por `endo-dsl new`. Edite e compile com `endo-dsl compile`.

game "Classificando Animais" {
  metadata {
    domain: "Ciências"
    topic: "Ciências"
    bloom: Compreender
  }

  objective obj_principal {
    description: "Descreva aqui o objetivo de aprendizagem."
    bloom: Compreender
  }

  mechanic mecanica_principal {
    type: classification
    bloom: Compreender
    addresses: obj_principal
    description: "Descreva a mecânica endógena."
    params {
      difficulty: "medium"
    }
  }

  loop principal {
    bloom: Compreender
    description: "Loop central de jogabilidade."
    steps {
      mecanica_principal -> mecanica_principal
    }
  }
}
```

**Códigos de saída:** `0` — arquivo criado

---

### 6.15 `lint` — análise de estilo e boas práticas

**Sinopse:**
```
endo-dsl [--db DB] [--json] lint <arquivo.endo> [--strict]
```

**Descrição.** Combina validação sintática e semântica com verificações de boas práticas:
objetivos sem mecânica que os endereça, mecânicas sem `addresses`, loops sem fechamento de
ciclo, parâmetros não documentados, etc. Diferentemente de `validate`, o `lint` classifica
problemas por **severidade** e pode ser integrado a pipelines de CI/CD com o flag `--strict`.

**Flags:**

| Flag | Descrição |
|------|-----------|
| `--strict` | Trata avisos como erros (saída `1` mesmo sem erros sintáticos) |

**Exemplo 1 — arquivo sem problemas:**
```bash
$ endo-dsl lint examples/fracoes.endo
✓ examples/fracoes.endo: nenhum problema encontrado.
```

**Exemplo 2 — arquivo com avisos (saída padrão):**
```bash
$ endo-dsl lint meu_jogo.endo
meu_jogo.endo: 0 erro(s), 2 aviso(s)
  [WARNING] mecânica 'revisao' não declara 'addresses' (linha 22, col 3)
         → adicione 'addresses: <objetivo>' para manter rastreabilidade
  [WARNING] objetivo 'obj_secundario' não é endereçado por nenhuma mecânica (linha 8, col 3)
         → pode ser um objetivo órfão; remova ou conecte a uma mecânica
```

**Exemplo 3 — modo estrito para CI:**
```bash
$ endo-dsl lint meu_jogo.endo --strict
meu_jogo.endo: 0 erro(s), 2 aviso(s)
  [WARNING] ...
$ echo $?
1
```

**Códigos de saída:** `0` — sem problemas (ou só avisos sem `--strict`) · `1` — erros ou avisos com `--strict`

---

### 6.16 `fmt` — formatação canônica

**Sinopse:**
```
endo-dsl [--quiet] fmt <arquivo.endo> [--write] [--check]
```

**Descrição.** Reformata um arquivo `.endo` para a forma canônica da plataforma: indentação
de 2 espaços, ordem normalizada de campos (metadata → objectives → mechanics → loops →
narratives), espaçamento consistente. O formatador é *best-effort*: preserva a semântica
(verifica equivalência de AST antes de sobrescrever), mas descarta comentários `//` e
normaliza a distinção string/identificador por heurística.

Sem flags, imprime o resultado formatado em `stdout` (não modifica o arquivo).

**Flags:**

| Flag | Descrição |
|------|-----------|
| `--write` | Edita o arquivo no lugar (in-place) |
| `--check` | Apenas verifica se o arquivo já está formatado; retorna `1` se não estiver (útil em CI/pre-commit) |

**Exemplo 1 — preview da formatação:**
```bash
$ endo-dsl fmt meu_jogo.endo
game "Meu Jogo" {
  metadata {
    domain: "Matemática"
    ...
  }
  ...
}
```

**Exemplo 2 — formatar no lugar:**
```bash
$ endo-dsl fmt meu_jogo.endo --write
✓ meu_jogo.endo: formatado.
```

**Exemplo 3 — verificação em pipeline de CI:**
```bash
$ endo-dsl fmt examples/fracoes.endo --check
✓ examples/fracoes.endo: já está formatado.
$ echo $?
0
```

**Códigos de saída:** `0` — arquivo já formatado ou formatação bem-sucedida · `1` — arquivo não formatado (em `--check`) ou erro de sintaxe

---

### 6.17 `stats` — métricas de uso da plataforma

**Sinopse:**
```
endo-dsl [--db DB] [--quiet] [--json] stats
```

**Descrição.** Consulta o banco de dados e exibe contagens agregadas dos principais objetos
da plataforma: componentes (total, canônicos, experimentais), sessões de design, especificações,
protótipos, usos de componentes e avaliações. Útil para monitoramento de pesquisa e relatórios
de acompanhamento.

**Exemplo 1 — estatísticas em texto:**
```bash
$ endo-dsl stats
Métricas da plataforma Endo-DSL
────────────────────────────────────────
  components                        14
  components_canonical              10
  components_experimental            4
  design_sessions                   23
  specifications                    31
  prototypes                        28
  component_usages                  87
  evaluations                       41
```

**Exemplo 2 — saída JSON para monitoramento automatizado:**
```bash
$ endo-dsl --json stats
{
  "components": 14,
  "components_canonical": 10,
  "components_experimental": 4,
  "design_sessions": 23,
  "specifications": 31,
  "prototypes": 28,
  "component_usages": 87,
  "evaluations": 41
}
```

**Exemplo 3 — integração com dashboard de pesquisa:**
```bash
$ endo-dsl --json stats | \
    jq '{"razão_sucesso": (.prototypes / .specifications), "avaliações_por_protótipo": (.evaluations / .prototypes)}'
{
  "razão_sucesso": 0.903,
  "avaliações_por_protótipo": 1.464
}
```

**Códigos de saída:** `0` sempre

---

### 6.18 `export` — exportação da biblioteca

**Sinopse:**
```
endo-dsl [--db DB] [--quiet] export [--out <arquivo.json>]
```

**Descrição.** Exporta todos os componentes da biblioteca para um arquivo JSON portável.
O JSON inclui metadados de versão da plataforma (`version`) e a lista de componentes
(`components`). Pode ser enviado para `stdout` (padrão) ou gravado em arquivo com `--out`.

**Flags:**

| Flag | Descrição |
|------|-----------|
| `--out` | Caminho do arquivo JSON de saída. Se omitido, imprime em `stdout` |

**Exemplo 1 — exportar para arquivo:**
```bash
$ endo-dsl export --out backup_biblioteca_20260609.json
✓ 14 componente(s) exportado(s) para backup_biblioteca_20260609.json
```

**Exemplo 2 — exportar para stdout e inspecionar:**
```bash
$ endo-dsl export | python3 -m json.tool | head -10
{
  "version": "1.1.0",
  "components": [
    {
      "id": 1,
      "key": "quiz.basic.recall",
      "name": "Quiz de Fixação — Nível Básico",
      ...
```

**Exemplo 3 — backup automático diário:**
```bash
$ endo-dsl export --out "backups/biblioteca_$(date +%Y%m%d).json"
✓ 14 componente(s) exportado(s) para backups/biblioteca_20260609.json
```

**Códigos de saída:** `0` sempre

---

### 6.19 `import` — importação de componentes

**Sinopse:**
```
endo-dsl [--db DB] [--quiet] [--json] import --in <arquivo.json> [--merge]
```

**Descrição.** Importa componentes de um arquivo JSON no formato produzido por `export`. Por
padrão, sobrescreve componentes com a mesma chave; com `--merge`, ignora chaves já existentes
(preservando os componentes locais).

**Flags:**

| Flag | Obrigatória | Descrição |
|------|:-----------:|-----------|
| `--in` | **sim** | Caminho do arquivo JSON de entrada |
| `--merge` | não | Ignora componentes cuja chave já existe no banco local |

**Exemplo 1 — importação completa:**
```bash
$ endo-dsl import --in biblioteca_compartilhada.json
✓ 8 componente(s) importado(s); 0 ignorado(s).
```

**Exemplo 2 — importação com merge (preserva locais):**
```bash
$ endo-dsl import --in atualizacao_biblioteca.json --merge
✓ 3 componente(s) importado(s); 5 ignorado(s).
```

**Exemplo 3 — saída JSON:**
```bash
$ endo-dsl --json import --in backup_biblioteca_20260601.json --merge
{
  "created": 2,
  "skipped": 12
}
```

**Códigos de saída:** `0` sempre

---

### 6.20 `config` — configuração persistente do usuário

**Sinopse:**
```
endo-dsl [--json] config {get|set|list|reset|path} [chave] [valor]
```

**Descrição.** Lê e grava a configuração persistente do usuário armazenada em JSON em
`~/.config/endo-dsl/config.json` (ou no caminho definido por `ENDO_DSL_CONFIG`/`XDG_CONFIG_HOME`).
Suporta chaves **pontilhadas** para acesso a subobjetos.

| Ação | Descrição |
|------|-----------|
| `get <chave>` | Imprime o valor da chave (pontilhada) |
| `set <chave> <valor>` | Define o valor e persiste no arquivo |
| `list` | Lista todas as configurações efetivas (arquivo + variáveis de ambiente) |
| `reset` | Restaura o arquivo para os valores padrão |
| `path` | Imprime o caminho do arquivo de configuração |

**Chaves disponíveis e padrões:**

| Chave | Padrão | Descrição |
|-------|--------|-----------|
| `theme` | `endo` | Tema de interface |
| `backend` | `template` | Backend LLM |
| `model` | `claude-sonnet-4-20250514` | Modelo Claude |
| `db_path` | `null` | Caminho do banco (null = padrão automático) |
| `default_domain` | `Matemática` | Domínio padrão para `new` e `generate` |
| `default_bloom` | `Analisar` | Bloom padrão para `new` |
| `editor.tab_size` | `2` | Tamanho da indentação no formatador |
| `editor.font` | `JetBrains Mono` | Fonte no editor web |
| `output_dir` | `null` | Diretório de saída de protótipos (null = cwd) |
| `locale` | `pt-BR` | Localização |

**Exemplo 1 — listar configuração completa:**
```bash
$ endo-dsl config list
  backend                = template
  db_path                = null
  default_bloom          = Analisar
  default_domain         = Matemática
  editor.font            = JetBrains Mono
  editor.tab_size        = 2
  locale                 = pt-BR
  model                  = claude-sonnet-4-20250514
  output_dir             = null
  theme                  = dark
```

**Exemplo 2 — configurar backend e tema:**
```bash
$ endo-dsl config set backend claude
✓ backend = claude

$ endo-dsl config set theme dark
✓ theme = dark
```

**Exemplo 3 — ler uma chave pontilhada:**
```bash
$ endo-dsl config get editor.tab_size
2

$ endo-dsl config path
/home/usuario/.config/endo-dsl/config.json
```

**Exemplo 4 — resetar para padrões:**
```bash
$ endo-dsl config reset
✓ configuração restaurada para os padrões em /home/usuario/.config/endo-dsl/config.json
```

**Códigos de saída:** `0` — sucesso · `2` — argumentos insuficientes

---

### 6.21 `theme` — temas de interface

**Sinopse:**
```
endo-dsl [--json] theme {list|show|set} [nome]
```

**Descrição.** Gerencia os temas visuais da interface web. O tema define variáveis CSS para
cores de fundo, texto, primária, superfície, borda e as seis cores da Taxonomia de Bloom. Os
temas disponíveis são: `endo` (padrão, índigo/slate), `light` (branco/cinza), `dark`
(escuro/azul-profundo), `solarized` (paleta Solarized) e `high-contrast` (alto contraste).

| Ação | Descrição |
|------|-----------|
| `list` | Lista os temas disponíveis, marcando o atual |
| `show <nome>` | Imprime o CSS do tema (bloco `:root` ou `[data-theme=…]`) |
| `set <nome>` | Define o tema ativo (persiste em `config.json`) |

**Exemplo 1 — listar temas:**
```bash
$ endo-dsl theme list
  endo (atual)
  light
  dark
  solarized
  high-contrast
```

**Exemplo 2 — inspecionar tema `dark`:**
```bash
$ endo-dsl theme show dark
[data-theme="dark"] {
  --bg: #1a1a2e;
  --fg: #e8eaf6;
  --primary: #a5b4fc;
  --surface: #26263f;
  --border: #3b3b5c;
  --bloom-lembrar: #93c5fd;
  --bloom-compreender: #5eead4;
  --bloom-aplicar: #86efac;
  --bloom-analisar: #fde047;
  --bloom-avaliar: #fdba74;
  --bloom-criar: #fca5a5;
}
```

**Exemplo 3 — definir tema de alto contraste para acessibilidade:**
```bash
$ endo-dsl theme set high-contrast
✓ tema definido: high-contrast
```

**Códigos de saída:** `0` — sucesso · `1` — tema desconhecido · `2` — argumentos insuficientes

---

### 6.22 `watch` — modo observador de arquivo

**Sinopse:**
```
endo-dsl [--db DB] [--quiet] watch <arquivo.endo> [--interval <segundos>]
```

**Descrição.** Observa o arquivo `.endo` especificado e o recompila automaticamente toda vez
que detecta uma modificação (via polling do `mtime`). Imprime o caminho do HTML gerado a cada
compilação bem-sucedida, ou as mensagens de erro caso a compilação falhe. Interrompe com
`Ctrl+C`.

Ideal para um fluxo de trabalho tipo "editar e ver": abra o protótipo no navegador e deixe-o
aberto; edite o `.endo` no seu editor favorito; o `watch` recompila e você recarrega o
navegador.

**Flags:**

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--interval` | `1.0` | Intervalo de polling em segundos. Mínimo: 0.2s |

**Exemplo 1 — modo observador padrão:**
```bash
$ endo-dsl watch examples/fracoes.endo
Observando examples/fracoes.endo (Ctrl+C para parar)…
✓ recompilado: /home/usuario/.endo/prototypes/proto_22/prototype.html
✓ recompilado: /home/usuario/.endo/prototypes/proto_22/prototype.html
✗ falha de compilação:
  [ERROR] mecânica 'teste' tem tipo desconhecido 'adventure' (linha 18, col 12)
✓ recompilado: /home/usuario/.endo/prototypes/proto_22/prototype.html
^C
Encerrado.
```

**Exemplo 2 — polling mais rápido para desenvolvimento ativo:**
```bash
$ endo-dsl watch meu_projeto.endo --interval 0.3
Observando meu_projeto.endo (Ctrl+C para parar)…
✓ recompilado: /home/usuario/.endo/prototypes/proto_25/prototype.html
```

**Exemplo 3 — combinado com abertura automática do navegador:**
```bash
$ endo-dsl watch meu_jogo.endo &
WATCH_PID=$!
sleep 2   # aguarda primeira compilação
xdg-open /home/usuario/.endo/prototypes/proto_$(endo-dsl --json stats | jq .prototypes)/prototype.html
wait $WATCH_PID
```

**Códigos de saída:** `0` — encerrado normalmente (Ctrl+C) · `1` — arquivo não encontrado · `130` — interrupção de sinal

---

### 6.23 `doctor` — diagnóstico do ambiente

**Sinopse:**
```
endo-dsl [--db DB] [--quiet] [--json] doctor
```

**Descrição.** Verifica e reporta o estado de saúde do ambiente de instalação da Endo-DSL.
Checa: versão do Python (≥3.11), presença e validade do arquivo de configuração, acesso ao
banco de dados SQLite, presença de componentes na biblioteca, configuração do backend LLM e
chave de API, tema configurado e permissão de escrita no diretório de saída.

Cada verificação recebe um status: `OK`, `WARN` (aviso, não bloqueia o uso) ou `FAIL`
(problema que impede o funcionamento normal).

**Exemplo 1 — diagnóstico completo:**
```bash
$ endo-dsl doctor
Diagnóstico do ambiente Endo-DSL
──────────────────────────────────────────────────
  [OK  ] Python                 3.11.9
  [OK  ] Config                 /home/usuario/.config/endo-dsl/config.json
  [OK  ] Banco de dados         /home/usuario/.endo/endo_dsl.sqlite3
  [OK  ] Componentes            14 cadastrado(s)
  [WARN] Backend LLM            claude selecionado, mas ANTHROPIC_API_KEY ausente
  [OK  ] Tema                   dark
  [OK  ] Permissão de escrita   /home/usuario/.endo
```

**Exemplo 2 — diagnóstico com problema grave:**
```bash
$ endo-dsl --db /tmp/inexistente/banco.db doctor
Diagnóstico do ambiente Endo-DSL
──────────────────────────────────────────────────
  [OK  ] Python                 3.11.9
  [WARN] Config                 /home/usuario/.config/endo-dsl/config.json (usando padrões)
  [FAIL] Banco de dados         /tmp/inexistente/banco.db — No such file or directory
  [WARN] Componentes            ? (rode seed-components)
  [OK  ] Backend LLM            template
  [OK  ] Tema                   endo
  [WARN] Permissão de escrita   /tmp/inexistente
```

**Exemplo 3 — saída JSON para monitoramento:**
```bash
$ endo-dsl --json doctor
{
  "checks": [
    {"status": "OK",   "label": "Python",              "detail": "3.11.9"},
    {"status": "OK",   "label": "Config",              "detail": "/home/usuario/…"},
    {"status": "OK",   "label": "Banco de dados",      "detail": "/home/usuario/…"},
    {"status": "OK",   "label": "Componentes",         "detail": "14 cadastrado(s)"},
    {"status": "WARN", "label": "Backend LLM",         "detail": "claude selecionado, mas ANTHROPIC_API_KEY ausente"},
    {"status": "OK",   "label": "Tema",                "detail": "dark"},
    {"status": "OK",   "label": "Permissão de escrita","detail": "/home/usuario/.endo"}
  ]
}
```

**Códigos de saída:** `0` — sem FAIL · `1` — pelo menos um FAIL

---

## 7. Compilador avulso — `endo-dslc`

O compilador pode ser invocado diretamente via Python sem a CLI principal, para integração
em pipelines programáticos:

```python
from endo_dsl.compiler.compiler import compile_source, reparametrize_content, CompileError

# Compilar uma string DSL
dsl = open("examples/fracoes.endo").read()
try:
    result = compile_source(dsl)
    print(result.html[:200])          # HTML5 gerado
    print(result.bloom_levels)        # ['Analisar', 'Lembrar']
    print(result.traceability)        # dict de rastreabilidade
    result.write("./saida/")          # grava arquivos
except CompileError as e:
    for msg in e.messages:
        print(f"[{msg['severity']}] {msg['message']}")
```

```python
# Reparametrizar um protótipo já compilado
html_original = open("prototype.html").read()
html_novo = reparametrize_content(
    html_original,
    domain="Ciências",
    topic="sistema solar"
)
open("prototype_ciencias.html", "w").write(html_novo)
```

**Uso como script (equivalente ao comando `compile`):**

```bash
python3 - <<'EOF'
from endo_dsl.compiler.compiler import compile_source
import sys
src = open(sys.argv[1]).read()
r = compile_source(src)
r.write("./build/")
print(f"Compilado: {r.bloom_levels}")
EOF examples/fracoes.endo
```

---

## 8. Cenários de uso típico

### 8.1 Professor elaborando quiz para aula de frações

**Contexto:** Professora do 5º ano quer um jogo para 15 minutos de aula. Não tem experiência
com programação mas quer entender a DSL.

```bash
# 1. Verificar que o ambiente está ok
endo-dsl doctor

# 2. Criar um scaffold inicial
endo-dsl new "Frações na Prática" --bloom Analisar --domain Matemática \
    --type comparison -o frações_aula.endo

# 3. Editar o arquivo no editor de texto favorito
# (editar frações_aula.endo, personalizar objetivo e parâmetros)

# 4. Validar durante a edição (pode rodar em loop ou via watch)
endo-dsl validate frações_aula.endo

# Ou usar o modo observador para feedback contínuo:
endo-dsl watch frações_aula.endo &

# 5. Compilar o protótipo final
endo-dsl compile frações_aula.endo --origin manual

# 6. Abrir no navegador
xdg-open ~/.endo/prototypes/proto_*/prototype.html

# 7. Avaliar o protótipo (registra nota para o relatório)
# (acessar http://localhost:8000/evaluate/<id> se o servidor estiver rodando)
```

**Saída esperada:**
```
✓ Arquivo criado: frações_aula.endo
✓ Especificação válida: 'Frações na Prática' (Bloom: Analisar)
✓ Protótipo #19 compilado: Frações na Prática
                html: /home/prof/.endo/prototypes/proto_19/prototype.html
  Abra no navegador: file:///home/prof/.endo/prototypes/proto_19/prototype.html
```

---

### 8.2 Pesquisador exportando biblioteca em lote para análise

**Contexto:** Pesquisador quer exportar todos os componentes, dados de uso e avaliações para
análise estatística em R. Trabalha com vários bancos de experimentos distintos.

```bash
# 1. Verificar estatísticas do banco de pesquisa
endo-dsl --db ~/pesquisa/exp_2026.sqlite3 stats

# 2. Exportar biblioteca completa
endo-dsl --db ~/pesquisa/exp_2026.sqlite3 export \
    --out ~/pesquisa/resultados/biblioteca_exp2026.json

# 3. Exportar avaliações em CSV para análise estatística
endo-dsl --db ~/pesquisa/exp_2026.sqlite3 report --csv \
    > ~/pesquisa/resultados/avaliacoes_exp2026.csv

# 4. Verificar as métricas gerais
endo-dsl --db ~/pesquisa/exp_2026.sqlite3 report

# 5. Combinar dados de múltiplos experimentos
for db in ~/pesquisa/exp_*.sqlite3; do
    nome=$(basename $db .sqlite3)
    endo-dsl --db $db --quiet report --csv > ~/pesquisa/resultados/${nome}.csv
done

# 6. Analisar no Python
python3 - <<'EOF'
import glob, pandas as pd
dfs = [pd.read_csv(f) for f in glob.glob('~/pesquisa/resultados/exp_*.csv')]
combined = pd.concat(dfs)
print(combined.groupby('origin')['overall_weighted'].describe())
EOF
```

**Saída esperada:**
```
Métricas da plataforma Endo-DSL
────────────────────────────────────────
  components                        14
  prototypes                        28
  evaluations                       41
...
✓ 14 componente(s) exportado(s) para biblioteca_exp2026.json
```

---

### 8.3 Curador revisando e aprovando componentes novos

**Contexto:** Curador da biblioteca recebeu notificação de novos componentes experimentais
submetidos por pesquisadores colaboradores. Quer revisar com critério e documentar as decisões.

```bash
# 1. Verificar a fila de curadoria
endo-dsl curate list

# 2. Inspecionar cada componente candidato a aprovação
endo-dsl library show classification.fractions.advanced

# 3. Verificar os metadados e a assinatura DSL no detalhe
endo-dsl --json library show classification.fractions.advanced | python3 -m json.tool

# 4. Testar a assinatura DSL: extrair e compilar
endo-dsl --json library show classification.fractions.advanced \
    | python3 -c "
import json,sys
comp = json.load(sys.stdin)
print(comp['dsl_signature'])
" > /tmp/test_comp.endo
endo-dsl validate /tmp/test_comp.endo

# 5. Aprovar componentes que passaram na revisão
endo-dsl curate approve 18 \
    --curator "ana.silva@cos.ufrj.br" \
    --note "Afinidade Bloom×mecânica correta; 6 instâncias validadas; parâmetros documentados"

endo-dsl curate approve 21 \
    --curator "ana.silva@cos.ufrj.br" \
    --note "Mecânica puzzle alinhada ao nível Criar; referência bibliográfica incluída"

# 6. Rejeitar componente com problema de alinhamento
endo-dsl curate reject 27 \
    --curator "ana.silva@cos.ufrj.br" \
    --note "Tipo 'sequencing' incompatível com bloom Criar; sugerir bloom Analisar ou Aplicar"

# 7. Verificar o resultado
endo-dsl curate list
# 1 componente(s) na fila de curadoria:
#   #23 matching.synonyms.pt  Compreender  matching  (instâncias: 2)

# 8. Exportar biblioteca atualizada para compartilhamento
endo-dsl export --out biblioteca_curada_$(date +%Y%m%d).json
```

**Saída esperada:**
```
4 componente(s) na fila de curadoria:
  #18 classification.fractions.adv   Analisar     classification  (instâncias: 6)
  #21 puzzle.build.open              Criar        puzzle          (instâncias: 4)
  #23 matching.synonyms.pt           Compreender  matching        (instâncias: 2)
  #27 sequencing.water.cycle         Aplicar      sequencing      (instâncias: 1)
✓ componente #18 promovido a canônico.
✓ componente #21 promovido a canônico.
✗ componente #27 rejeitado.
1 componente(s) na fila de curadoria:
  #23 matching.synonyms.pt           Compreender  matching        (instâncias: 2)
✓ 16 componente(s) exportado(s) para biblioteca_curada_20260609.json
```

---

*Endo-DSL · PESC/COPPE/UFRJ · contato: caiosazeredo@cos.ufrj.br*
