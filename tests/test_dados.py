import sqlite3


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


def test_seed_cria_estrutura_esperada(db_conn):
    tabelas = db_conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    nomes = {row["name"] for row in tabelas}

    assert "usuarios" in nomes
    assert "produtos" in nomes
    assert "estoque" in nomes
    assert "movimentacoes" in nomes
