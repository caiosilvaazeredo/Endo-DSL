"""Gerência de conexão e inicialização do banco SQLite.

Centraliza a abertura de conexões (com chaves estrangeiras e ``row_factory``
configurados), a aplicação do esquema (``schema.sql``) e utilitários de
serialização JSON usados por toda a plataforma.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Optional

_SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def default_db_path() -> Path:
    """Caminho padrão do banco (sobreponível por ``ENDO_DSL_DB``)."""
    env = os.environ.get("ENDO_DSL_DB")
    if env:
        return Path(env)
    root = Path(os.environ.get("ENDO_DSL_HOME", Path.cwd() / "data"))
    return root / "endo_dsl.sqlite3"


def now_iso() -> str:
    """Timestamp ISO-8601 em UTC (segundos)."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=False)


def from_json(text: Optional[str], default: Any = None) -> Any:
    if not text:
        return default
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return default


def connect(path: Optional[os.PathLike | str] = None) -> sqlite3.Connection:
    """Abre uma conexão SQLite com FKs ligadas e linhas acessíveis por nome."""
    db_path = Path(path) if path is not None else default_db_path()
    if str(db_path) != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


class Database:
    """Fachada fina sobre uma conexão SQLite, com inicialização de esquema.

    Pode ser usada como context manager::

        with Database("data/endo_dsl.sqlite3") as db:
            db.execute("SELECT 1")
    """

    def __init__(self, path: Optional[os.PathLike | str] = None, *, init: bool = True):
        self.path = Path(path) if path is not None else default_db_path()
        self.conn = connect(self.path)
        if init:
            self.initialize()

    # -- ciclo de vida ------------------------------------------------- #
    def initialize(self) -> None:
        """Aplica ``schema.sql`` (idempotente)."""
        sql = _SCHEMA_PATH.read_text(encoding="utf-8")
        self.conn.executescript(sql)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- helpers ------------------------------------------------------- #
    def execute(self, sql: str, params: Iterable[Any] = ()) -> sqlite3.Cursor:
        return self.conn.execute(sql, tuple(params))

    def executemany(self, sql: str, seq: Iterable[Iterable[Any]]) -> sqlite3.Cursor:
        return self.conn.executemany(sql, [tuple(p) for p in seq])

    def query_one(self, sql: str, params: Iterable[Any] = ()) -> Optional[sqlite3.Row]:
        return self.conn.execute(sql, tuple(params)).fetchone()

    def query_all(self, sql: str, params: Iterable[Any] = ()) -> List[sqlite3.Row]:
        return list(self.conn.execute(sql, tuple(params)).fetchall())

    def insert(self, sql: str, params: Iterable[Any] = ()) -> int:
        """Executa um INSERT e retorna o ``lastrowid``."""
        cur = self.conn.execute(sql, tuple(params))
        self.conn.commit()
        return int(cur.lastrowid)

    def commit(self) -> None:
        self.conn.commit()
