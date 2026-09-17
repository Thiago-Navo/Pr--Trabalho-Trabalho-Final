import os
import sqlite3

import pytest

from app.database import database
from app.seed import seed


@pytest.fixture
def db_conn():
    database.db_path = "techstock_test_pytest.db"
    if os.path.exists(database.db_path):
        os.remove(database.db_path)

    seed()
    conn = sqlite3.connect(database.db_path)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

    if os.path.exists(database.db_path):
        os.remove(database.db_path)


@pytest.fixture
def app_client():
    database.db_path = "techstock_test_app.db"
    if os.path.exists(database.db_path):
        os.remove(database.db_path)

    seed()
    app = __import__("app", fromlist=["create_app"]).create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    yield client

    if os.path.exists(database.db_path):
        os.remove(database.db_path)
