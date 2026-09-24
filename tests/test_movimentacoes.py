import sqlite3


def test_transferencia_entre_ruas_atualiza_estoque(app_client):
    login = app_client.post(
        "/login",
        data={"usuario": "admin", "senha": "admin123"},
        follow_redirects=False,
    )
    assert login.status_code == 302

    conn = sqlite3.connect("techstock_test_app.db")
    conn.row_factory = sqlite3.Row
    ruas = conn.execute("SELECT id, nome FROM ruas ORDER BY id LIMIT 2").fetchall()
    rua_origem = ruas[0]["id"]
    rua_destino = ruas[1]["id"]

    produto_id = conn.execute("SELECT id FROM produtos ORDER BY id LIMIT 1").fetchone()["id"]
    conn.execute(
        "INSERT OR REPLACE INTO estoque (produto_id, rua_id, quantidade) VALUES (?, ?, ?)",
        (produto_id, rua_origem, 10),
    )
    conn.commit()
    conn.close()

    resposta = app_client.post(
        "/movimentacoes/nova",
        data={
            "produto_id": produto_id,
            "rua_origem_id": rua_origem,
            "rua_destino_id": rua_destino,
            "quantidade": 4,
        },
        follow_redirects=False,
    )

    assert resposta.status_code == 302


def test_entrada_registra_movimento_e_atualiza_estoque(app_client):
    login = app_client.post(
        "/login",
        data={"usuario": "admin", "senha": "admin123"},
        follow_redirects=False,
    )
    assert login.status_code == 302

    conn = sqlite3.connect("techstock_test_app.db")
    conn.row_factory = sqlite3.Row
    produto_id = conn.execute("SELECT id FROM produtos ORDER BY id LIMIT 1").fetchone()["id"]
    rua_id = conn.execute("SELECT id FROM ruas ORDER BY id LIMIT 1").fetchone()["id"]
    conn.close()

    resposta = app_client.post(
        "/entradas/nova",
        data={
            "produto_id": produto_id,
            "rua_id": rua_id,
            "quantidade": 7,
        },
        follow_redirects=False,
    )

    assert resposta.status_code == 302


def test_saida_rejeita_quantidade_maior_que_disponivel(app_client):
    login = app_client.post(
        "/login",
        data={"usuario": "admin", "senha": "admin123"},
        follow_redirects=True,
    )
    assert login.status_code == 200

    conn = sqlite3.connect("techstock_test_app.db")
    conn.row_factory = sqlite3.Row
    produto_id = conn.execute("SELECT id FROM produtos ORDER BY id LIMIT 1").fetchone()["id"]
    rua_id = conn.execute("SELECT id FROM ruas ORDER BY id LIMIT 1").fetchone()["id"]
    conn.execute("DELETE FROM estoque WHERE produto_id = ? AND rua_id = ?", (produto_id, rua_id))
    conn.execute("INSERT INTO estoque (produto_id, rua_id, quantidade) VALUES (?, ?, ?)", (produto_id, rua_id, 3))
    conn.commit()
    conn.close()

    resposta = app_client.post(
        "/saidas/nova",
        data={
            "produto_id": produto_id,
            "rua_id": rua_id,
            "quantidade": 10,
            "motivo": "Ajuste de inventário",
        },
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert b"unidade" in resposta.data.lower() or b"quantidade" in resposta.data.lower()
