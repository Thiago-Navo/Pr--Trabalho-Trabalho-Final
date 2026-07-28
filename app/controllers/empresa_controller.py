from flask import Blueprint

empresa_bp = Blueprint("empresa", __name__, url_prefix="/empresas")


@empresa_bp.route("/")
def index():
    return "<h1>Hello from Empresas controller</h1><p>Empresa blueprint — estrutura inicial</p>"
