import os
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, session, flash, jsonify, g, Response
)
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import database
from app.models.produto import Produto
from app.repositories.produto_repository import ProdutoRepository

logger = logging.getLogger("techstock.controller")

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
            elif senha_hash and senha_hash == senha:
                # Migra senha em texto plano legado para hash forte
                valida = True
                novo_hash = generate_password_hash(senha)
                db.execute("UPDATE usuarios SET senha_hash = ?, senha = NULL WHERE id = ?", (novo_hash, r["id"]))
                db.commit()
                logger.info(f"Senha do usuário '{usuario}' migrada com sucesso para hash.")

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
        return render_template("login.html", form=request.form)

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
    repo = ProdutoRepository(db)
    saldos = repo.obter_saldos_detalhados()

    total_produtos = len(saldos)
    categorias = sorted(list({s["produto"].categoria or "Geral" for s in saldos}))
    total_categorias = len(categorias)
    criticos = sum(1 for s in saldos if s["status"] == "CRITICO")
    atencao = sum(1 for s in saldos if s["status"] == "ATENCAO")
    data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")

    # Serializa todos os produtos para injeção JSON direta no HTML gerado
    produtos_json = json.dumps([
        {
            "id": s["produto"].id,
            "nome": s["produto"].nome,
            "sku": s["produto"].sku,
            "categoria": s["produto"].categoria or "Geral",
            "qtd": s["qtd_total"],
            "min": s["produto"].estoque_min,
            "max": s["produto"].estoque_max,
            "status": s["status"],
            "preco": s["produto"].preco_formatado,
        }
        for s in saldos
    ], ensure_ascii=False)

    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TechStock — Relatório Offline de Estoque</title>
    <style>
        :root {{
            --bg: #0B1120;
            --surface: #1E293B;
            --border: #334155;
            --text: #F8FAFC;
            --text-muted: #94A3B8;
            --primary: #0284C7;
            --primary-light: #38BDF8;
            --success: #10B981;
            --warning: #F59E0B;
            --danger: #EF4444;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #F1F5F9;
            color: #0F172A;
            padding: 24px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            background: #FFFFFF;
            padding: 24px 28px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
            margin-bottom: 24px;
        }}
        .brand h1 {{ font-size: 1.5rem; color: #0284C7; display: flex; align-items: center; gap: 8px; }}
        .brand p {{ color: #64748B; font-size: 0.9rem; margin-top: 4px; }}
        .badge-offline {{
            background: #ECFDF5;
            color: #059669;
            border: 1px solid #A7F3D0;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: #FFFFFF;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border-left: 4px solid var(--primary);
        }}
        .kpi-card.danger {{ border-left-color: var(--danger); }}
        .kpi-card.warning {{ border-left-color: var(--warning); }}
        .kpi-card.success {{ border-left-color: var(--success); }}
        .kpi-title {{ font-size: 0.85rem; color: #64748B; font-weight: 600; text-transform: uppercase; }}
        .kpi-value {{ font-size: 2rem; font-weight: 700; color: #0F172A; margin-top: 4px; }}
        .controls {{
            background: #FFFFFF;
            padding: 18px 24px;
            border-radius: 12px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            display: flex;
            gap: 16px;
            flex-wrap: wrap;
            align-items: center;
        }}
        .search-box {{ flex: 1; min-width: 250px; }}
        input, select {{
            width: 100%;
            padding: 10px 14px;
            border: 1px solid #CBD5E1;
            border-radius: 8px;
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s;
        }}
        input:focus, select:focus {{ border-color: var(--primary); }}
        .btn {{
            padding: 10px 18px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            border: none;
            background: #0284C7;
            color: #FFFFFF;
            transition: opacity 0.2s;
        }}
        .btn:hover {{ opacity: 0.9; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: #FFFFFF;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }}
        th, td {{ padding: 14px 18px; text-align: left; font-size: 0.95rem; }}
        th {{ background: #F8FAFC; color: #475569; font-weight: 600; border-bottom: 1px solid #E2E8F0; }}
        tr:not(:last-child) td {{ border-bottom: 1px solid #F1F5F9; }}
        tr:hover {{ background: #F8FAFC; }}
        .badge {{
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 700;
            display: inline-block;
        }}
        .badge-critico {{ background: #FEE2E2; color: #DC2626; }}
        .badge-atencao {{ background: #FEF3C7; color: #D97706; }}
        .badge-ok {{ background: #DCFCE7; color: #16A34A; }}
        .tag {{ background: #F1F5F9; padding: 4px 8px; border-radius: 6px; font-size: 0.85rem; color: #475569; }}
        .footer-info {{
            margin-top: 16px;
            display: flex;
            justify-content: space-between;
            color: #64748B;
            font-size: 0.85rem;
        }}
        @media print {{
            body {{ background: #FFFFFF; padding: 0; }}
            .controls, .badge-offline {{ display: none; }}
            table, header, .kpi-card {{ box-shadow: none; border: 1px solid #CBD5E1; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <h1>📦 TechStock — Relatório de Estoque</h1>
                <p>Relatório Standalone gerado em {data_geracao}</p>
            </div>
            <div class="badge-offline">
                ● 100% Offline (Standalone)
            </div>
        </header>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Total de Produtos</div>
                <div class="kpi-value">{total_produtos}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Categorias Ativas</div>
                <div class="kpi-value">{total_categorias}</div>
            </div>
            <div class="kpi-card warning">
                <div class="kpi-title">Estoque em Atenção</div>
                <div class="kpi-value">{atencao}</div>
            </div>
            <div class="kpi-card danger">
                <div class="kpi-title">Estoque Crítico</div>
                <div class="kpi-value">{criticos}</div>
            </div>
        </div>

        <div class="controls">
            <div class="search-box">
                <input type="text" id="busca" placeholder="🔍 Filtrar por nome do produto ou SKU..." aria-label="Pesquisar produto">
            </div>
            <div style="min-width: 180px;">
                <select id="filtroCategoria" aria-label="Filtrar por categoria">
                    <option value="">Todas as Categorias</option>
                    {''.join(f'<option value="{c}">{c}</option>' for c in categorias)}
                </select>
            </div>
            <div style="min-width: 160px;">
                <select id="filtroStatus" aria-label="Filtrar por status">
                    <option value="">Todos os Status</option>
                    <option value="CRITICO">Crítico</option>
                    <option value="ATENCAO">Atenção</option>
                    <option value="OK">Normal (OK)</option>
                </select>
            </div>
            <button class="btn" onclick="window.print()">🖨️ Imprimir / Salvar PDF</button>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Produto</th>
                    <th>SKU</th>
                    <th>Categoria</th>
                    <th>Qtd. Atual</th>
                    <th>Mín / Máx</th>
                    <th>Preço Un.</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="tabelaCorpo"></tbody>
        </table>

        <div class="footer-info">
            <span id="contadorItens">Carregando itens...</span>
            <span>TechStock WMS — Gestão Inteligente de Estoque</span>
        </div>
    </div>

    <script>
        // Dados embutidos diretamente no HTML pelo Flask para independência total de servidor
        const PRODUTOS = {produtos_json};

        function renderizar() {{
            const termo = document.getElementById("busca").value.toLowerCase().trim();
            const cat = document.getElementById("filtroCategoria").value;
            const status = document.getElementById("filtroStatus").value;

            const filtrados = PRODUTOS.filter(p => {{
                const matchTermo = !termo || p.nome.toLowerCase().includes(termo) || p.sku.toLowerCase().includes(termo);
                const matchCat = !cat || p.categoria === cat;
                const matchStatus = !status || p.status === status;
                return matchTermo && matchCat && matchStatus;
            }});

            const tbody = document.getElementById("tabelaCorpo");
            if (filtrados.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 32px; color: #64748B;">Nenhum produto atende aos filtros selecionados.</td></tr>';
            }} else {{
                tbody.innerHTML = filtrados.map(p => `
                    <tr>
                        <td><strong>${{p.nome}}</strong></td>
                        <td><code>${{p.sku}}</code></td>
                        <td><span class="tag">${{p.categoria}}</span></td>
                        <td><strong>${{p.qtd}}</strong></td>
                        <td>${{p.min}} / ${{p.max}}</td>
                        <td>${{p.preco}}</td>
                        <td><span class="badge badge-${{p.status.toLowerCase()}}">${{p.status}}</span></td>
                    </tr>
                `).join("");
            }}

            document.getElementById("contadorItens").innerText = `Exibindo ${{filtrados.length}} de ${{PRODUTOS.length}} produtos cadastrados`;
        }}

        document.getElementById("busca").addEventListener("input", renderizar);
        document.getElementById("filtroCategoria").addEventListener("change", renderizar);
        document.getElementById("filtroStatus").addEventListener("change", renderizar);

        // Inicialização imediata
        renderizar();
    </script>
</body>
</html>"""

    response = Response(html, mimetype="text/html")
    response.headers["Content-Disposition"] = "attachment; filename=relatorio_techstock.html"
    return response


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
    session["rascunho_concluido"] = "rua"
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

    categorias = db.execute("SELECT * FROM categorias ORDER BY nome").fetchall()
    uso_rows = db.execute("SELECT categoria, COUNT(*) AS n FROM produtos WHERE categoria IS NOT NULL GROUP BY categoria").fetchall()
    uso_categorias = {r["categoria"]: r["n"] for r in uso_rows}

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
        categorias=categorias,
        uso_categorias=uso_categorias,
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
    if categoria == "__nova__":
        categoria = request.form.get("nova_categoria", "").strip()
        if categoria:
            existe_cat = db.execute("SELECT 1 FROM categorias WHERE LOWER(nome) = LOWER(?)", (categoria,)).fetchone()
            if not existe_cat:
                db.execute("INSERT INTO categorias (nome) VALUES (?)", (categoria,))
                db.commit()

    rua_id_raw = request.form.get("rua_id", "").strip()
    if rua_id_raw == "__nova__":
        nova_rua = request.form.get("nova_rua", "").strip()
        if nova_rua:
            existe_rua = db.execute("SELECT id FROM ruas WHERE LOWER(nome) = LOWER(?)", (nova_rua,)).fetchone()
            if existe_rua:
                rua_id = existe_rua["id"]
            else:
                cur = db.execute("INSERT INTO ruas (nome, tipo) VALUES (?, ?)", (nova_rua, categoria or None))
                db.commit()
                rua_id = cur.lastrowid
        else:
            rua_id = None
    else:
        try:
            rua_id = int(rua_id_raw) if rua_id_raw else None
        except ValueError:
            rua_id = None

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

    prod = Produto(
        id=None,
        nome=nome,
        sku=sku,
        categoria=categoria,
        estoque_min=estoque_min if estoque_min is not None else 0,
        estoque_max=estoque_max if estoque_max is not None else 100,
    )
    try:
        prod.validar()
    except ValueError as val_err:
        erros.append(str(val_err))

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

    repo = ProdutoRepository(db)
    if not erros and repo.buscar_por_sku(sku):
        erros.append("Já existe um produto cadastrado com esse SKU.")

    if erros:
        for e in erros:
            flash(e, "danger")
        return redirect(url_for("produtos"))

    if rua["tipo"] is None:
        db.execute("UPDATE ruas SET tipo = ? WHERE id = ?", (categoria, rua_id))

    produto_id = repo.salvar(prod, rua_id=rua_id, qtd_inicial=qtd)
    session["rascunho_concluido"] = "produto"

    flash(f'Produto "{nome}" cadastrado com sucesso em "{rua["nome"]}".', "success")
    return redirect(url_for("produtos"))


@front_bp.route("/produtos/<int:produto_id>/editar", methods=["POST"], endpoint="editar_produto")
@admin_required
def editar_produto(produto_id):
    db = get_db()
    repo = ProdutoRepository(db)
    produto = repo.buscar_por_id(produto_id)
    if not produto:
        flash("Produto não encontrado.", "danger")
        return redirect(url_for("produtos"))

    nome = request.form.get("nome", "").strip()
    categoria = request.form.get("categoria", "").strip()
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

    if categoria:
        db.execute(
            "UPDATE produtos SET nome = ?, categoria = ?, estoque_min = ?, estoque_max = ?, atualizado_em = datetime('now') WHERE id = ?",
            (nome, categoria, estoque_min, estoque_max, produto_id),
        )
    else:
        db.execute(
            "UPDATE produtos SET nome = ?, estoque_min = ?, estoque_max = ?, atualizado_em = datetime('now') WHERE id = ?",
            (nome, estoque_min, estoque_max, produto_id),
        )
    db.commit()
    flash(f'Produto "{nome}" atualizado com sucesso.', "success")
    return redirect(request.referrer or url_for("produtos"))


@front_bp.route("/categorias/nova", methods=["POST"], endpoint="nova_categoria")
@admin_required
def nova_categoria():
    db = get_db()
    nome = request.form.get("nome", "").strip()
    if not nome:
        flash("Informe o nome da categoria.", "danger")
    else:
        existe = db.execute("SELECT 1 FROM categorias WHERE LOWER(nome) = LOWER(?)", (nome,)).fetchone()
        if existe:
            flash(f'A categoria "{nome}" já existe.', "warning")
        else:
            db.execute("INSERT INTO categorias (nome) VALUES (?)", (nome,))
            db.commit()
            session["rascunho_concluido"] = "categoria"
            flash(f'Categoria "{nome}" cadastrada com sucesso!', "success")
    return redirect(url_for("produtos"))


@front_bp.route("/categorias/<int:categoria_id>/excluir", methods=["POST"], endpoint="excluir_categoria")
@admin_required
def excluir_categoria(categoria_id):
    db = get_db()
    cat = db.execute("SELECT * FROM categorias WHERE id = ?", (categoria_id,)).fetchone()
    if cat:
        db.execute("DELETE FROM categorias WHERE id = ?", (categoria_id,))
        db.commit()
        flash(f'Categoria "{cat["nome"]}" excluída com sucesso.', "success")
    else:
        flash("Categoria não encontrada.", "danger")
    return redirect(url_for("produtos"))


@front_bp.route("/produtos/<int:produto_id>/excluir", methods=["POST"], endpoint="excluir_produto")
@admin_required
def excluir_produto(produto_id):
    db = get_db()
    repo = ProdutoRepository(db)
    db.execute("DELETE FROM movimentacoes WHERE produto_id = ?", (produto_id,))
    db.execute("DELETE FROM saidas WHERE produto_id = ?", (produto_id,))
    db.execute("DELETE FROM entradas WHERE produto_id = ?", (produto_id,))
    db.execute("DELETE FROM estoque WHERE produto_id = ?", (produto_id,))
    repo.excluir(produto_id)
    flash("Produto excluído com sucesso.", "success")
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
    session["rascunho_concluido"] = "movimentacao"
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
    session["rascunho_concluido"] = "entrada"
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
    session["rascunho_concluido"] = "saida"
    flash(f'Saída de {quantidade} unidade(s) de "{produto["nome"]}" registrada.', "success")
    return redirect(url_for("saidas"))
