# Variantes de distribuição do Endo-DSL

Builds otimizadas do compilador Endo-DSL para diferentes alvos. Todas geram o
**mesmo protótipo HTML5 jogável e autocontido** (RF19–RF23) a partir de uma
especificação `.endo`; o que muda é o **empacotamento** e o **ambiente de
execução**.

| Variante | Dependências | Banco de dados | Alvo | Tamanho | Caso de uso |
|---|---|---|---|---|---|
| **Plataforma completa** (`endo_dsl` inteiro) | stdlib + subsistemas (web, library, agents) | **SQLite** | servidor / desktop com Python | pacote completo | autoria interativa, pipeline LLM, pesquisa |
| **`compiler-only`** | só stdlib do Python ≥ 3.10 | **nenhum** | qualquer Python (CLI/CI/batch) | ~105 KB (`standalone.py`) | compilar em lote, embarcar, CI, base das outras builds |
| **`browser`** (Pyodide) | Pyodide (WASM, CDN) + payload local | **nenhum** | navegador, 100% client-side | payload ~33 KB + runtime Pyodide | demo/uso estático sem servidor (GitHub Pages) |
| **`native`** (Nuitka) | nenhuma em runtime (CPython embutido) | **nenhum** | binário desktop (Linux/Win/macOS) | ~15,8 MB (binário onefile) | entregar a usuários sem Python instalado |

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
