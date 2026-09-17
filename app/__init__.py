from flask import Flask

from app.controllers.main_controller import front_bp
from app.controllers.api_controller import api_bp # Registro do Controller da API - POR DEV MAURICIO

def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(front_bp)
    app.register_blueprint(api_bp)

    return app
