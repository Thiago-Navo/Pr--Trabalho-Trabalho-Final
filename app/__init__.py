import os
import logging
import sqlite3
from flask import Flask, url_for, current_app, render_template

from app.database import database
from app.controllers.main_controller import front_bp
from app.controllers.api_controller import api_bp

# Configuração centralizada de Logging do Python
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("techstock")


def init_database_if_needed():
    """Garante que em qualquer máquina nova o banco e tabelas sejam criados e populados automaticamente."""
    try:
        conn = sqlite3.connect(database.db_path)
        cursor = conn.cursor()
        tabela = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'").fetchone()
        conn.close()
        if not tabela:
            logger.info("Banco de dados não encontrado ou vazio. Executando seed automático...")
            from app.seed import seed
            seed()
    except Exception as e:
        logger.warning(f"Erro ao verificar/inicializar banco de dados automático: {e}")


def formatar_data_br(valor):
    """Converte datas em formato ISO/SQLite (YYYY-MM-DD HH:MM:SS) para padrão brasileiro com hora (DD/MM/YYYY às HH:MM)."""
    if not valor:
        return "—"
    try:
        if isinstance(valor, str):
            val_limpo = valor.strip().replace("T", " ")
            partes = val_limpo.split(" ")
            data_parte = partes[0]
            hora_parte = partes[1] if len(partes) > 1 else ""

            if "-" in data_parte:
                pedacos = data_parte.split("-")
                if len(pedacos) >= 3:
                    ano, mes, dia = pedacos[:3]
                    data_br = f"{dia.zfill(2)}/{mes.zfill(2)}/{ano}"
                else:
                    data_br = data_parte
            else:
                data_br = data_parte

            if hora_parte:
                horas = hora_parte.split(":")[:2]
                return f"{data_br} às {':'.join(horas)}"
            return data_br
        elif hasattr(valor, "strftime"):
            return valor.strftime("%d/%m/%Y às %H:%M")
        return str(valor)
    except Exception:
        return str(valor)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "chave-secreta-techstock-2026")

    # Registra filtro Jinja2 para padrão de data e hora brasileiro
    app.jinja_env.filters["data_br"] = formatar_data_br

    # Auto-inicializa o banco e seed se for a primeira vez rodando no PC
    init_database_if_needed()

    @app.teardown_appcontext
    def fechar_conexao_db(exc):
        database.close_connection(exc)

    app.register_blueprint(front_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_globals():
        from flask import session
        def rascunho_de(chave):
            return session.get(f"rascunho_{chave}", {})

        def rascunho_extra(chave):
            return session.get(f"rascunho_extra_{chave}", {})

        existe_conta = True
        try:
            db = database.get_connection()
            row = db.execute("SELECT COUNT(*) AS n FROM usuarios").fetchone()
            existe_conta = (row["n"] > 0) if row else False
        except Exception:
            pass

        return {
            "rascunho_de": rascunho_de,
            "rascunho_extra": rascunho_extra,
            "rascunho_concluido": session.pop("rascunho_concluido", None),
            "rascunho_chave": session.pop("rascunho_chave", None),
            "existe_conta": existe_conta,
        }

    @app.errorhandler(404)
    def erro_404(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def erro_500(error):
        return render_template("errors/500.html"), 500

    @app.cli.command("init-db")
    def init_db_command():
        """Inicializa e popula o banco de dados via Flask CLI."""
        from app.seed import seed
        seed()
        print("Banco de dados inicializado e populado com sucesso via CLI!")

    def handle_build_error(error, endpoint, values):
        if f"front.{endpoint}" in current_app.view_functions:
            return url_for(f"front.{endpoint}", **values)
        if f"api.{endpoint}" in current_app.view_functions:
            return url_for(f"api.{endpoint}", **values)
        return None

    app.url_build_error_handlers.append(handle_build_error)

    logger.info("Aplicação TechStock inicializada com sucesso.")
    return app

