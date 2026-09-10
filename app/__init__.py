import os
from flask import Flask, url_for, current_app

from app.controllers.main_controller import front_bp
from app.controllers.api_controller import api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-techstock-2026")

    app.register_blueprint(front_bp)
    app.register_blueprint(api_bp)

    def handle_build_error(error, endpoint, values):
        if f"front.{endpoint}" in current_app.view_functions:
            return url_for(f"front.{endpoint}", **values)
        if f"api.{endpoint}" in current_app.view_functions:
            return url_for(f"api.{endpoint}", **values)
        return None

    app.url_build_error_handlers.append(handle_build_error)

    return app
