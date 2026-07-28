from flask import Blueprint

categoria_bp = Blueprint("categoria", __name__, url_prefix="/categorias")


@categoria_bp.route("/")
def index():
    return "<h1>Hello from Categorias controller</h1><p>Categoria blueprint — estrutura inicial</p>"
