import sqlite3


def _consultar(sql, parametros=()):
    conn = sqlite3.connect("techstock_test_app.db")
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, parametros).fetchall()
    finally:
        conn.close()


def _criar_produto(client, sufixo):
    nome_rua_origem = f"Rua origem {sufixo}"
    nome_rua_destino = f"Rua destino {sufixo}"
    client.post("/ruas/nova", data={"nome": nome_rua_origem})
    client.post("/ruas/nova", data={"nome": nome_rua_destino})
    ruas = _consultar(
        "SELECT id, nome FROM ruas WHERE nome IN (?, ?)",
        (nome_rua_origem, nome_rua_destino),
    )
    rua_ids = {rua["nome"]: rua["id"] for rua in ruas}

    resposta = client.post(
        "/produtos/novo",
        data={
            "nome": f"Produto jornada {sufixo}",
            "sku": f"JORNADA-{sufixo}",
            "categoria": "Memória",
            "rua_id": rua_ids[nome_rua_origem],
            "qtd": 8,
            "estoque_min": 10,
            "estoque_max": 30,
        },
    )
    assert resposta.status_code == 302
    produto = _consultar("SELECT id FROM produtos WHERE sku = ?", (f"JORNADA-{sufixo}",))[0]
    return produto["id"], rua_ids[nome_rua_origem], rua_ids[nome_rua_destino], nome_rua_origem


def _operar_estoque(client, produto_id, origem_id, destino_id, nome_produto):
    transferencia = client.post(
        "/movimentacoes/nova",
        data={
            "produto_id": produto_id,
            "rua_origem_id": origem_id,
            "rua_destino_id": destino_id,
            "quantidade": 8,
        },
    )
    assert transferencia.status_code == 302

    entrada = client.post(
        "/entradas/nova",
        data={"produto_id": produto_id, "rua_id": destino_id, "quantidade": 5},
    )
    assert entrada.status_code == 302

    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert nome_produto.encode() in dashboard.data

    relatorio = client.get("/exportar-relatorio")
    assert relatorio.status_code == 200
    assert relatorio.mimetype == "text/html"
    assert "attachment; filename=relatorio_techstock.html" in relatorio.headers["Content-Disposition"]
    assert nome_produto.encode() in relatorio.data

    saida = client.post(
        "/saidas/nova",
        data={"produto_id": produto_id, "rua_id": destino_id, "quantidade": 3, "motivo": "Teste de jornada"},
    )
    assert saida.status_code == 302


def test_jornada_completa_admin_e_operador(app_client):
    login_admin = app_client.post("/login", data={"usuario": "admin", "senha": "admin123"})
    assert login_admin.status_code == 302

    produto_id, rua_origem_id, rua_destino_id, _ = _criar_produto(app_client, "ADMIN")
    _operar_estoque(app_client, produto_id, rua_origem_id, rua_destino_id, "Produto jornada ADMIN")

    entrada_origem = app_client.post(
        "/entradas/nova",
        data={"produto_id": produto_id, "rua_id": rua_origem_id, "quantidade": 1},
    )
    assert entrada_origem.status_code == 302
    mover_saldo_final = app_client.post(
        "/movimentacoes/nova",
        data={
            "produto_id": produto_id,
            "rua_origem_id": rua_origem_id,
            "rua_destino_id": rua_destino_id,
            "quantidade": 1,
        },
    )
    assert mover_saldo_final.status_code == 302

    edicao = app_client.post(
        f"/ruas/{rua_origem_id}/editar",
        data={"nome": "Rua admin editada"},
    )
    assert edicao.status_code == 302
    exclusao = app_client.post(f"/ruas/{rua_origem_id}/excluir")
    assert exclusao.status_code == 302
    assert not _consultar("SELECT id FROM ruas WHERE id = ?", (rua_origem_id,))
    assert _consultar("SELECT id FROM entradas WHERE produto_id = ? AND rua_id IS NULL", (produto_id,))
    assert _consultar(
        "SELECT id FROM movimentacoes WHERE produto_id = ? AND (rua_origem_id IS NULL OR rua_destino_id IS NULL)",
        (produto_id,),
    )

    cadastro_operador = app_client.post(
        "/cadastro",
        data={
            "usuario": "operador_teste",
            "senha": "operador123",
            "confirmar_senha": "operador123",
            "papel": "operador",
        },
    )
    assert cadastro_operador.status_code == 302
    assert _consultar("SELECT id FROM usuarios WHERE usuario = 'operador_teste' AND papel = 'operador'")

    app_client.get("/logout")
    login_operador = app_client.post(
        "/login",
        data={"usuario": "operador_teste", "senha": "operador123"},
    )
    assert login_operador.status_code == 302

    produto_operador_id, rua_operador_id, destino_operador_id, nome_rua_operador = _criar_produto(
        app_client, "OPERADOR"
    )
    _operar_estoque(
        app_client,
        produto_operador_id,
        rua_operador_id,
        destino_operador_id,
        "Produto jornada OPERADOR",
    )

    app_client.post(f"/ruas/{rua_operador_id}/editar", data={"nome": "Edição indevida"})
    app_client.post(f"/ruas/{rua_operador_id}/excluir")
    rua_operador = _consultar("SELECT nome FROM ruas WHERE id = ?", (rua_operador_id,))[0]
    assert rua_operador["nome"] == nome_rua_operador