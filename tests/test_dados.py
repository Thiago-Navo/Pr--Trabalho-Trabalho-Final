import sqlite3

from app import migrar_rua_historico
from app.database import database


def test_dashboard_mostra_indicadores_essenciais(app_client):
    login = app_client.post(
        "/login",
        data={"usuario": "admin", "senha": "admin123"},
        follow_redirects=False,
    )
    assert login.status_code == 302

    resposta = app_client.get("/dashboard")
    assert resposta.status_code == 200
    html = resposta.get_data(as_text=True)
    assert "Produtos cadastrados" in html
    assert "Estoque baixo" in html
    assert "Movimentações dos últimos 7 dias" in html


def test_relatorio_standalone_gera_html(app_client):
    login = app_client.post(
        "/login",
        data={"usuario": "admin", "senha": "admin123"},
        follow_redirects=False,
    )
    assert login.status_code == 302

    resposta = app_client.get("/exportar-relatorio")
    assert resposta.status_code == 200
    html = resposta.get_data(as_text=True)
    assert "Relatório Standalone" in html
    assert "TechStock" in html
    assert "<html" in html.lower()
    assert resposta.mimetype == "text/html"
    assert resposta.headers["Content-Disposition"] == "attachment; filename=relatorio_techstock.html"

    dashboard = app_client.get("/dashboard").get_data(as_text=True)
    assert 'data-full-reload class="btn btn-outline-secondary"' in dashboard


def test_seed_cria_estrutura_esperada(db_conn):
    tabelas = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    nomes = {row["name"] for row in tabelas}

    assert "usuarios" in nomes
    assert "produtos" in nomes
    assert "estoque" in nomes
    assert "movimentacoes" in nomes


def test_migracao_permite_desvincular_ruas_sem_perder_historico(tmp_path, monkeypatch):
    caminho_db = tmp_path / "legado.db"
    conn = sqlite3.connect(caminho_db)
    conn.executescript("""
        CREATE TABLE usuarios (id INTEGER PRIMARY KEY);
        CREATE TABLE ruas (id INTEGER PRIMARY KEY);
        CREATE TABLE produtos (id INTEGER PRIMARY KEY);
        CREATE TABLE entradas (
            id INTEGER PRIMARY KEY,
            produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
            rua_id INTEGER NOT NULL REFERENCES ruas(id),
            quantidade INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            usuario_id INTEGER REFERENCES usuarios(id),
            data TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE saidas (
            id INTEGER PRIMARY KEY,
            produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
            rua_id INTEGER NOT NULL REFERENCES ruas(id),
            quantidade INTEGER NOT NULL,
            motivo TEXT,
            usuario_id INTEGER REFERENCES usuarios(id),
            data TEXT NOT NULL DEFAULT (datetime('now'))
        );
        INSERT INTO usuarios VALUES (1);
        INSERT INTO ruas VALUES (1);
        INSERT INTO produtos VALUES (1);
        INSERT INTO entradas (id, produto_id, rua_id, quantidade, tipo, usuario_id)
        VALUES (1, 1, 1, 4, 'reabastecimento', 1);
        INSERT INTO saidas (id, produto_id, rua_id, quantidade, usuario_id)
        VALUES (1, 1, 1, 2, 1);
    """)
    conn.close()

    monkeypatch.setattr(database, "db_path", str(caminho_db))
    migrar_rua_historico()

    conn = sqlite3.connect(caminho_db)
    try:
        entrada = conn.execute("SELECT rua_id, quantidade FROM entradas WHERE id = 1").fetchone()
        saida = conn.execute("SELECT rua_id, quantidade FROM saidas WHERE id = 1").fetchone()
        nulaveis = {
            tabela: next(coluna for coluna in conn.execute(f"PRAGMA table_info({tabela})") if coluna[1] == "rua_id")[3]
            for tabela in ("entradas", "saidas")
        }
    finally:
        conn.close()

    assert entrada == (1, 4)
    assert saida == (1, 2)
    assert nulaveis == {"entradas": 0, "saidas": 0}
