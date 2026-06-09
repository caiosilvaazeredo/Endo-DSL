# Manual de Comandos — Endo-DSL

> Referência completa da interface de linha de comando (CLI) da plataforma
> **Endo-DSL**, desenvolvida no PESC/COPPE/UFRJ. Documenta tanto os comandos
> **implementados** quanto os comandos **planejados** (em desenvolvimento por
> outra frente de trabalho).

A CLI é o ponto de entrada `endo-dsl` (instalado via `pip install -e .`) e também
pode ser invocada como módulo: `python -m endo_dsl <comando> [opções]`.

---

## 1. Tabela de referência rápida

### 1.1 Comandos implementados

| Comando | Descrição | RF |
|---------|-----------|----|
| `endo-dsl validate <arquivo>` | Valida sintaxe e semântica de um `.endo` | RF03/RF04 |
| `endo-dsl compile <arquivo>` | Compila DSL → protótipo HTML5 | RF19–RF23 |
| `endo-dsl generate ...` | Pipeline multi-agente: gera DSL a partir do contexto | RF13–RF18 |
| `endo-dsl library <ação>` | Biblioteca de componentes (list/search/seed/show) | RF07–RF12 |
| `endo-dsl curate <ação>` | Curadoria de componentes (list/approve/reject) | RF12 |
| `endo-dsl reparametrize <id>` | Troca o domínio de um protótipo sem recompilar | RF22 |
| `endo-dsl report` | Relatório comparativo auto × manual | RF26 |
| `endo-dsl grammar` | Imprime a gramática formal (EBNF) | RF01/RF02 |
| `endo-dsl limits` | Imprime os limites da gramática | RF06 |
| `endo-dsl serve` | Inicia a interface web (jornada completa) | — |
| `endo-dsl demo` | Demonstração completa fim-a-fim | — |

### 1.2 Comandos planejados (em desenvolvimento)

| Comando | Descrição prevista |
|---------|--------------------|
| `endo-dsl init-db` | Cria/migra o banco SQLite explicitamente |
| `endo-dsl seed-components` | Atalho para `library seed` |
| `endo-dsl export` | Exporta sessões/protótipos/biblioteca para um pacote |
| `endo-dsl import` | Importa um pacote exportado |
| `endo-dsl theme` | Define o tema visual (claro/escuro/alto-contraste) |
| `endo-dsl config` | Lê/escreve configurações persistentes |
| `endo-dsl watch` | Recompila ao salvar um `.endo` (modo observador) |
| `endo-dsl new` | Scaffolding de um novo projeto/`.endo` |
| `endo-dsl lint` | Análise de estilo/boas práticas da DSL |
| `endo-dsl fmt` | Formatação automática de um `.endo` |
| `endo-dsl stats` | Estatísticas agregadas da plataforma |
| `endo-dsl doctor` | Diagnóstico do ambiente e da instalação |

### 1.3 Opções globais

| Opção | Descrição |
|-------|-----------|
| `--version` | Imprime a versão (`Endo-DSL <versão>`) e sai |
| `--db <caminho>` | Caminho do banco SQLite (padrão: `data/endo_dsl.sqlite3`) |
| `-h`, `--help` | Ajuda do comando ou subcomando |

> As opções globais vêm **antes** do subcomando: `endo-dsl --db /tmp/x.sqlite3 validate a.endo`.

---

## 2. `python -m endo_dsl` e variáveis de ambiente

### 2.1 Invocação como módulo

Quando o pacote não está instalado como script, use a forma de módulo —
funcionalmente idêntica ao executável `endo-dsl`:

```bash
python -m endo_dsl validate examples/fracoes.endo
python -m endo_dsl --db /tmp/lab.sqlite3 serve --port 9000
```

### 2.2 Variáveis de ambiente

| Variável | Efeito |
|----------|--------|
| `ENDO_DSL_DB` | Caminho-padrão do banco quando `--db` não é informado |
| `ANTHROPIC_API_KEY` | Habilita o backend LLM Claude no comando `generate` |
| `ENDO_DSL_BACKEND` | Seleciona o backend de geração (`heuristic` \| `claude`) |
| `ENDO_DSL_THEME` | Tema da interface web (`light` \| `dark` \| `contrast`) |

Exemplo:

