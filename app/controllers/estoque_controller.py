from flask import Blueprint

estoque_bp = Blueprint("estoque", __name__, url_prefix="/estoque")


@estoque_bp.route("/")
def index():
    return "<h1>Hello from Estoque controller</h1><p>Estoque blueprint — estrutura inicial</p>"
