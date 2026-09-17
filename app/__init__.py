import os
import sqlite3
from flask import Flask, url_for, current_app

from app.database import database
from app.controllers.main_controller import front_bp
from app.controllers.api_controller import api_bp


def init_database_if_needed():
    """Garante que em qualquer máquina nova o banco e tabelas sejam criados e populados automaticamente."""
    try:
        conn = sqlite3.connect(database.db_path)
        cursor = conn.cursor()
        tabela = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'").fetchone()
        conn.close()
        if not tabela:
            print("[INFO] Banco de dados não encontrado ou vazio. Executando seed automático...")
            from app.seed import seed
            seed()
    except Exception as e:
        print(f"[AVISO] Erro ao verificar/inicializar banco de dados automático: {e}")


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-techstock-2026")

    # Auto-inicializa o banco e seed se for a primeira vez rodando no PC
    init_database_if_needed()

    @app.teardown_appcontext
    def fechar_conexao_db(exc):
        database.close_connection(exc)

    app.register_blueprint(front_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def erro_404(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def erro_500(error):
        return render_template("errors/500.html"), 500

    def handle_build_error(error, endpoint, values):
        if f"front.{endpoint}" in current_app.view_functions:
            return url_for(f"front.{endpoint}", **values)
        if f"api.{endpoint}" in current_app.view_functions:
            return url_for(f"api.{endpoint}", **values)
        return None

    app.url_build_error_handlers.append(handle_build_error)

    return app
