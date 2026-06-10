"""Sistema de configuração/personalização da plataforma Endo-DSL.

Configuração do usuário persistida em JSON (apenas stdlib). Localização:

* ``ENDO_DSL_CONFIG`` (se definido) — caminho explícito do arquivo;
* caso contrário ``$XDG_CONFIG_HOME/endo-dsl/config.json``;
* caso contrário ``~/.config/endo-dsl/config.json``.

Suporta chaves "pontilhadas" (ex.: ``editor.tab_size``) e variáveis de ambiente
que têm precedência sobre o arquivo para um subconjunto de chaves.
"""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# --------------------------------------------------------------------------- #
# Valores padrão
# --------------------------------------------------------------------------- #
DEFAULTS: Dict[str, Any] = {
    "theme": "endo",            # light | dark | auto | <nome de tema>
    "backend": "template",      # template | claude
    "model": "claude-sonnet-4-20250514",
    "db_path": None,            # None => usa default_db_path() do banco
    "default_domain": "Matemática",
    "default_bloom": "Analisar",
    "editor": {
        "tab_size": 2,
        "font": "JetBrains Mono",
    },
    "output_dir": None,         # None => diretório de trabalho atual
    "locale": "pt-BR",          # pt-BR | en
}

# Variáveis de ambiente -> chave pontilhada. Têm precedência sobre o arquivo.
_ENV_OVERRIDES = {
    "ENDO_DSL_DB": "db_path",
    "ENDO_DSL_BACKEND": "backend",
    "ENDO_DSL_THEME": "theme",
    "ANTHROPIC_MODEL": "model",
}


# --------------------------------------------------------------------------- #
# Localização do arquivo
# --------------------------------------------------------------------------- #
def config_path() -> Path:
    """Resolve o caminho do arquivo de configuração do usuário."""
    explicit = os.environ.get("ENDO_DSL_CONFIG")
    if explicit:
        return Path(explicit).expanduser()
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg).expanduser() if xdg else Path.home() / ".config"
    return base / "endo-dsl" / "config.json"


# --------------------------------------------------------------------------- #
# Carga/persistência
# --------------------------------------------------------------------------- #
def _deep_merge(base: Dict[str, Any], over: Dict[str, Any]) -> Dict[str, Any]:
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _apply_env(cfg: Dict[str, Any]) -> Dict[str, Any]:
    cfg = copy.deepcopy(cfg)
    for env, key in _ENV_OVERRIDES.items():
        val = os.environ.get(env)
        if val:
            _set_dotted(cfg, key, val)
    # Se há chave de API mas backend não foi escolhido explicitamente, prefira claude.
    if os.environ.get("ANTHROPIC_API_KEY") and "ENDO_DSL_BACKEND" not in os.environ:
        if cfg.get("backend") == DEFAULTS["backend"]:
            cfg["backend"] = "claude"
    return cfg


def load_config(*, with_env: bool = True) -> Dict[str, Any]:
    """Carrega a configuração: DEFAULTS <- arquivo <- variáveis de ambiente."""
    cfg = copy.deepcopy(DEFAULTS)
    path = config_path()
    if path.exists():
        try:
            stored = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(stored, dict):
                cfg = _deep_merge(cfg, stored)
        except (ValueError, OSError):
            pass
    if with_env:
        cfg = _apply_env(cfg)
    return cfg


def save_config(d: Dict[str, Any]) -> Path:
    """Persiste o dicionário de configuração no arquivo do usuário."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def reset() -> Path:
    """Restaura a configuração para os padrões (regrava o arquivo)."""
    return save_config(copy.deepcopy(DEFAULTS))


# --------------------------------------------------------------------------- #
# Acesso por chave pontilhada
# --------------------------------------------------------------------------- #
def _get_dotted(d: Dict[str, Any], key: str, default: Any = None) -> Any:
    cur: Any = d
    for part in key.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def _set_dotted(d: Dict[str, Any], key: str, value: Any) -> None:
    parts = key.split(".")
    cur = d
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[part] = nxt
        cur = nxt
    cur[parts[-1]] = value


def _coerce(value: str) -> Any:
    """Converte strings da CLI para tipos JSON razoáveis."""
    low = value.strip().lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "none", ""):
        return None
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def get(key: str, default: Any = None) -> Any:
    """Lê uma chave (pontilhada) da configuração efetiva."""
    cfg = load_config()
    sentinel = object()
    val = _get_dotted(cfg, key, sentinel)
    if val is sentinel:
        return default
    return val


def set(key: str, value: Any) -> Dict[str, Any]:  # noqa: A001 - API intencional
    """Define uma chave (pontilhada) e persiste. Strings são convertidas de tipo."""
    cfg = load_config(with_env=False)
    if isinstance(value, str):
        value = _coerce(value)
    _set_dotted(cfg, key, value)
    save_config(cfg)
    return cfg


def flatten(d: Optional[Dict[str, Any]] = None, prefix: str = "") -> Dict[str, Any]:
    """Achata o dicionário de configuração em chaves pontilhadas (para listagem)."""
    d = d if d is not None else load_config()
    out: Dict[str, Any] = {}
    for k, v in d.items():
        full = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, full + "."))
        else:
            out[full] = v
    return out
