import sqlite3


def test_cadastro_de_produto_com_sucesso(app_client):
    login = app_client.post(
        "/login",
        data={"usuario": "admin", "senha": "admin123"},
        follow_redirects=False,
    )
    assert login.status_code == 302

    rua = app_client.post("/ruas/nova", data={"nome": "Rua Produtos"}, follow_redirects=False)
    assert rua.status_code == 302

    conn = sqlite3.connect("techstock_test_app.db")
    conn.row_factory = sqlite3.Row
    rua_id = conn.execute("SELECT id FROM ruas WHERE nome = ?", ("Rua Produtos",)).fetchone()["id"]

    resposta = app_client.post(
        "/produtos/novo",
        data={
            "nome": "Teclado Gamer",
            "sku": "TEC-001",
            "categoria": "Periféricos",
            "rua_id": rua_id,
            "qtd": 10,
            "estoque_min": 2,
            "estoque_max": 50,
        },
        follow_redirects=False,
    )
    conn.close()

    assert resposta.status_code == 302


def test_produto_nao_pode_ser_cadastrado_sem_rua(app_client):
    login = app_client.post(
        "/login",
        data={"usuario": "admin", "senha": "admin123"},
        follow_redirects=False,
    )
    assert login.status_code == 302

    resposta = app_client.post(
        "/produtos/novo",
        data={
            "nome": "Mouse Sem Fio",
            "sku": "MOU-001",
            "categoria": "Periféricos",
            "rua_id": "",
            "qtd": 5,
            "estoque_min": 1,
            "estoque_max": 20,
        },
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert b"Cadastre uma rua antes de criar produtos." in resposta.data or b"Escolha a rua" in resposta.data


def test_produto_duplicado_gera_erro(app_client):
    login = app_client.post(
        "/login",
        data={"usuario": "admin", "senha": "admin123"},
        follow_redirects=False,
    )
    assert login.status_code == 302

    conn = sqlite3.connect("techstock_test_app.db")
    conn.row_factory = sqlite3.Row
    rua_id = conn.execute("SELECT id FROM ruas ORDER BY id LIMIT 1").fetchone()["id"]
    conn.close()

    primeiro = app_client.post(
        "/produtos/novo",
        data={
            "nome": "Monitor 24 polegadas",
            "sku": "MON-24",
            "categoria": "Periféricos",
            "rua_id": rua_id,
            "qtd": 4,
            "estoque_min": 1,
            "estoque_max": 20,
        },
        follow_redirects=False,
    )
    assert primeiro.status_code == 302

    duplicado = app_client.post(
        "/produtos/novo",
        data={
            "nome": "Monitor 24 polegadas v2",
            "sku": "MON-24",
            "categoria": "Periféricos",
            "rua_id": rua_id,
            "qtd": 3,
            "estoque_min": 1,
            "estoque_max": 20,
        },
        follow_redirects=True,
    )

    assert duplicado.status_code == 200
    assert b"produto" in duplicado.data.lower()
    assert b"SKU" in duplicado.data or b"sku" in duplicado.data.lower()


def test_gerenciamento_de_categorias(app_client):
    login = app_client.post(
        "/login",
        data={"usuario": "admin", "senha": "admin123"},
        follow_redirects=False,
    )
    assert login.status_code == 302

    resp_add = app_client.post(
        "/categorias/nova",
        data={"nome": "Acessórios VR"},
        follow_redirects=True,
    )
    assert resp_add.status_code == 200
    assert b"Acess\xc3\xb3rios VR" in resp_add.data or b"Acess" in resp_add.data

    conn = sqlite3.connect("techstock_test_app.db")
    conn.row_factory = sqlite3.Row
    cat = conn.execute("SELECT id FROM categorias WHERE nome = ?", ("Acessórios VR",)).fetchone()
    conn.close()
    assert cat is not None

    resp_del = app_client.post(f"/categorias/{cat['id']}/excluir", follow_redirects=True)
    assert resp_del.status_code == 200

