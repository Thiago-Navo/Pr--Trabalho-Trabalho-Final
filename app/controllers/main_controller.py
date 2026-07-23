from flask import Blueprint, render_template, g

from app.database import database

front_bp = Blueprint("front", __name__)


@front_bp.route("/")
def index():
    """Página inicial — os dados são carregados via model e passados ao template."""
    db = database.get_connection()
    # Exemplo: total de produtos cadastrados
    total_produtos = db.execute("SELECT COUNT(*) AS total FROM produto").fetchone()["total"]

    return render_template("index.html", total_produtos=total_produtos)


@front_bp.route("/sobre")
def sobre():
    return render_template("sobre.html")


@front_bp.teardown_request
def close_db(exception=None):
    """Fecha a conexão com o banco ao final de cada requisição."""
    database.close_connection(exception)