```bash
export ENDO_DSL_DB=$HOME/.endo/endo.sqlite3
export ANTHROPIC_API_KEY=sk-ant-...
export ENDO_DSL_BACKEND=claude
endo-dsl generate --objective "comparar frações" --domain "Matemática" --bloom Analisar
```

> Sem `ANTHROPIC_API_KEY` (ou com `anthropic` não instalado) a plataforma usa o
> backend **heurístico** determinístico, que não requer rede.

---

## 3. Comandos implementados — referência detalhada

Cada entrada traz: **sinopse**, **descrição**, **flags**, **exemplos com saída
esperada** e **códigos de saída**.

> **Convenção de códigos de saída:** `0` = sucesso; `1` = falha de
> validação/compilação/dado ausente; `2` = uso incorreto (argumentos inválidos,
> tratados pelo `argparse`).

---

### 3.1 `validate` — validação sintática e semântica (RF03/RF04)

**Sinopse**
```
endo-dsl [--db DB] validate <arquivo.endo>
```

**Descrição.** Faz o *parse* do arquivo e executa a validação semântica
(coerência cognitiva de Bloom, referências de objetivos, mecânicas etc.). Não
gera artefatos. Erros vão para `stderr`; avisos (warnings) não impedem o sucesso.

**Flags.** Nenhuma além das globais. Argumento posicional obrigatório: o caminho
do arquivo `.endo`.

**Exemplo 1 — especificação válida**
```bash
$ endo-dsl validate examples/fracoes.endo
✓ Especificação válida: 'Comparando Frações' (Bloom: Analisar, Lembrar)
  1 aviso(s):
  [WARNING] mecânica 'revisao' (Lembrar) abaixo do nível-alvo (Analisar)
         → considere uma mecânica afim a Analisar (classification, comparison)
```

**Exemplo 2 — especificação inválida**
```bash
$ endo-dsl validate quebrado.endo
✗ Especificação inválida:
  [ERROR] mecânica 'mistério' tem tipo desconhecido 'mistério' (linha 12, col 11)
         → tipos disponíveis: classification, comparison, matching, puzzle, quiz, ...
```

**Códigos de saída.** `0` válido · `1` inválido.

---

### 3.2 `compile` — compilação DSL → HTML5 (RF19–RF23)

**Sinopse**
```
endo-dsl [--db DB] compile <arquivo.endo> [--origin {manual,auto,hybrid}]
```

**Descrição.** Compila a especificação em um protótipo HTML5 autocontido (sem
dependências externas em runtime), persiste a especificação e o protótipo no
banco e escreve os artefatos em `<workspace>/proto_<id>/`:

- `prototype.html` — o jogo jogável;
- `prototype.traceability.html` / `.json` — rastreabilidade pedagógica (RF23);
- `prototype.content.json` — *content pack* (permite reparametrização, RF22).

**Flags.**

| Flag | Padrão | Descrição |
|------|--------|-----------|
| `--origin` | `manual` | Origem registrada do protótipo (`manual`, `auto`, `hybrid`) — usada na comparação auto × manual (RF26) |

**Exemplo 1 — compilação bem-sucedida**
```bash
$ endo-dsl compile examples/fracoes.endo
✓ Protótipo #17 compilado: Comparando Frações
                html: /…/prototypes/proto_17/prototype.html
   traceability_html: /…/prototypes/proto_17/prototype.traceability.html
   traceability_json: /…/prototypes/proto_17/prototype.traceability.json
        content_pack: /…/prototypes/proto_17/prototype.content.json

  Abra no navegador: file:///…/prototypes/proto_17/prototype.html
```

**Exemplo 2 — falha de compilação com sugestão de biblioteca (RF20)**
```bash
$ endo-dsl compile examples/sem_tipo.endo
✗ Falha de compilação:
  [ERROR] mecânica 'm1' não declara 'type'
         → a biblioteca oferece a mecânica 'quiz' (Quiz); considere usá-la.
```

**Códigos de saída.** `0` compilado · `1` erro de compilação.

---

### 3.3 `generate` — pipeline multi-agente (RF13–RF18)

**Sinopse**
```
endo-dsl [--db DB] generate --objective TXT --domain TXT --bloom NIVEL
    [--topic T] [--age FAIXA] [--level ESCOL] [--duration MIN]
    [--name NOME] [--components K1,K2] [--from-scratch] [--compile] [--out ARQ]
```

