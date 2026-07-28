from flask import Blueprint

produto_bp = Blueprint("produto", __name__, url_prefix="/produtos")


@produto_bp.route("/")
def index():
    return "<h1>Hello from Produtos controller</h1><p>Produto blueprint — estrutura inicial</p>"
