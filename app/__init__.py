from flask import Flask

from app.controllers.main_controller import front_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(front_bp)

    return app
