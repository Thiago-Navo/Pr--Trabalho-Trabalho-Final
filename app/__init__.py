from flask import Flask

from app.controllers.auth_controller import auth_bp
from app.controllers.categoria_controller import categoria_bp
from app.controllers.empresa_controller import empresa_bp
from app.controllers.estoque_controller import estoque_bp
from app.controllers.main_controller import front_bp
from app.controllers.movimento_controller import movimento_bp
from app.controllers.produto_controller import produto_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder="static")

    # Blueprints
    app.register_blueprint(front_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(produto_bp)
    app.register_blueprint(empresa_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(movimento_bp)
    app.register_blueprint(estoque_bp)

    return app
