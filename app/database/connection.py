import sqlite3
from flask import g


class Database:
    """Conexão única com o banco SQLite, gerenciada pelo Flask."""

    def __init__(self, db_path: str = "techstock.db"):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Retorna a conexão ativa (cria uma se não existir)."""
        if "db" not in g:
            g.db = sqlite3.connect(self.db_path)
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    def close_connection(self, exception=None):
        """Fecha a conexão ao final da requisição."""
        db = g.pop("db", None)
        if db is not None:
            db.close()
