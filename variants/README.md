# Variantes de distribuição do Endo-DSL

Builds otimizadas do compilador Endo-DSL para diferentes alvos. Todas geram o
**mesmo protótipo HTML5 jogável e autocontido** (RF19–RF23) a partir de uma
especificação `.endo`; o que muda é o **empacotamento** e o **ambiente de
execução**.

| Variante | Dependências | Banco de dados | Alvo | Tamanho | Caso de uso |
|---|---|---|---|---|---|
| **Plataforma completa** (`endo_dsl` inteiro) | stdlib + subsistemas (web, library, agents, boardgame) | **SQLite** | servidor / desktop com Python | pacote completo | autoria interativa, pipeline LLM, canvas ENDO-GDC, jogos de tabuleiro, pesquisa |
| **`compiler-only`** | só stdlib do Python ≥ 3.10 | **nenhum** | qualquer Python (CLI/CI/batch) | ~105 KB (`standalone.py`) | compilar em lote, embarcar, CI, base das outras builds |
| **`browser`** (Pyodide) | Pyodide (WASM, CDN) + payload local | **nenhum** | navegador, 100% client-side | payload ~33 KB + runtime Pyodide | demo/uso estático sem servidor (GitHub Pages) |
| **`native`** (Nuitka) | nenhuma em runtime (CPython embutido) | **nenhum** | binário desktop (Linux/Win/macOS) | ~15,8 MB (binário onefile) | entregar a usuários sem Python instalado |

## Recursos de jogos de tabuleiro (boardgame)

A plataforma completa inclui o módulo `endo_dsl.boardgame` com:

- Canvas **ENDO-GDC** interativo (`/gdc`) — 8 seções pedagógicas coloridas
- **25 mecânicas** catalogadas de jogos reais (Catan, Cluedo, Dominion, Risk, Pandemic…)
- **8 arquétipos** de jogo: `trilha`, `quiz_battle`, `memory_match`, `word_race`, `strategy_grid`, `cooperative_quest`, `auction_economy`, `deduction_mystery`
- Pipeline Canvas → DSL `boardgame{}` → HTML5 jogável auto-contido
- CLI com suporte a `--boardgame` e `--template <arquétipo>` (ver `endo-dslc --help`)

## Resumo

- **`compiler-only/`** — distribuição mínima e sem banco de dados. CLI
  `endo-dslc` (em `endo_dsl/compiler_cli.py`) e um bundle de arquivo único
  `standalone.py` (gerado por `bundle.py`).
- **`browser/`** — o compilador roda no navegador via Pyodide; editor dividido
  com pré-visualização ao vivo. `build.py` gera o payload `.zip`.
- **`native/`** — binário AOT em código de máquina via Nuitka;
  `build_native.sh` compila a partir do `standalone.py`.

Cada subpasta tem seu próprio `README.md` com instruções e rationale.

## Restrições de design respeitadas

Estas variantes adicionam apenas arquivos sob `variants/` e o módulo fino
`endo_dsl/compiler_cli.py`. O caminho de compilação (`compile_source`) já era
livre de banco de dados; nenhuma variante importa `endo_dsl.db`, `web` ou
`agents`.
