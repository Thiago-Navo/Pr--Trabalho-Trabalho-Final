import sqlite3
from flask import g


def get_connection() -> sqlite3.Connection:
    """Retorna a conexão ativa (cria uma se não existir)."""
    if "db" not in g:
        g.db = sqlite3.connect("techstock.db")
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def execute(sql: str, params: tuple = ()) -> sqlite3.Cursor:
    """Executa uma instrução SQL com transação (BEGIN / COMMIT / ROLLBACK)."""
    db = get_connection()
    try:
        db.execute("BEGIN")
        cursor = db.execute(sql, params)
        db.commit()
        return cursor
    except Exception:
        db.rollback()
        raise


def fetch_one(sql: str, params: tuple = ()):
    """Retorna uma única linha ou None."""
    db = get_connection()
    return db.execute(sql, params).fetchone()


def fetch_all(sql: str, params: tuple = ()) -> list:
    """Retorna todas as linhas."""
    db = get_connection()
    return db.execute(sql, params).fetchall()


def close_connection(exception=None):
    """Fecha a conexão ao final da requisição."""
    db = g.pop("db", None)
    if db is not None:
        db.close()
