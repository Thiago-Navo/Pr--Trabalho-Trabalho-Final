from flask import Blueprint

movimento_bp = Blueprint("movimento", __name__, url_prefix="/movimentos")


@movimento_bp.route("/")
def index():
    return "<h1>Hello from Movimentos controller</h1><p>Movimento blueprint — estrutura inicial</p>"
