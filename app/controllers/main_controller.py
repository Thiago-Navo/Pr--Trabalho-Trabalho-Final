from flask import Blueprint, render_template

from app.database import close_connection
from app.models.produto import Produto

front_bp = Blueprint("front", __name__)


@front_bp.route("/")
def index():
    """Página inicial — os dados são carregados via model e passados ao template."""
    try:
        total_produtos = Produto.contar_total()
    except Exception:
        total_produtos = 0
    return render_template("index.html", total_produtos=total_produtos)


@front_bp.route("/sobre")
def sobre():
    return render_template("sobre.html")


@front_bp.teardown_request
def close_db(exception=None):
    """Fecha a conexão com o banco ao final de cada requisição."""
    close_connection(exception)
