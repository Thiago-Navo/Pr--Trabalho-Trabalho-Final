import os
import gc
import sqlite3
import pytest

from app.database import database
from app.seed import seed


def _safe_remove(path):
    gc.collect()
    if os.path.exists(path):
        try:
            os.remove(path)
        except (PermissionError, OSError):
            pass


@pytest.fixture
def db_conn():
    database.db_path = "techstock_test_pytest.db"
    _safe_remove(database.db_path)

    seed()
    conn = sqlite3.connect(database.db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

    _safe_remove(database.db_path)


@pytest.fixture
def app_client():
    database.db_path = "techstock_test_app.db"
    _safe_remove(database.db_path)

    seed()
    app = __import__("app", fromlist=["create_app"]).create_app()
    app.config["TESTING"] = True

    with app.app_context():
        with app.test_client() as client:
            yield client
        database.close_connection()

    _safe_remove(database.db_path)
