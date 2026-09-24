from app.utils.paginacao import Paginacao


def test_paginacao_calculo_basico():
    pag = Paginacao(itens=list(range(10)), pagina=1, por_pagina=10, total_itens=25)
    assert pag.total_paginas == 3
    assert pag.pagina == 1
    assert pag.inicio_registro == 1
    assert pag.fim_registro == 10
    assert not pag.tem_anterior
    assert pag.tem_proximo
    assert pag.proxima_pagina == 2
    assert pag.range_paginas == [1, 2, 3]


def test_paginacao_segunda_pagina():
    pag = Paginacao(itens=list(range(10)), pagina=2, por_pagina=10, total_itens=25)
    assert pag.pagina == 2
    assert pag.inicio_registro == 11
    assert pag.fim_registro == 20
    assert pag.tem_anterior
    assert pag.pagina_anterior == 1
    assert pag.tem_proximo
    assert pag.proxima_pagina == 3


def test_paginacao_ultima_pagina_incompleta():
    pag = Paginacao(itens=list(range(5)), pagina=3, por_pagina=10, total_itens=25)
    assert pag.pagina == 3
    assert pag.inicio_registro == 21
    assert pag.fim_registro == 25
    assert pag.tem_anterior
    assert not pag.tem_proximo


def test_paginacao_sem_itens():
    pag = Paginacao(itens=[], pagina=1, por_pagina=10, total_itens=0)
    assert pag.total_paginas == 1
    assert pag.total_itens == 0
    assert pag.inicio_registro == 0
    assert pag.fim_registro == 0
    assert not pag.tem_anterior
    assert not pag.tem_proximo
    assert pag.range_paginas == [1]


def test_paginacao_limites_clamp():
    # Página menor que 1 ajusta para 1
    pag_min = Paginacao(itens=[], pagina=0, por_pagina=10, total_itens=30)
    assert pag_min.pagina == 1

    # Página maior que total_paginas ajusta para total_paginas
    pag_max = Paginacao(itens=[], pagina=99, por_pagina=10, total_itens=30)
    assert pag_max.pagina == 3


def test_paginacao_com_reticencias():
    # Muitas páginas (ex: 20 páginas, página 10 ativa)
    pag = Paginacao(itens=[], pagina=10, por_pagina=5, total_itens=100)
    assert pag.total_paginas == 20
    rng = pag.range_paginas
    assert 1 in rng
    assert 20 in rng
    assert "..." in rng
    assert 10 in rng


def test_rotas_com_paginacao(app_client):
    # Login como admin
    login_resp = app_client.post("/login", data={"usuario": "admin", "senha": "admin123"}, follow_redirects=True)
    assert login_resp.status_code == 200

    resp = app_client.get("/produtos?page=1")
    assert resp.status_code == 200
    assert b"paginacao" in resp.data or b"pagination" in resp.data

    resp_ruas = app_client.get("/ruas?page=1")
    assert resp_ruas.status_code == 200

    resp_mov = app_client.get("/movimentacoes?page=1")
    assert resp_mov.status_code == 200

    resp_ent = app_client.get("/entradas?page=1")
    assert resp_ent.status_code == 200

    resp_sai = app_client.get("/saidas?page=1")
    assert resp_sai.status_code == 200
