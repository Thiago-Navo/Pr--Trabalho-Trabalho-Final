import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify, g, Response
)
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import database

front_bp = Blueprint("front", __name__)


# --------------------------------------------------------------------------
# Conexão / Sessão
# --------------------------------------------------------------------------

def get_db():
    return database.get_connection()


def _sessao_valida():
    """Confirma que o usuário da sessão ainda existe no banco."""
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return False
    db = get_db()
    try:
        existe = db.execute("SELECT 1 FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        if not existe:
            session.clear()
            return False
        return True
    except Exception:
        return False


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not _sessao_valida():
            flash("Sua sessão expirou ou não é mais válida. Faça login novamente.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not _sessao_valida():
            flash("Sua sessão expirou ou não é mais válida. Faça login novamente.", "warning")
            return redirect(url_for("login"))
        papel = session.get("papel", "")
        if papel != "admin" and papel != "Administradora" and papel != "Administrador":
            flash("Apenas administradores podem fazer isso.", "danger")
            return redirect(request.referrer or url_for("dashboard"))
        return view(*args, **kwargs)
    return wrapped


@front_bp.app_context_processor
def inject_usuario():
    return {
        "usuario_logado": session.get("usuario_nome"),
        "papel_logado": session.get("papel"),
    }


# --------------------------------------------------------------------------
# Login / Cadastro / Logout
# --------------------------------------------------------------------------

@front_bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if _sessao_valida():
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")

        db = get_db()
        # Busca por usuario ou email (case-insensitive)
        row = db.execute("""
            SELECT * FROM usuarios
            WHERE (LOWER(usuario) = LOWER(?) OR LOWER(nome) = LOWER(?) OR LOWER(email) = LOWER(?))
        """, (usuario, usuario, usuario)).fetchone()

        if row:
            r = dict(row)
            senha_hash = r.get("senha_hash") or r.get("senha")
            valida = False
            if senha_hash and str(senha_hash).startswith(("scrypt:", "pbkdf2:")):
                valida = check_password_hash(senha_hash, senha)
            elif senha_hash:
                valida = (senha_hash == senha)

            if valida:
                session.clear()
                session["usuario_id"] = r["id"]
                nome_exibicao = r.get("usuario") or r.get("nome") or usuario
                session["usuario_nome"] = nome_exibicao
                papel = r.get("papel") or ("admin" if r.get("cargo") in ("Administradora", "Administrador", "admin") else "operador")
                session["papel"] = papel
                flash(f"Bem-vindo(a), {nome_exibicao}!", "success")
                destino = request.args.get("next") or url_for("dashboard")
                return redirect(destino)

        flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html")


@front_bp.route("/cadastro", methods=["GET", "POST"], endpoint="cadastro")
def cadastro():
    criando_como_admin = _sessao_valida() and session.get("papel") == "admin"
    if _sessao_valida() and not criando_como_admin:
        return redirect(url_for("dashboard"))

    db = get_db()
    total_usr = db.execute("SELECT COUNT(*) AS n FROM usuarios").fetchone()["n"]
    existe_algum_usuario = total_usr > 0

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        confirmar = request.form.get("confirmar_senha", "")
        papel = request.form.get("papel", "operador")

        erros = []
        if len(usuario) < 3:
            erros.append("O usuário precisa ter ao menos 3 caracteres.")
        if len(senha) < 6:
            erros.append("A senha precisa ter ao menos 6 caracteres.")
        if senha != confirmar:
            erros.append("As senhas não conferem.")
        if papel not in ("admin", "operador"):
            papel = "operador"

        if not existe_algum_usuario:
            papel = "admin"
        elif not criando_como_admin:
            papel = "operador"

        if not erros:
            ja_existe = db.execute(
                "SELECT 1 FROM usuarios WHERE LOWER(usuario) = LOWER(?) OR LOWER(nome) = LOWER(?)",
                (usuario, usuario)
            ).fetchone()
            if ja_existe:
                erros.append("Esse nome de usuário já está em uso.")

        if erros:
            for e in erros:
                flash(e, "danger")
            return render_template(
                "cadastro.html",
                primeiro=not existe_algum_usuario,
                criando_como_admin=criando_como_admin,
                form=request.form,
            )

        hash_senha = generate_password_hash(senha)
        db.execute(
            "INSERT INTO usuarios (usuario, nome, email, senha_hash, papel, cargo) VALUES (?, ?, ?, ?, ?, ?)",
            (usuario, usuario, f"{usuario.lower()}@techstock.com", hash_senha, papel, "Administrador" if papel == "admin" else "Operador"),
        )
        db.commit()

        if criando_como_admin:
            flash(f'Usuário "{usuario}" ({papel}) criado com sucesso.', "success")
            return redirect(url_for("cadastro"))

        flash("Cadastro criado com sucesso! Faça login para continuar.", "success")
        return redirect(url_for("login"))

    return render_template(
        "cadastro.html",
        primeiro=not existe_algum_usuario,
        criando_como_admin=criando_como_admin,
        form={},
    )


@front_bp.route("/logout", endpoint="logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))


@front_bp.route("/", endpoint="home")
def home():
    return redirect(url_for("dashboard"))


# --------------------------------------------------------------------------
# Dashboard
# --------------------------------------------------------------------------

@front_bp.route("/dashboard", endpoint="dashboard")
@login_required
def dashboard():
    db = get_db()

    total_produtos = db.execute("SELECT COUNT(*) AS n FROM produtos").fetchone()["n"]
    total_categorias = db.execute("SELECT COUNT(DISTINCT categoria) AS n FROM produtos").fetchone()["n"]

    saldo_por_produto = db.execute("""
        SELECT p.id, p.nome, p.sku, p.categoria, p.estoque_min, p.estoque_max,
               COALESCE(SUM(e.quantidade), 0) AS qtd_total
        FROM produtos p
        LEFT JOIN estoque e ON e.produto_id = p.id
        GROUP BY p.id
        ORDER BY (COALESCE(SUM(e.quantidade), 0) * 1.0 / NULLIF(p.estoque_max, 0)) ASC
    """).fetchall()

    estoque_baixo = [p for p in saldo_por_produto if p["qtd_total"] <= p["estoque_min"]]
    em_atencao = [p for p in saldo_por_produto if p["qtd_total"] <= p["estoque_min"] * 1.5][:8]

    por_categoria = db.execute("""
        SELECT p.categoria AS categoria, COALESCE(SUM(e.quantidade), 0) AS total
        FROM produtos p
        LEFT JOIN estoque e ON e.produto_id = p.id
        GROUP BY p.categoria
        ORDER BY total DESC
    """).fetchall()

    hoje = datetime.now().date()
    dias = [hoje - timedelta(days=i) for i in range(6, -1, -1)]
    data_inicio = dias[0].isoformat()

    linhas_entrada = db.execute("""
        SELECT date(data) AS dia, SUM(quantidade) AS total
        FROM entradas
        WHERE date(data) >= date(?)
        GROUP BY dia
    """, (data_inicio,)).fetchall()

    linhas_saida = db.execute("""
        SELECT date(data) AS dia, SUM(quantidade) AS total
        FROM saidas
        WHERE date(data) >= date(?)
        GROUP BY dia
    """, (data_inicio,)).fetchall()

    mapa_entrada = {r["dia"]: r["total"] for r in linhas_entrada}
    mapa_saida = {r["dia"]: r["total"] for r in linhas_saida}

    serie_entradas = [mapa_entrada.get(d.isoformat(), 0) for d in dias]
    serie_saidas = [mapa_saida.get(d.isoformat(), 0) for d in dias]

    serie_movimentacoes = {
        "labels": [d.strftime("%d/%m") for d in dias],
        "entradas": serie_entradas,
        "saidas": serie_saidas,
    }

    return render_template(
        "dashboard.html",
        total_produtos=total_produtos,
        total_categorias=total_categorias,
        estoque_baixo=len(estoque_baixo),
        em_atencao=em_atencao,
        por_categoria=por_categoria,
        serie_movimentacoes=serie_movimentacoes,
        entradas_7d=sum(serie_entradas),
        saidas_7d=sum(serie_saidas),
    )


@front_bp.route("/exportar-relatorio", endpoint="exportar_relatorio")
@login_required
def exportar_relatorio():
    db = get_db()

    total_produtos = db.execute("SELECT COUNT(*) AS n FROM produtos").fetchone()["n"]
    total_categorias = db.execute("SELECT COUNT(DISTINCT categoria) AS n FROM produtos").fetchone()["n"]
    estoque_baixo = db.execute("""
        SELECT COUNT(*) AS n
        FROM (
            SELECT p.id
            FROM produtos p
            LEFT JOIN estoque e ON e.produto_id = p.id
            GROUP BY p.id
            HAVING COALESCE(SUM(e.quantidade), 0) <= p.estoque_min
        )
    """).fetchone()["n"]
    por_categoria = db.execute("""
        SELECT p.categoria AS categoria, COALESCE(SUM(e.quantidade), 0) AS total
        FROM produtos p
        LEFT JOIN estoque e ON e.produto_id = p.id
        GROUP BY p.categoria
        ORDER BY total DESC
    """).fetchall()

    itens = []
    for row in por_categoria:
        itens.append(f"<tr><td>{row['categoria'] or 'Sem categoria'}</td><td>{row['total']}</td></tr>")

    html = f"""<!doctype html>
    <html lang=\"pt-BR\">
    <head>
        <meta charset=\"utf-8\">
        <title>Relatório Standalone</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 32px; color: #1f2937; }}
            h1 {{ color: #0f172a; }}
            .cards {{ display: flex; gap: 16px; flex-wrap: wrap; }}
            .card {{ border: 1px solid #dbe3ef; border-radius: 12px; padding: 16px 20px; min-width: 180px; background: #f8fafc; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            th, td {{ border: 1px solid #dbe3ef; padding: 10px; text-align: left; }}
            th {{ background: #e2e8f0; }}
        </style>
    </head>
    <body>
        <h1>Relatório Standalone - TechStock</h1>
        <p>Resumo do estoque gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        <div class=\"cards\">
            <div class=\"card\"><strong>Produtos:</strong><br>{total_produtos}</div>
            <div class=\"card\"><strong>Categorias:</strong><br>{total_categorias}</div>
            <div class=\"card\"><strong>Estoque baixo:</strong><br>{estoque_baixo}</div>
        </div>
        <table>
            <thead><tr><th>Categoria</th><th>Quantidade</th></tr></thead>
            <tbody>{''.join(itens) if itens else '<tr><td colspan="2">Nenhuma categoria cadastrada.</td></tr>'}</tbody>
        </table>
    </body>
    </html>"""

    return Response(html, mimetype="text/html")


# --------------------------------------------------------------------------
# Ruas
# --------------------------------------------------------------------------

@front_bp.route("/ruas", endpoint="ruas")
@login_required
def ruas():
    db = get_db()
    lista = db.execute("""
        SELECT r.*, COALESCE(SUM(e.quantidade), 0) AS qtd_total,
               COUNT(DISTINCT e.produto_id) AS produtos_distintos
        FROM ruas r
        LEFT JOIN estoque e ON e.rua_id = r.id AND e.quantidade > 0
        GROUP BY r.id
        ORDER BY r.nome
    """).fetchall()
    return render_template("ruas.html", ruas=lista)


@front_bp.route("/ruas/nova", methods=["POST"], endpoint="nova_rua")
@login_required
def nova_rua():
    nome = request.form.get("nome", "").strip()
    if not nome:
        flash("Informe um nome para a rua.", "danger")
        return redirect(url_for("ruas"))

    db = get_db()
    ja_existe = db.execute("SELECT 1 FROM ruas WHERE nome = ?", (nome,)).fetchone()
    if ja_existe:
        flash("Já existe uma rua com esse nome.", "danger")
        return redirect(url_for("ruas"))

    db.execute("INSERT INTO ruas (nome, tipo) VALUES (?, NULL)", (nome,))
    db.commit()
    flash(f'Rua "{nome}" criada. Ela ficará disponível para qualquer categoria até receber o primeiro produto.', "success")
    return redirect(url_for("ruas"))


@front_bp.route("/ruas/<int:rua_id>/editar", methods=["POST"], endpoint="editar_rua")
@admin_required
def editar_rua(rua_id):
    db = get_db()
    rua = db.execute("SELECT * FROM ruas WHERE id = ?", (rua_id,)).fetchone()
    if not rua:
        flash("Rua não encontrada.", "danger")
        return redirect(url_for("ruas"))

    nome = request.form.get("nome", "").strip()
    if not nome:
        flash("Informe um nome para a rua.", "danger")
        return redirect(url_for("ruas"))

    ja_existe = db.execute("SELECT 1 FROM ruas WHERE nome = ? AND id != ?", (nome, rua_id)).fetchone()
    if ja_existe:
        flash("Já existe uma rua com esse nome.", "danger")
        return redirect(url_for("ruas"))

    db.execute("UPDATE ruas SET nome = ? WHERE id = ?", (nome, rua_id))
    db.commit()
    flash(f'Rua renomeada para "{nome}".', "success")
    return redirect(url_for("ruas"))


@front_bp.route("/ruas/<int:rua_id>/excluir", methods=["POST"], endpoint="excluir_rua")
@admin_required
def excluir_rua(rua_id):
    db = get_db()
    tem_estoque = db.execute(
        "SELECT COALESCE(SUM(quantidade), 0) AS n FROM estoque WHERE rua_id = ?", (rua_id,)
    ).fetchone()["n"]

    if tem_estoque > 0:
        flash("Não é possível excluir: essa rua ainda tem produtos guardados nela.", "danger")
        return redirect(url_for("ruas"))

    db.execute("DELETE FROM ruas WHERE id = ?", (rua_id,))
    db.commit()
    flash("Rua excluída.", "success")
    return redirect(url_for("ruas"))


# --------------------------------------------------------------------------
# Produtos
# --------------------------------------------------------------------------

@front_bp.route("/produtos", endpoint="produtos")
@login_required
def produtos():
    db = get_db()
    termo = request.args.get("q", "").strip()

    query = """
        SELECT p.*, COALESCE(SUM(e.quantidade), 0) AS qtd_total
        FROM produtos p
        LEFT JOIN estoque e ON e.produto_id = p.id
        WHERE 1=1
    """
    params = []
    if termo:
        query += " AND (p.nome LIKE ? OR p.sku LIKE ? OR p.categoria LIKE ?)"
        params += [f"%{termo}%", f"%{termo}%", f"%{termo}%"]
    query += " GROUP BY p.id ORDER BY p.nome"

    lista = db.execute(query, params).fetchall()
    ruas_disponiveis = db.execute("SELECT * FROM ruas ORDER BY nome").fetchall()
    tem_ruas = len(ruas_disponiveis) > 0

    localizacoes = {}
    for p in lista:
        locs = db.execute("""
            SELECT r.id, r.nome, e.quantidade
            FROM estoque e JOIN ruas r ON r.id = e.rua_id
            WHERE e.produto_id = ? AND e.quantidade > 0
            ORDER BY r.nome
        """, (p["id"],)).fetchall()
        localizacoes[p["id"]] = locs

    return render_template(
        "produtos.html",
        produtos=lista,
        ruas=ruas_disponiveis,
        tem_ruas=tem_ruas,
        termo=termo,
        localizacoes=localizacoes,
    )


@front_bp.route("/produtos/novo", methods=["POST"], endpoint="novo_produto")
@login_required
def novo_produto():
    db = get_db()

    total_ruas = db.execute("SELECT COUNT(*) AS n FROM ruas").fetchone()["n"]
    if total_ruas == 0:
        flash("Cadastre uma rua antes de criar produtos.", "danger")
        return redirect(url_for("produtos"))

    nome = request.form.get("nome", "").strip()
    sku = request.form.get("sku", "").strip()
    categoria = request.form.get("categoria", "").strip()
    rua_id = request.form.get("rua_id", type=int)
    qtd = request.form.get("qtd", type=int)
    estoque_min = request.form.get("estoque_min", type=int)
    estoque_max = request.form.get("estoque_max", type=int)

    erros = []
    if not nome:
        erros.append("Informe o nome do produto.")
    if not sku:
        erros.append("Informe o código (SKU).")
    if not categoria:
        erros.append("Informe a categoria/tipo do produto.")
    if not rua_id:
        erros.append("Escolha a rua onde o produto será guardado.")
    if qtd is None or qtd < 0:
        erros.append("Informe uma quantidade inicial válida.")
    if estoque_min is None or estoque_max is None or estoque_min < 0 or estoque_max < 0:
        erros.append("Informe estoque mínimo e máximo válidos.")
    elif estoque_max < estoque_min:
        erros.append("O estoque máximo não pode ser menor que o mínimo.")

    rua = None
    if rua_id and not erros:
        rua = db.execute("SELECT * FROM ruas WHERE id = ?", (rua_id,)).fetchone()
        if not rua:
            erros.append("Rua inválida.")
        elif rua["tipo"] and rua["tipo"] != categoria:
            erros.append(
                f'A rua "{rua["nome"]}" já é usada para produtos do tipo '
                f'"{rua["tipo"]}". Não é possível guardar "{categoria}" nela.'
            )

    if not erros:
        sku_existe = db.execute("SELECT 1 FROM produtos WHERE sku = ?", (sku,)).fetchone()
        if sku_existe:
            erros.append("Já existe um produto com esse SKU.")

    if erros:
        for e in erros:
            flash(e, "danger")
        return redirect(url_for("produtos"))

    cur = db.execute(
        "INSERT INTO produtos (nome, sku, categoria, estoque_min, estoque_max) VALUES (?, ?, ?, ?, ?)",
        (nome, sku, categoria, estoque_min, estoque_max),
    )
    produto_id = cur.lastrowid

    if rua["tipo"] is None:
        db.execute("UPDATE ruas SET tipo = ? WHERE id = ?", (categoria, rua_id))

    db.execute(
        "INSERT INTO estoque (produto_id, rua_id, quantidade) VALUES (?, ?, ?)",
        (produto_id, rua_id, qtd),
    )

    db.execute("""
        INSERT INTO entradas (produto_id, rua_id, quantidade, tipo, usuario_id)
        VALUES (?, ?, ?, 'novo_produto', ?)
    """, (produto_id, rua_id, qtd, session.get("usuario_id", 1)))

    db.commit()
    flash(f'Produto "{nome}" cadastrado em "{rua["nome"]}".', "success")
    return redirect(url_for("produtos"))


@front_bp.route("/produtos/<int:produto_id>/editar", methods=["POST"], endpoint="editar_produto")
@admin_required
def editar_produto(produto_id):
    db = get_db()
    produto = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    if not produto:
        flash("Produto não encontrado.", "danger")
        return redirect(url_for("produtos"))

    nome = request.form.get("nome", "").strip()
    estoque_min = request.form.get("estoque_min", type=int)
    estoque_max = request.form.get("estoque_max", type=int)

    erros = []
    if not nome:
        erros.append("Informe o nome do produto.")
    if estoque_min is None or estoque_max is None or estoque_min < 0 or estoque_max < 0:
        erros.append("Informe estoque mínimo e máximo válidos.")
    elif estoque_max < estoque_min:
        erros.append("O estoque máximo não pode ser menor que o mínimo.")

    if erros:
        for e in erros:
            flash(e, "danger")
        return redirect(request.referrer or url_for("produtos"))

    db.execute(
        "UPDATE produtos SET nome = ?, estoque_min = ?, estoque_max = ? WHERE id = ?",
        (nome, estoque_min, estoque_max, produto_id),
    )
    db.commit()
    flash(f'Produto "{nome}" atualizado.', "success")
    return redirect(request.referrer or url_for("produtos"))


@front_bp.route("/produtos/<int:produto_id>/excluir", methods=["POST"], endpoint="excluir_produto")
@admin_required
def excluir_produto(produto_id):
    db = get_db()
    db.execute("DELETE FROM movimentacoes WHERE produto_id = ?", (produto_id,))
    db.execute("DELETE FROM saidas WHERE produto_id = ?", (produto_id,))
    db.execute("DELETE FROM entradas WHERE produto_id = ?", (produto_id,))
    db.execute("DELETE FROM estoque WHERE produto_id = ?", (produto_id,))
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()
    flash("Produto excluído.", "success")
    return redirect(url_for("produtos"))


# --------------------------------------------------------------------------
# Movimentações
# --------------------------------------------------------------------------

@front_bp.route("/movimentacoes", endpoint="movimentacoes")
@login_required
def movimentacoes():
    db = get_db()
    produtos_lista = db.execute("SELECT * FROM produtos ORDER BY nome").fetchall()

    historico = db.execute("""
        SELECT m.*, p.nome AS produto_nome, p.sku,
               ro.nome AS rua_origem_nome, rd.nome AS rua_destino_nome,
               u.usuario AS usuario_nome
        FROM movimentacoes m
        JOIN produtos p ON p.id = m.produto_id
        LEFT JOIN ruas ro ON ro.id = m.rua_origem_id
        LEFT JOIN ruas rd ON rd.id = m.rua_destino_id
        LEFT JOIN usuarios u ON u.id = m.usuario_id
        ORDER BY m.data DESC, m.id DESC
        LIMIT 200
    """).fetchall()

    return render_template("movimentacoes.html", produtos=produtos_lista, historico=historico)


@front_bp.route("/api/produtos/<int:produto_id>/estoque", endpoint="api_estoque_produto")
@login_required
def api_estoque_produto(produto_id):
    db = get_db()
    produto = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    if not produto:
        return jsonify({"erro": "produto não encontrado"}), 404

    locais = db.execute("""
        SELECT r.id AS rua_id, r.nome AS rua_nome, e.quantidade
        FROM estoque e JOIN ruas r ON r.id = e.rua_id
        WHERE e.produto_id = ? AND e.quantidade > 0
        ORDER BY r.nome
    """, (produto_id,)).fetchall()

    ruas_destino = db.execute("""
        SELECT id, nome, tipo FROM ruas
        WHERE tipo IS NULL OR tipo = ?
        ORDER BY nome
    """, (produto["categoria"],)).fetchall()

    return jsonify({
        "categoria": produto["categoria"],
        "locais_origem": [dict(l) for l in locais],
        "ruas_destino": [dict(r) for r in ruas_destino],
    })


@front_bp.route("/movimentacoes/nova", methods=["POST"], endpoint="nova_movimentacao")
@login_required
def nova_movimentacao():
    db = get_db()

    produto_id = request.form.get("produto_id", type=int)
    rua_origem_id = request.form.get("rua_origem_id", type=int)
    rua_destino_id = request.form.get("rua_destino_id", type=int)
    quantidade = request.form.get("quantidade", type=int)

    produto = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    if not produto:
        flash("Produto inválido.", "danger")
        return redirect(url_for("movimentacoes"))

    if rua_origem_id == rua_destino_id:
        flash("A rua de origem e destino não podem ser a mesma.", "danger")
        return redirect(url_for("movimentacoes"))

    origem = db.execute("SELECT * FROM estoque WHERE produto_id = ? AND rua_id = ?",
                         (produto_id, rua_origem_id)).fetchone()
    if not origem or not quantidade or quantidade <= 0:
        flash("Quantidade inválida ou produto não encontrado na rua de origem.", "danger")
        return redirect(url_for("movimentacoes"))

    if quantidade > origem["quantidade"]:
        flash(f'Só há {origem["quantidade"]} unidade(s) disponível(is) nessa rua de origem.', "danger")
        return redirect(url_for("movimentacoes"))

    destino_rua = db.execute("SELECT * FROM ruas WHERE id = ?", (rua_destino_id,)).fetchone()
    if not destino_rua:
        flash("Rua de destino inválida.", "danger")
        return redirect(url_for("movimentacoes"))

    if destino_rua["tipo"] and destino_rua["tipo"] != produto["categoria"]:
        flash(
            f'Não é possível mover "{produto["nome"]}" ({produto["categoria"]}) para '
            f'"{destino_rua["nome"]}", que já guarda produtos do tipo "{destino_rua["tipo"]}".',
            "danger",
        )
        return redirect(url_for("movimentacoes"))

    if destino_rua["tipo"] is None:
        db.execute("UPDATE ruas SET tipo = ? WHERE id = ?", (produto["categoria"], rua_destino_id))

    nova_qtd_origem = origem["quantidade"] - quantidade
    if nova_qtd_origem == 0:
        db.execute("DELETE FROM estoque WHERE id = ?", (origem["id"],))
    else:
        db.execute("UPDATE estoque SET quantidade = ? WHERE id = ?", (nova_qtd_origem, origem["id"]))

    destino_estoque = db.execute("SELECT * FROM estoque WHERE produto_id = ? AND rua_id = ?",
                                  (produto_id, rua_destino_id)).fetchone()
    if destino_estoque:
        db.execute("UPDATE estoque SET quantidade = quantidade + ? WHERE id = ?",
                   (quantidade, destino_estoque["id"]))
    else:
        db.execute("INSERT INTO estoque (produto_id, rua_id, quantidade) VALUES (?, ?, ?)",
                   (produto_id, rua_destino_id, quantidade))

    ainda_tem_estoque = db.execute(
        "SELECT COALESCE(SUM(quantidade), 0) AS n FROM estoque WHERE rua_id = ?", (rua_origem_id,)
    ).fetchone()["n"]
    if ainda_tem_estoque == 0:
        db.execute("UPDATE ruas SET tipo = NULL WHERE id = ?", (rua_origem_id,))

    db.execute("""
        INSERT INTO movimentacoes (produto_id, rua_origem_id, rua_destino_id, quantidade, tipo, usuario_id)
        VALUES (?, ?, ?, ?, 'transferencia', ?)
    """, (produto_id, rua_origem_id, rua_destino_id, quantidade, session.get("usuario_id", 1)))

    db.commit()
    flash(f'{quantidade} unidade(s) de "{produto["nome"]}" movida(s) com sucesso.', "success")
    return redirect(url_for("movimentacoes"))


# --------------------------------------------------------------------------
# Entradas
# --------------------------------------------------------------------------

@front_bp.route("/entradas", endpoint="entradas")
@login_required
def entradas():
    db = get_db()
    produtos_lista = db.execute("SELECT * FROM produtos ORDER BY nome").fetchall()

    historico = db.execute("""
        SELECT e.*, p.nome AS produto_nome, p.sku,
               r.nome AS rua_nome, u.usuario AS usuario_nome
        FROM entradas e
        JOIN produtos p ON p.id = e.produto_id
        JOIN ruas r ON r.id = e.rua_id
        LEFT JOIN usuarios u ON u.id = e.usuario_id
        ORDER BY e.data DESC, e.id DESC
        LIMIT 200
    """).fetchall()

    return render_template("entradas.html", produtos=produtos_lista, historico=historico)


@front_bp.route("/entradas/nova", methods=["POST"], endpoint="nova_entrada")
@login_required
def nova_entrada():
    db = get_db()

    produto_id = request.form.get("produto_id", type=int)
    rua_id = request.form.get("rua_id", type=int)
    quantidade = request.form.get("quantidade", type=int)

    produto = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    if not produto:
        flash("Produto inválido.", "danger")
        return redirect(url_for("entradas"))

    if not quantidade or quantidade <= 0:
        flash("Informe uma quantidade válida.", "danger")
        return redirect(url_for("entradas"))

    rua = db.execute("SELECT * FROM ruas WHERE id = ?", (rua_id,)).fetchone()
    if not rua:
        flash("Rua inválida.", "danger")
        return redirect(url_for("entradas"))

    if rua["tipo"] and rua["tipo"] != produto["categoria"]:
        flash(
            f'Não é possível guardar "{produto["nome"]}" ({produto["categoria"]}) em '
            f'"{rua["nome"]}", que já guarda produtos do tipo "{rua["tipo"]}".',
            "danger",
        )
        return redirect(url_for("entradas"))

    if rua["tipo"] is None:
        db.execute("UPDATE ruas SET tipo = ? WHERE id = ?", (produto["categoria"], rua_id))

    existente = db.execute("SELECT * FROM estoque WHERE produto_id = ? AND rua_id = ?",
                            (produto_id, rua_id)).fetchone()
    if existente:
        db.execute("UPDATE estoque SET quantidade = quantidade + ? WHERE id = ?",
                   (quantidade, existente["id"]))
    else:
        db.execute("INSERT INTO estoque (produto_id, rua_id, quantidade) VALUES (?, ?, ?)",
                   (produto_id, rua_id, quantidade))

    db.execute("""
        INSERT INTO entradas (produto_id, rua_id, quantidade, tipo, usuario_id)
        VALUES (?, ?, ?, 'reabastecimento', ?)
    """, (produto_id, rua_id, quantidade, session.get("usuario_id", 1)))

    db.commit()
    flash(f'Entrada de {quantidade} unidade(s) de "{produto["nome"]}" registrada em "{rua["nome"]}".', "success")
    return redirect(url_for("entradas"))


# --------------------------------------------------------------------------
# Saídas
# --------------------------------------------------------------------------

@front_bp.route("/saidas", endpoint="saidas")
@login_required
def saidas():
    db = get_db()
    produtos_lista = db.execute("SELECT * FROM produtos ORDER BY nome").fetchall()

    historico = db.execute("""
        SELECT s.*, p.nome AS produto_nome, p.sku,
               r.nome AS rua_nome, u.usuario AS usuario_nome
        FROM saidas s
        JOIN produtos p ON p.id = s.produto_id
        JOIN ruas r ON r.id = s.rua_id
        LEFT JOIN usuarios u ON u.id = s.usuario_id
        ORDER BY s.data DESC, s.id DESC
        LIMIT 200
    """).fetchall()

    return render_template("saidas.html", produtos=produtos_lista, historico=historico)


@front_bp.route("/saidas/nova", methods=["POST"], endpoint="nova_saida")
@login_required
def nova_saida():
    db = get_db()

    produto_id = request.form.get("produto_id", type=int)
    rua_id = request.form.get("rua_id", type=int)
    quantidade = request.form.get("quantidade", type=int)
    motivo = request.form.get("motivo", "").strip()

    produto = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    if not produto:
        flash("Produto inválido.", "danger")
        return redirect(url_for("saidas"))

    origem = db.execute("SELECT * FROM estoque WHERE produto_id = ? AND rua_id = ?",
                         (produto_id, rua_id)).fetchone()
    if not origem or not quantidade or quantidade <= 0:
        flash("Quantidade inválida ou produto não encontrado nessa rua.", "danger")
        return redirect(url_for("saidas"))

    if quantidade > origem["quantidade"]:
        flash(f'Só há {origem["quantidade"]} unidade(s) disponível(is) nessa rua.', "danger")
        return redirect(url_for("saidas"))

    nova_qtd = origem["quantidade"] - quantidade
    if nova_qtd == 0:
        db.execute("DELETE FROM estoque WHERE id = ?", (origem["id"],))
    else:
        db.execute("UPDATE estoque SET quantidade = ? WHERE id = ?", (nova_qtd, origem["id"]))

    ainda_tem_estoque = db.execute(
        "SELECT COALESCE(SUM(quantidade), 0) AS n FROM estoque WHERE rua_id = ?", (rua_id,)
    ).fetchone()["n"]
    if ainda_tem_estoque == 0:
        db.execute("UPDATE ruas SET tipo = NULL WHERE id = ?", (rua_id,))

    db.execute("""
        INSERT INTO saidas (produto_id, rua_id, quantidade, motivo, usuario_id)
        VALUES (?, ?, ?, ?, ?)
    """, (produto_id, rua_id, quantidade, motivo or None, session.get("usuario_id", 1)))

    db.commit()
    flash(f'Saída de {quantidade} unidade(s) de "{produto["nome"]}" registrada.', "success")
    return redirect(url_for("saidas"))
