"""Registro de temas de interface (paleta reutilizável).

Cada tema mapeia variáveis CSS (``--bg``, ``--fg``, ``--primary``, ``--surface``,
``--border``) e as seis cores da Taxonomia de Bloom. A interface web pode
consumir :func:`as_css` para emitir um bloco ``:root`` / ``[data-theme=...]``.

As cores de Bloom reutilizam a paleta de ``web/static/app.css`` (badges).
"""

from __future__ import annotations

from typing import Dict, List

# Ordem canônica dos seis níveis (chaves estáveis em minúsculas, ASCII).
BLOOM_KEYS: List[str] = [
    "lembrar", "compreender", "aplicar", "analisar", "avaliar", "criar",
]

# Paleta de Bloom reaproveitada dos badges (claro).
_BLOOM_LIGHT = {
    "lembrar": "#1e40af",
    "compreender": "#0d9488",
    "aplicar": "#16a34a",
    "analisar": "#ca8a04",
    "avaliar": "#ea580c",
    "criar": "#dc2626",
}
_BLOOM_DARK = {
    "lembrar": "#93c5fd",
    "compreender": "#5eead4",
    "aplicar": "#86efac",
    "analisar": "#fde047",
    "avaliar": "#fdba74",
    "criar": "#fca5a5",
}


def _theme(bg, fg, primary, surface, border, bloom) -> Dict[str, str]:
    base = {
        "--bg": bg,
        "--fg": fg,
        "--primary": primary,
        "--surface": surface,
        "--border": border,
    }
    for key in BLOOM_KEYS:
        base[f"--bloom-{key}"] = bloom[key]
    return base


_THEMES: Dict[str, Dict[str, str]] = {
    # Tema padrão (indigo/slate).
    "endo": _theme("#f4f6f9", "#1a1a2e", "#4f46e5", "#ffffff", "#e2e8f0", _BLOOM_LIGHT),
    "light": _theme("#ffffff", "#111827", "#2563eb", "#f8fafc", "#e5e7eb", _BLOOM_LIGHT),
    "dark": _theme("#1a1a2e", "#e8eaf6", "#a5b4fc", "#26263f", "#3b3b5c", _BLOOM_DARK),
    "solarized": _theme("#fdf6e3", "#073642", "#268bd2", "#eee8d5", "#93a1a1", {
        "lembrar": "#268bd2",
        "compreender": "#2aa198",
        "aplicar": "#859900",
        "analisar": "#b58900",
        "avaliar": "#cb4b16",
        "criar": "#dc322f",
    }),
    "high-contrast": _theme("#000000", "#ffffff", "#ffff00", "#0a0a0a", "#ffffff", {
        "lembrar": "#00b7ff",
        "compreender": "#00ffd0",
        "aplicar": "#00ff66",
        "analisar": "#ffff00",
        "avaliar": "#ff9d00",
        "criar": "#ff4d4d",
    }),
}

DEFAULT_THEME = "endo"


def list_themes() -> List[str]:
    """Nomes de temas disponíveis."""
    return list(_THEMES.keys())


def get_theme(name: str) -> Dict[str, str]:
    """Retorna o dicionário de variáveis CSS de um tema (padrão se desconhecido)."""
    return dict(_THEMES.get(name, _THEMES[DEFAULT_THEME]))


def as_css(name: str) -> str:
    """Emite um bloco CSS para o tema.

    Para ``light``/``endo`` usa ``:root``; demais usam ``[data-theme="<nome>"]``
    para permitir alternância via atributo no ``<html>``.
    """
    vars_ = get_theme(name)
    selector = ":root" if name in ("endo", "light") else f'[data-theme="{name}"]'
    lines = [f"{selector} {{"]
    for k, v in vars_.items():
        lines.append(f"  {k}: {v};")
    lines.append("}")
    return "\n".join(lines)