**Descrição.** Cria uma sessão de design (Fase 1), recupera componentes da
biblioteca (Fase 2, salvo `--from-scratch`), gera a DSL com refinamento iterativo
e a valida (Fases 3–4). Imprime a DSL gerada e as métricas de geração.

**Flags.**

| Flag | Obrigatória | Descrição |
|------|:-----------:|-----------|
| `--objective` | sim | Objetivo de aprendizagem |
| `--domain` | sim | Área de conhecimento |
| `--bloom` | sim | Nível de Bloom alvo (`Lembrar`…`Criar`) |
| `--topic` | não | Tópico específico (padrão: igual ao domínio) |
| `--age` | não | Faixa etária (ex.: `10-11`) |
| `--level` | não | Nível de escolaridade (ex.: `5º ano`) |
| `--duration` | não | Duração em minutos (inteiro) |
| `--name` | não | Nome da sessão |
| `--components` | não | Chaves de componentes, separadas por vírgula |
| `--from-scratch` | não | Gera sem recuperar componentes |
| `--compile` | não | Compila o resultado, se válido |
| `--out` | não | Salva a DSL gerada em arquivo |

**Exemplo 1 — geração com biblioteca + compilação**
```bash
$ endo-dsl generate --objective "comparar frações" --domain "Matemática" \
      --bloom Analisar --age 10-11 --duration 15 --compile --out fracoes.endo
Sessão #4 criada. Backend LLM: heuristic
Geração ✓ válida em 1 tentativa(s) — 2 mecânicas, 1 loop, 0 erros
Componentes usados: classification.fractions, quiz.basic.recall

--- Especificação DSL gerada ---
game "Comparando Frações" { … }

Salvo em fracoes.endo

✓ Compilado: /…/prototypes/proto_5/prototype.html

Métricas de geração: {"attempts": 1, "valid": true, "components": 2}
```

**Exemplo 2 — geração do zero (sem rede, backend heurístico)**
```bash
$ endo-dsl generate --objective "identificar figuras" --domain "Geometria" \
      --bloom Lembrar --from-scratch
Sessão #6 criada. Backend LLM: heuristic
Geração ✓ válida em 1 tentativa(s) — 1 mecânicas, 0 loop, 0 erros

--- Especificação DSL gerada ---
game "Identificando Figuras" { … }

Métricas de geração: {"attempts": 1, "valid": true, "components": 0}
```

**Códigos de saída.** `0` geração válida · `1` geração inválida após as tentativas.

---

### 3.4 `library` — biblioteca de componentes (RF07–RF12)

**Sinopse**
```
endo-dsl [--db DB] library {list|search|seed|show} [chave]
    [--text T] [--bloom B] [--type TIPO] [--domain D]
    [--status {canonical,experimental}] [--force]
```

**Descrição.** Gerencia o catálogo de componentes pedagógicos reutilizáveis.

| Ação | Efeito |
|------|--------|
| `list` / `search` | Lista componentes, aplicando os filtros informados |
| `seed` | Cadastra os componentes canônicos de referência |
| `show <chave>` | Imprime o componente em JSON |

**Flags de filtro** (`list`/`search`): `--text`, `--bloom`, `--type`,
`--domain`, `--status`. Flag `--force` (em `seed`) recria os canônicos.

**Exemplo 1 — popular e listar por nível de Bloom**
```bash
$ endo-dsl library seed
12 componente(s) canônico(s) cadastrado(s).

$ endo-dsl library list --bloom Analisar
2 componente(s):
  ★ classification.fractions          Analisar     classification ⟨4.2⟩
  ○ comparison.pairs                  Analisar     comparison

  ★ canônico · ○ experimental
```

**Exemplo 2 — detalhar um componente**
```bash
$ endo-dsl library show quiz.basic.recall
{
  "key": "quiz.basic.recall",
  "name": "Quiz de fixação",
  "bloom_level": "Lembrar",
  "mechanic_type": "quiz",
  "status": "canonical",
  ...
}
```

**Códigos de saída.** `0` sucesso · `1` componente não encontrado (`show`).

---

### 3.5 `curate` — curadoria de componentes (RF12)

**Sinopse**
```
endo-dsl [--db DB] curate {list|approve|reject} [id]
    [--curator NOME] [--note JUSTIFICATIVA]
```

