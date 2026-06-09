# Variante `compiler-only` — Endo-DSL sem banco de dados

Distribuição **mínima e sem dependências** que expõe **apenas** o compilador
Endo-DSL: a transformação `.endo` → protótipo **HTML5 jogável e autocontido**
(RF19–RF23). Nenhum SQLite, nenhum agente LLM, nenhuma biblioteca web ou
servidor estão presentes neste caminho.

## Como difere da plataforma completa

| Aspecto | Plataforma completa | `compiler-only` |
|---|---|---|
| Banco de dados | SQLite (biblioteca, sessões) | **nenhum** |
| Agentes LLM / pipeline | sim | **não** |
| Servidor web | sim (`endo_dsl.web`) | **não** |
| Dependências | stdlib + subsistemas | **somente stdlib do Python ≥ 3.10** |
| Superfície | DSL + biblioteca + agentes + compilador | só o compilador |
| Caso de uso | autoria interativa, pesquisa | CI, batch, embarcar, build nativa |

O caminho de compilação (`endo_dsl.compiler.compiler.compile_source`) já é
livre de banco de dados: ele faz `parse → validação semântica → render HTML`,
e retorna um `CompileResult` com HTML5 autossuficiente (CSS+JS embutidos).

## Instalar apenas o compilador

A CLI vive no pacote principal, em `endo_dsl/compiler_cli.py`, e é exposta como
o entry point `endo-dslc`. Para instalar **somente** o subconjunto do
compilador, basta o pacote `endo_dsl` (sem importar `endo_dsl.db`/`web`/
`agents`/`library`, que ficam inertes se não usados):

```bash
pip install -e .            # instala o pacote; o caminho do compilador é stdlib-only
endo-dslc examples/fracoes.endo -o jogo.html
```

> A CLI `endo-dslc` importa exclusivamente `endo_dsl.compiler.*` e
> `endo_dsl.dsl.*` — nunca toca em `endo_dsl.db`.

## Uso (CLI `endo-dslc`)

```bash
# DSL educativo padrão
endo-dslc entrada.endo                  # escreve ./entrada.html ao lado da entrada
endo-dslc entrada.endo -o jogo.html     # define o arquivo de saída
cat entrada.endo | endo-dslc -          # lê da entrada padrão (stdin)
endo-dslc entrada.endo --trace          # também grava o doc. de rastreabilidade (RF23)
endo-dslc entrada.endo --check          # apenas valida (parse + semântica), sem escrever
endo-dslc entrada.endo --no-strict      # gera mesmo com erros semânticos

# Jogos de tabuleiro — compilar DSL boardgame{}
endo-dslc jogo.endo --boardgame         # compila bloco boardgame{} -> HTML5
endo-dslc jogo.endo --boardgame --domain Ciências --topic ecossistemas

# Jogos de tabuleiro — gerar a partir de arquétipo (sem arquivo .endo)
endo-dslc --template trilha -o trilha.html
endo-dslc --template quiz_battle --domain Matemática --topic frações --players 4
endo-dslc --template memory_match --bloom Lembrar --title "Memória de Biomas"
```

Arquétipos disponíveis: `trilha`, `quiz_battle`, `memory_match`, `word_race`,
`strategy_grid`, `cooperative_quest`, `auction_economy`, `deduction_mystery`.

Códigos de saída: `0` sucesso · `1` erro de compilação · `2` erro de E/S.

## Arquivo único: `standalone.py`

Para distribuir o compilador sem instalar nada, use o bundle de arquivo único.
Ele embute a cadeia mínima de módulos (apenas `dsl` + `compiler`) e roda em
qualquer Python ≥ 3.10:

```bash
python standalone.py entrada.endo -o saida.html
python standalone.py entrada.endo --trace
cat entrada.endo | python standalone.py -
```

`standalone.py` é **gerado** a partir dos módulos reais por `bundle.py`.
Reexecute após mudar o compilador:

```bash
python variants/compiler-only/bundle.py   # regera standalone.py
```

### Verificado

`standalone.py` foi copiado para um diretório fora do repositório (`/tmp`) — sem
acesso ao pacote `endo_dsl` instalado — e compilou `examples/fracoes.endo` em um
HTML5 de ~19 KB, tanto a partir de arquivo quanto de stdin, incluindo `--trace`.
Nenhuma referência a SQLite no caminho executado.
