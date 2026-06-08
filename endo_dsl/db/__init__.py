"""Camada de persistência (SQLite) da plataforma Endo-DSL."""

from endo_dsl.db.database import Database, default_db_path, connect

__all__ = ["Database", "default_db_path", "connect"]