**Descrição.** Materializa a jornada do **curador**: revisa componentes
experimentais e os promove a canônicos ou os rejeita, registrando autor e
justificativa (trilha auditável).

| Ação | Efeito |
|------|--------|
| `list` | Lista a fila de componentes experimentais |
| `approve <id>` | Promove o componente a canônico |
| `reject <id>` | Rejeita o componente |

**Exemplo 1 — listar a fila**
```bash
$ endo-dsl curate list
3 componente(s) na fila de curadoria:
  #18 classification.fractions      Analisar     classification (instâncias: 6)
  #21 puzzle.build.open             Criar        puzzle         (instâncias: 4)
  #23 matching.synonyms             Compreender  matching       (instâncias: 2)
```

**Exemplo 2 — aprovar com justificativa**
```bash
$ endo-dsl curate approve 18 --curator ana@cos.ufrj.br \
      --note "alinhamento Bloom verificado em 6 instâncias"
✓ componente #18 promovido a canônico.
```

**Códigos de saída.** `0` sucesso · `2` ação não reconhecida.

---

### 3.6 `reparametrize` — troca de domínio sem recompilar (RF22)

**Sinopse**
```
endo-dsl [--db DB] reparametrize <prototype_id> --domain DOMINIO [--topic T]
```

**Descrição.** Substitui o conteúdo embutido de um protótipo já compilado,
**preservando a estrutura** (mecânicas, interações, níveis de Bloom). Gera
`prototype.reparam.html` ao lado do original.

**Exemplo**
```bash
$ endo-dsl reparametrize 17 --domain "Ciências" --topic "células"
✓ Protótipo #17 reparametrizado para 'Ciências'.
  /…/prototypes/proto_17/prototype.reparam.html
```

**Códigos de saída.** `0` sucesso · `1` protótipo não encontrado.

---

### 3.7 `report` — relatório comparativo (RF24–RF26)

**Sinopse**
```
endo-dsl [--db DB] report [--csv]
```

**Descrição.** Imprime o relatório comparativo entre protótipos automáticos e
manuais. Com `--csv`, exporta as avaliações brutas (RF25).

**Exemplo 1 — relatório textual**
```bash
$ endo-dsl report
RELATÓRIO COMPARATIVO  (auto n=12 · manual n=9)
Média geral:  auto 3.86  ·  manual 4.12  ·  Δ -0.26
Por dimensão:
  Alinhamento pedagógico      auto 3.90  manual 4.20  Δ -0.30
  Coerência cognitiva (Bloom) auto 4.30  manual 4.10  Δ +0.20
  ...
```

**Exemplo 2 — exportação CSV**
```bash
$ endo-dsl report --csv > avaliacoes.csv
$ head -1 avaliacoes.csv
prototype_id,origin,evaluator,bloom_level,domain,pedagogical_alignment,...
```

**Códigos de saída.** `0`.

---

### 3.8 `grammar` — gramática formal (RF01/RF02)

**Sinopse**
```
endo-dsl grammar
```

**Descrição.** Imprime a gramática EBNF completa da DSL em `stdout`.

```bash
$ endo-dsl grammar | head -3
(* Gramática formal da Endo-DSL — RF01, RF02 *)
spec = game_decl ;
game_decl = "game" , string , "{" , { game_member } , "}" ;
```

**Códigos de saída.** `0`.

---

### 3.9 `limits` — limites da formalização (RF06)

**Sinopse**
```
endo-dsl limits
```

**Descrição.** Imprime, em Markdown, quais construtos são formalizados,
parcialmente formalizados ou deixados ao controle humano deliberado.

```bash
$ endo-dsl limits | head -4
# Limites Formais da Gramática Endo-DSL (RF06)
...
## Formalizados (verificáveis pela gramática)
- Mecânicas de jogo (tipo) — ...
```

**Códigos de saída.** `0`.

---

### 3.10 `serve` — interface web

**Sinopse**
```
endo-dsl [--db DB] serve [--host HOST] [--port PORT]
```

**Descrição.** Sobe o servidor HTTP embutido (stdlib) com a jornada completa
(`/`, `/studio`, `/library`, `/curator`, `/report`, `/docs`).

**Flags.** `--host` (padrão `127.0.0.1`) · `--port` (padrão `8000`).

```bash
$ endo-dsl serve --host 0.0.0.0 --port 8000
Endo-DSL servindo em http://0.0.0.0:8000  (Ctrl+C para parar)
```

