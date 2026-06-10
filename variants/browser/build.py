"""Build do payload do compilador Endo-DSL para o navegador (Pyodide).

Produz ``variants/browser/endo_compiler_payload.zip`` contendo APENAS o
subconjunto mínimo de módulos do compilador (pacotes ``endo_dsl.dsl`` e
``endo_dsl.compiler`` + ``compiler_cli``), preservando a estrutura de pacote
para que o Pyodide os monte com ``pyodide.unpackArchive`` (ou via FS) e os
``import endo_dsl...`` resolvam normalmente.

Também copia o exemplo ``examples/fracoes.endo`` para a pasta da variante.

NENHUM módulo de banco de dados/web/agentes entra no zip.

Uso::

    python variants/browser/build.py
"""

from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "endo_dsl"
HERE = Path(__file__).resolve().parent

# Arquivos a empacotar, com o caminho relativo (dentro do zip) que reproduz a
# árvore de pacotes esperada pelo Python. Apenas o caminho do compilador.
FILES = [
    "endo_dsl/__init__.py",
    "endo_dsl/compiler_cli.py",
    "endo_dsl/dsl/__init__.py",
    "endo_dsl/dsl/bloom.py",
    "endo_dsl/dsl/limits.py",
    "endo_dsl/dsl/ast.py",
    "endo_dsl/dsl/tokenizer.py",
    "endo_dsl/dsl/semantic.py",
    "endo_dsl/dsl/parser.py",
    "endo_dsl/compiler/__init__.py",
    "endo_dsl/compiler/traceability.py",
    "endo_dsl/compiler/engine.py",
    "endo_dsl/compiler/content.py",
    "endo_dsl/compiler/compiler.py",
]

# Módulos que NÃO devem entrar (sanidade): tudo com banco de dados/web/agentes.
FORBIDDEN_PREFIXES = ("endo_dsl/db", "endo_dsl/web", "endo_dsl/agents",
                      "endo_dsl/library", "endo_dsl/platform", "endo_dsl/evaluation")


def main() -> int:
    for f in FILES:
        if f.startswith(FORBIDDEN_PREFIXES):
            raise SystemExit(f"módulo proibido na lista do payload: {f}")

    out_zip = HERE / "endo_compiler_payload.zip"
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in FILES:
            src = ROOT / rel
            if not src.exists():
                raise SystemExit(f"arquivo ausente: {src}")
            zf.write(src, rel)

    # Copia o exemplo para a variante (servido junto da página estática).
    example_src = ROOT / "examples" / "fracoes.endo"
    if example_src.exists():
        (HERE / "fracoes.endo").write_text(
            example_src.read_text(encoding="utf-8"), encoding="utf-8")

    size = out_zip.stat().st_size
    print(f"payload gerado: {out_zip} ({size} bytes, {len(FILES)} módulos)")
    print(f"exemplo copiado: {HERE / 'fracoes.endo'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
