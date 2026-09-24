def test_consulta_total_de_produtos(db_conn):
    total = db_conn.execute("SELECT COUNT(*) AS total FROM produtos").fetchone()["total"]
    assert total > 0


def test_consulta_total_de_estoque_baixo(db_conn):
    baixo = db_conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM (
            SELECT p.id
            FROM produtos p
            LEFT JOIN estoque e ON e.produto_id = p.id
            GROUP BY p.id
            HAVING COALESCE(SUM(e.quantidade), 0) <= p.estoque_min
        )
        """
    ).fetchone()["total"]

    assert baixo >= 0


def test_consulta_por_categoria(db_conn):
    categorias = db_conn.execute(
        "SELECT categoria, COUNT(*) AS total_itens FROM produtos GROUP BY categoria ORDER BY categoria"
    ).fetchall()

    assert len(categorias) > 0
    assert all(row["total_itens"] >= 0 for row in categorias)
