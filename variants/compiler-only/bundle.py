"""Gerador do ``standalone.py`` — empacota a cadeia mínima do compilador.

Lê os módulos reais do pacote ``endo_dsl`` (apenas os do caminho de compilação,
livre de banco de dados) e emite um único arquivo Python autocontido capaz de
compilar um ``.endo`` em ``.html`` sem instalar o pacote.

Reexecute este script sempre que os módulos do compilador mudarem::

    python variants/compiler-only/bundle.py
"""

from __future__ import annotations

from pathlib import Path

# Raiz do repositório (este arquivo está em variants/compiler-only/).
ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "endo_dsl"

# Pacotes (têm __init__) — criados como shells PRIMEIRO, depois seus __init__
# são executados por último (pois importam submódulos que precisam já existir).
PACKAGES = [
    ("endo_dsl", PKG / "__init__.py"),
    ("endo_dsl.dsl", PKG / "dsl" / "__init__.py"),
    ("endo_dsl.compiler", PKG / "compiler" / "__init__.py"),
]

# Submódulos folha, em ordem de dependência. Apenas o subconjunto do compilador
# — NENHUM módulo de banco de dados/web/agentes.
LEAVES = [
    ("endo_dsl.dsl.bloom", PKG / "dsl" / "bloom.py"),
    ("endo_dsl.dsl.limits", PKG / "dsl" / "limits.py"),
    ("endo_dsl.dsl.ast", PKG / "dsl" / "ast.py"),
    ("endo_dsl.dsl.tokenizer", PKG / "dsl" / "tokenizer.py"),
    ("endo_dsl.dsl.semantic", PKG / "dsl" / "semantic.py"),
    ("endo_dsl.dsl.parser", PKG / "dsl" / "parser.py"),
    ("endo_dsl.compiler.traceability", PKG / "compiler" / "traceability.py"),
    ("endo_dsl.compiler.engine", PKG / "compiler" / "engine.py"),
    ("endo_dsl.compiler.content", PKG / "compiler" / "content.py"),
    ("endo_dsl.compiler.compiler", PKG / "compiler" / "compiler.py"),
    ("endo_dsl.compiler_cli", PKG / "compiler_cli.py"),
]

HEADER = '''#!/usr/bin/env python3
"""Endo-DSL compiler — distribuição STANDALONE (arquivo único, sem banco de dados).

GERADO AUTOMATICAMENTE por variants/compiler-only/bundle.py — NÃO edite à mão.

Compila uma especificação .endo em um protótipo HTML5 jogável e autocontido,
usando apenas a biblioteca padrão do Python (>=3.10). Sem SQLite, sem servidor,
sem dependências externas.

Uso:
    python standalone.py entrada.endo -o saida.html
    python standalone.py entrada.endo --trace
    cat entrada.endo | python standalone.py -
"""

from __future__ import annotations

import sys
import types

# --------------------------------------------------------------------------- #
# Registra os módulos do compilador embutidos em sys.modules, na ordem de
# dependência, para que os ``import endo_dsl...`` internos resolvam sem o pacote
# instalado. Cada bloco abaixo é o código-fonte literal de um módulo real.
# --------------------------------------------------------------------------- #
def _shell(name: str) -> None:
    """Cria um objeto-pacote vazio (com __path__) registrado em sys.modules."""
    mod = types.ModuleType(name)
    mod.__file__ = "<bundled:%s>" % name
    mod.__path__ = []  # marca como pacote
    sys.modules[name] = mod
    if "." in name:
        parent, _, child = name.rpartition(".")
        setattr(sys.modules[parent], child, mod)


def _run(name: str, source: str) -> None:
    """Executa o código-fonte de um módulo dentro do seu namespace.

    Para pacotes, o shell já existe em sys.modules; para folhas, cria o módulo.
    """
    mod = sys.modules.get(name)
    if mod is None:
        mod = types.ModuleType(name)
        mod.__file__ = "<bundled:%s>" % name
        sys.modules[name] = mod
        if "." in name:
            parent, _, child = name.rpartition(".")
            setattr(sys.modules[parent], child, mod)
    exec(compile(source, mod.__file__, "exec"), mod.__dict__)


'''

FOOTER = '''
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    from endo_dsl.compiler_cli import main  # type: ignore  # noqa: E402
    raise SystemExit(main())
'''


def main() -> int:
    parts = [HEADER]

    pkg_by_name = dict(PACKAGES)

    # 1) Cria os shells de pacote (na ordem pai -> filho).
    parts.append("# --- shells de pacote (criados antes da execução dos __init__) ---\n")
    for name, _ in PACKAGES:
        parts.append(f"_shell({name!r})\n")
    parts.append("\n")

    # 2) Executa o __init__ raiz primeiro: define endo_dsl.__version__, que os
    #    submódulos folha importam em tempo de import. Não importa submódulos.
    parts.append("# === __init__: endo_dsl (raiz: __version__) ===\n")
    parts.append(f"_run('endo_dsl', r'''{_escape(pkg_by_name['endo_dsl'].read_text(encoding='utf-8'))}''')\n\n")

    # 3) Executa os submódulos folha, em ordem de dependência.
    for name, path in LEAVES:
        src = path.read_text(encoding="utf-8")
        parts.append(f"# === módulo: {name} ===\n")
        parts.append(f"_run({name!r}, r'''{_escape(src)}''')\n\n")

    # 4) Executa os __init__ dos sub-pacotes por último (importam as folhas já
    #    registradas).
    for name, path in PACKAGES:
        if name == "endo_dsl":
            continue
        src = path.read_text(encoding="utf-8")
        parts.append(f"# === __init__: {name} ===\n")
        parts.append(f"_run({name!r}, r'''{_escape(src)}''')\n\n")

    parts.append(FOOTER)

    out = Path(__file__).resolve().parent / "standalone.py"
    out.write_text("".join(parts), encoding="utf-8")
    print(f"standalone.py gerado: {out} ({out.stat().st_size} bytes)")
    return 0


def _escape(src: str) -> str:
    # Os módulos não contêm a sequência de três aspas simples; ainda assim,
    # protegemos contra ela e contra barras invertidas finais.
    if "'''" in src:
        raise ValueError("módulo contém ''' — empacotamento de raw-string inviável")
    return src


if __name__ == "__main__":
    raise SystemExit(main())