**Códigos de saída.** `0` ao encerrar (Ctrl+C).

---

### 3.11 `demo` — demonstração fim-a-fim

**Sinopse**
```
endo-dsl [--db DB] demo
```

**Descrição.** Executa uma demonstração completa: cria sessão, recupera,
gera, compila e avalia, imprimindo cada etapa.

```bash
$ endo-dsl demo
[1/6] Contexto … [2/6] Recuperação … [3/6] Geração … [4/6] Validação ✓
[5/6] Compilação → proto_1/prototype.html  [6/6] Avaliação registrada.
```

**Códigos de saída.** `0`.

---

## 4. Comandos planejados — especificação prevista

Estes comandos serão implementados por outra frente. As assinaturas abaixo são a
**especificação de contrato** acordada, para que documentação e implementação
permaneçam alinhadas.

### 4.1 `init-db`
```
endo-dsl [--db DB] init-db [--force]
```
Cria/migra o schema SQLite explicitamente (hoje feito sob demanda). `--force`
recria as tabelas. Saída esperada: `✓ banco inicializado em <caminho>`.

### 4.2 `seed-components`
```
endo-dsl [--db DB] seed-components [--force]
```
Atalho ergonômico para `library seed`. Saída: `N componente(s) canônico(s) cadastrado(s).`

### 4.3 `export`
```
endo-dsl [--db DB] export --out PACOTE.zip [--include sessions,prototypes,library]
```
Empacota sessões, protótipos e/ou a biblioteca para portabilidade/backup.

### 4.4 `import`
```
endo-dsl [--db DB] import PACOTE.zip [--merge|--replace]
```
Restaura um pacote exportado, com estratégia de fusão ou substituição.

### 4.5 `theme`
```
endo-dsl theme {light|dark|contrast|show}
```
Define/exibe o tema visual da interface web (persistido; ver `ENDO_DSL_THEME`).

### 4.6 `config`
```
endo-dsl config {get|set|list} [chave] [valor]
```
Lê/escreve configurações persistentes (ex.: `backend`, `db`, `theme`).

### 4.7 `watch`
```
endo-dsl [--db DB] watch <arquivo.endo> [--out DIR]
```
Recompila automaticamente ao salvar o arquivo (loop validar→compilar), ideal
para o fluxo tipo-Overleaf com pré-visualização ao vivo.

### 4.8 `new`
```
endo-dsl new <nome> [--bloom NIVEL] [--mechanic TIPO]
```
Scaffolding: cria um `.endo` inicial preenchido com metadados e um esqueleto de
mecânica/objetivo coerentes com o nível de Bloom.

### 4.9 `lint`
```
endo-dsl lint <arquivo.endo>
```
Análise de estilo/boas práticas (avisos não bloqueantes): objetivos órfãos,
mecânicas sem `addresses`, loops sem fechamento, etc.

### 4.10 `fmt`
```
endo-dsl fmt <arquivo.endo> [--check]
```
Formatação canônica (indentação, ordem de campos). `--check` apenas verifica.

### 4.11 `stats`
```
endo-dsl [--db DB] stats
```
Estatísticas agregadas: nº de sessões, protótipos, componentes, distribuição por
nível de Bloom e por domínio.

### 4.12 `doctor`
```
endo-dsl doctor
```
Diagnóstico do ambiente: versão de Python, presença de `anthropic`, gravabilidade
do banco/workspace, integridade do schema. Saída tipo *checklist* (`✓`/`✗`).

---

## 5. Receitas comuns

```bash
# Validar antes de compilar
endo-dsl validate examples/fracoes.endo && endo-dsl compile examples/fracoes.endo

# Gerar, salvar e compilar num só passo
endo-dsl generate --objective "comparar frações" --domain Matemática \
    --bloom Analisar --compile --out out/fracoes.endo

# Subir a interface web com um banco isolado para experimentos
endo-dsl --db /tmp/experimento.sqlite3 serve --port 9000

# Curadoria em lote
endo-dsl curate list
endo-dsl curate approve 18 --curator eu@ufrj.br --note "ok"

# Exportar avaliações para análise estatística
endo-dsl report --csv > dados/avaliacoes.csv
```

---

*Endo-DSL · PESC/COPPE/UFRJ · contato: caiosazeredo@cos.ufrj.br*
