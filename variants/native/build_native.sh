#!/usr/bin/env bash
# Build NATIVO (código de máquina) do compilador Endo-DSL "compiler-only".
#
# Alvo principal: desktop Linux x86_64. O binário resultante é AOT (machine
# code), não precisa de runtime Python instalado e tem startup quase instantâneo.
#
# Entrada: variants/compiler-only/standalone.py (arquivo único, sem banco de
# dados). Regenere-o antes, se necessário:
#     python variants/compiler-only/bundle.py
#
# Uso:
#     bash variants/native/build_native.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENTRY="$ROOT/variants/compiler-only/standalone.py"
DIST="$ROOT/variants/native/dist"
mkdir -p "$DIST"

echo ">> Regenerando standalone.py"
python "$ROOT/variants/compiler-only/bundle.py"

echo ">> Instalando Nuitka"
pip install --quiet nuitka

# --------------------------------------------------------------------------- #
# Caminho A (preferido): binário onefile autônomo.
#   --onefile  : um único executável que se autoextrai
#   --standalone: empacota o CPython embutido
# Pode ser LENTO. Se exceder o tempo, use o Caminho B.
# --------------------------------------------------------------------------- #
echo ">> [A] Nuitka --onefile --standalone (pode demorar)"
python -m nuitka \
    --onefile --standalone \
    --output-dir="$DIST" \
    --output-filename="endo-dslc" \
    --remove-output \
    --assume-yes-for-downloads \
    --lto=no \
    "$ENTRY"

echo ">> Binário em $DIST/endo-dslc"

# --------------------------------------------------------------------------- #
# Caminho B (fallback rápido): compilação "accelerated" (não-onefile). Gera um
# binário que ainda depende do Python do sistema, mas compila em segundos.
#     python -m nuitka --output-dir="$DIST" "$ENTRY"
#
# Caminho C (Cython): transpila o core para C e compila um .so.
#     pip install cython
#     cython --embed -3 -o "$DIST/standalone.c" "$ENTRY"
#     gcc -Os "$DIST/standalone.c" -o "$DIST/endo-dslc" \
#         $(python3-config --includes) $(python3-config --ldflags) -lpython3.11
#   (ou, como módulo .so:  cythonize -i variants/compiler-only/standalone.py)
#
# Caminho D (PyInstaller): empacota, mas é bytecode (não AOT machine code).
#     pip install pyinstaller
#     pyinstaller --onefile --name endo-dslc --distpath "$DIST" "$ENTRY"
#
# Cross-build Windows/macOS: rode este script NA plataforma alvo (Nuitka não faz
# cross-compile). Em Windows use MSVC/MinGW; o binário sai .exe. Em macOS, o
# Nuitka produz um Mach-O (assine/notarize para distribuição).
# --------------------------------------------------------------------------- #
