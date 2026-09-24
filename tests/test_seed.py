def test_seed_cria_usuario_admin_padrao(db_conn):
    usuario = db_conn.execute(
        "SELECT usuario, email, papel FROM usuarios WHERE usuario = ?",
        ("admin",),
    ).fetchone()

    assert usuario is not None
    assert usuario["email"] == "admin@techstock.com"
    assert usuario["papel"] == "admin"


def test_seed_cria_usuarios_operadores(db_conn):
    usuarios = db_conn.execute(
        "SELECT usuario, papel FROM usuarios WHERE papel = 'operador' ORDER BY usuario"
    ).fetchall()

    nomes = [row["usuario"] for row in usuarios]
    assert "thiago" in nomes
    assert "mauricio" in nomes
