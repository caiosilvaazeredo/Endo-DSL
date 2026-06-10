# Variante `native` — Endo-DSL em código de máquina (desktop)

Build **AOT (ahead-of-time) em código de máquina** do compilador "compiler-only"
(`endo-dslc`), via [Nuitka](https://nuitka.net). O resultado é um **único binário
nativo** que:

- **não precisa de runtime Python instalado** (CPython vai embutido — onefile);
- compila `.endo` → HTML5 com a mesma CLI do `compiler-only`;
- é livre de banco de dados (parte de `variants/compiler-only/standalone.py`).

## Rationale

- **Código de máquina AOT**: Nuitka traduz o Python para C e compila com `gcc`,
  produzindo um ELF nativo (não bytecode interpretado).
- **Distribuição de arquivo único**: um executável autônomo para entregar a
  usuários de desktop sem pedir "instale o Python".
- **Sem dependências externas**: o protótipo HTML5 gerado também é autocontido.

## O que foi efetivamente construído (neste ambiente)

| Item | Resultado |
|---|---|
| Ferramenta | Nuitka 4.1.2 + gcc 13 + patchelf 0.17.2 |
| Comando | `nuitka --onefile --standalone --lto=no` sobre `standalone.py` |
| Saída | `variants/native/dist/endo-dslc` |
| Tipo | `ELF 64-bit LSB pie executable, x86-64, stripped` |
| Tamanho | ~15,8 MB (CPython embutido) |
| Execução | OK — compilou `examples/fracoes.endo` → HTML5 de ~19 KB |

`patchelf` e `nuitka` foram instalados via `pip`. A build onefile **sem**
`zstandard` não comprime o payload (apenas um aviso, não impede a build).

## Build

```bash
bash variants/native/build_native.sh
# -> variants/native/dist/endo-dslc
./variants/native/dist/endo-dslc examples/fracoes.endo -o jogo.html
```

O script regenera `standalone.py`, instala Nuitka e compila. Caminhos de
fallback (Cython `--embed`/`--module`, Nuitka "accelerated" não-onefile,
PyInstaller) estão documentados em comentários no próprio `build_native.sh`.

## Comparação de startup medida (Linux x86_64)

3 execuções de `endo-dslc examples/fracoes.endo` (relógio `real`):

| Build | run 1 | run 2 | run 3 |
|---|---|---|---|
| nativo (Nuitka onefile) | 0,086 s | 0,083 s | 0,091 s |
| `python standalone.py`  | 0,070 s | 0,064 s | 0,064 s |

**Observação honesta**: neste workload minúsculo o binário **onefile** não ficou
mais rápido — ele se **autoextrai** para um diretório temporário a cada execução,
o que custa ~15–25 ms que dominam a tarefa trivial. O ganho de startup AOT
aparece em duas situações:

- usar o modo **`--standalone`** (pasta, não onefile): sem reextração por
  execução, o startup cai abaixo do CPython;
- workloads maiores, onde o tempo de import/parse do CPython pesa mais que o
  overhead fixo de extração.

O valor central desta variante é a **distribuição de arquivo único sem runtime
Python**, não necessariamente latência menor em tarefas triviais.

## Alvos de plataforma

- **Linux x86_64**: produzido aqui (ELF). Para máxima portabilidade entre
  distros, compile na glibc mais antiga que pretende suportar.
- **Windows**: rode `build_native.sh` (ou os comandos Nuitka equivalentes) numa
  máquina Windows com MSVC ou MinGW; a saída é `endo-dslc.exe`. Nuitka **não**
  faz cross-compile — compile na plataforma alvo.
- **macOS**: Nuitka gera um Mach-O; assine/notarize (`codesign`/`notarytool`)
  para distribuir fora do Gatekeeper.
