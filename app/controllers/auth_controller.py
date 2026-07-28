from flask import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/")
def index():
    return "<h1>Hello from Auth controller</h1><p>Auth blueprint — estrutura inicial</p>"
