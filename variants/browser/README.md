# Variante `browser` — Endo-DSL no navegador (Pyodide)

Build **100% client-side**: o compilador Endo-DSL roda **inteiramente no
navegador** via [Pyodide](https://pyodide.org) (CPython compilado para
WebAssembly). O usuário escreve a DSL, clica em **Compilar**, e o protótipo
HTML5 jogável aparece em uma pré-visualização — **sem backend, sem servidor,
sem banco de dados**.

## Arquivos

- `index.html` — editor dividido (DSL à esquerda, `iframe` de pré-visualização
  à direita), botão **Compilar**, exemplos prontos e download do HTML gerado.
  Paleta indigo/slate.
- `build.py` — empacota o subconjunto mínimo do compilador em
  `endo_compiler_payload.zip` (somente `endo_dsl.dsl` + `endo_dsl.compiler`,
  preservando a árvore de pacotes) e copia o exemplo. **Nenhum** módulo de
  banco de dados/web/agentes entra no zip.
- `endo_compiler_payload.zip` — gerado por `build.py` (14 módulos, ~33 KB).

## Como abrir

O `fetch` do payload exige HTTP (não funciona via `file://`). Sirva a pasta:

```bash
python variants/browser/build.py          # (re)gera o payload
python -m http.server -d variants/browser 8000
# abra http://localhost:8000/
```

No carregamento, a página:
1. baixa o Pyodide do CDN jsDelivr;
2. faz `fetch` de `endo_compiler_payload.zip` e o monta no FS virtual com
   `pyodide.unpackArchive`;
3. confirma `from endo_dsl.compiler.compiler import compile_source`;
4. habilita o botão **Compilar**, que executa o compilador Python no navegador
   e injeta o HTML resultante no `iframe` via `srcdoc`.

### Rede / self-host do Pyodide

A página usa o Pyodide do **CDN**, então precisa de rede na primeira carga
(depois fica em cache). Para uso **totalmente offline / self-host**, baixe o
runtime e troque a tag `<script>`:

```html
<!-- de: -->
<script src="https://cdn.jsdelivr.net/pyodide/v0.26.2/full/pyodide.js"></script>
<!-- para um caminho local: -->
<script src="./pyodide/pyodide.js"></script>
```

e copie `pyodide.js`, `pyodide.asm.*`, `python_stdlib.zip` etc. para
`variants/browser/pyodide/`. O **payload do Endo-DSL** já é local (não vem do
CDN), pois é puro Python (stdlib).

## Rationale de otimização

- **Sem backend**: nenhuma rota, nenhuma sessão, nenhum SQLite. Toda a
  compilação acontece no cliente.
- **Totalmente estático**: pode ser hospedado em **GitHub Pages**, Netlify, S3
  ou qualquer CDN — não há servidor para manter ou escalar.
- **Payload enxuto**: só `dsl` + `compiler` (o caminho livre de banco de dados),
  ~33 KB comprimidos — em vez do pacote inteiro.
- **Privacidade**: a especificação nunca sai do navegador do usuário.
- **Zero instalação** para o usuário final: basta a URL.

## Validação

Sem Chromium neste ambiente, a UI não foi executada de fato. Porém, o **payload
Python** foi validado estaticamente contra os módulos reais: o zip foi extraído
em um diretório isolado, importado sozinho (sem o pacote instalado), e
`compile_source(examples/fracoes.endo)` produziu ~19 KB de HTML. O JavaScript da
página é autoconsistente com essa API (`compile_source` / `CompileError.messages`).
