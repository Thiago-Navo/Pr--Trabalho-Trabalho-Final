import sqlite3
import sys
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Garante que a raiz do projeto esteja no sys.path ao rodar como script direto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import database  # Importa a instância centralizada

def get_db():
    conn = sqlite3.connect(database.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn):
    """Cria a estrutura de tabelas necessária para a aplicação e API."""
    cursor = conn.cursor()

    cursor.executescript(
        """
        DROP TABLE IF EXISTS estoque_local;
        DROP TABLE IF EXISTS endereco_estoque;
        DROP TABLE IF EXISTS movimento;
        DROP TABLE IF EXISTS movimentacoes;
        DROP TABLE IF EXISTS entradas;
        DROP TABLE IF EXISTS saidas;
        DROP TABLE IF EXISTS estoque;
        DROP TABLE IF EXISTS produtos;
        DROP TABLE IF EXISTS drives;
        DROP TABLE IF EXISTS ruas;
        DROP TABLE IF EXISTS categorias;
        DROP TABLE IF EXISTS fornecedores;
        DROP TABLE IF EXISTS empresas;
        DROP TABLE IF EXISTS usuarios;

        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT,
            senha_hash TEXT NOT NULL,
            papel TEXT DEFAULT 'operador',
            cargo TEXT DEFAULT 'Operador',
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_fantasia TEXT NOT NULL,
            razao_social TEXT,
            cnpj TEXT UNIQUE NOT NULL,
            tipo TEXT DEFAULT 'fabricante',
            cep TEXT,
            logradouro TEXT,
            bairro TEXT,
            cidade TEXT,
            uf TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf_cnpj TEXT UNIQUE NOT NULL,
            telefone TEXT,
            cep TEXT,
            logradouro TEXT,
            bairro TEXT,
            cidade TEXT,
            uf TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            descritivo TEXT
        );

        CREATE TABLE ruas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            tipo TEXT,
            descricao TEXT,
            corredor TEXT,
            prateleira TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE drives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rua_id INTEGER NOT NULL,
            codigo TEXT UNIQUE NOT NULL,
            categoria_sugerida TEXT,
            ocupacao_pct INTEGER DEFAULT 0,
            FOREIGN KEY (rua_id) REFERENCES ruas (id) ON DELETE CASCADE
        );

        CREATE TABLE endereco_estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            tipo TEXT DEFAULT 'vao',
            corredor TEXT,
            prateleira TEXT,
            parent_id INTEGER,
            caminho TEXT DEFAULT '',
            em_uso BOOLEAN DEFAULT 1
        );

        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sku TEXT UNIQUE NOT NULL,
            preco INTEGER DEFAULT 0,
            categoria TEXT,
            categoria_id INTEGER,
            fornecedor_id INTEGER,
            drive_id INTEGER,
            quantidade INTEGER NOT NULL DEFAULT 0,
            estoque_min INTEGER NOT NULL DEFAULT 0,
            estoque_max INTEGER NOT NULL DEFAULT 0,
            quantidade_minima INTEGER NOT NULL DEFAULT 0,
            descricao TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id),
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id),
            FOREIGN KEY (drive_id) REFERENCES drives (id)
        );

        CREATE TABLE estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
            rua_id INTEGER NOT NULL REFERENCES ruas(id) ON DELETE CASCADE,
            quantidade INTEGER NOT NULL DEFAULT 0,
            UNIQUE (produto_id, rua_id)
        );

        CREATE TABLE estoque_local (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            endereco_estoque_id INTEGER,
            empresa_id INTEGER,
            quantidade INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (produto_id) REFERENCES produtos (id),
            FOREIGN KEY (endereco_estoque_id) REFERENCES endereco_estoque (id),
            FOREIGN KEY (empresa_id) REFERENCES empresas (id)
        );

        CREATE TABLE movimento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            usuario_id INTEGER DEFAULT 1,
            fornecedor_id INTEGER,
            tipo TEXT CHECK(tipo IN ('ENTRADA', 'SAIDA')) NOT NULL,
            quantidade INTEGER NOT NULL,
            observacao TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (produto_id) REFERENCES produtos (id),
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id)
        );

        CREATE TABLE movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
            rua_origem_id INTEGER REFERENCES ruas(id),
            rua_destino_id INTEGER REFERENCES ruas(id),
            quantidade INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('cadastro', 'transferencia')),
            usuario_id INTEGER REFERENCES usuarios(id),
            data TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE saidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
            rua_id INTEGER NOT NULL REFERENCES ruas(id),
            quantidade INTEGER NOT NULL,
            motivo TEXT,
            usuario_id INTEGER REFERENCES usuarios(id),
            data TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE entradas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
            rua_id INTEGER NOT NULL REFERENCES ruas(id),
            quantidade INTEGER NOT NULL,
            tipo TEXT NOT NULL CHECK (tipo IN ('novo_produto', 'reabastecimento')),
            usuario_id INTEGER REFERENCES usuarios(id),
            data TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """
    )
    conn.commit()


def data_com_offset(dias_atras, hora=12, minuto=0):
    momento = datetime.now() - timedelta(days=dias_atras)
    momento = momento.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    return momento.strftime("%Y-%m-%d %H:%M:%S")


def seed():
    conn = get_db()
    init_db(conn)
    cursor = conn.cursor()

    # 1. Usuários
    usuarios = [
        (
            "admin",
            "Administrador Padrão",
            "admin@techstock.com",
            generate_password_hash("admin123"),
            "admin",
            "Administrador",
        ),
        (
            "pamela",
            "Pâmela Cristina",
            "pamela@techstock.com",
            generate_password_hash("admin123"),
            "admin",
            "Administradora",
        ),
        (
            "thiago",
            "Thiago Rodrigues",
            "thiago@techstock.com",
            generate_password_hash("user123"),
            "operador",
            "Operador de Estoque",
        ),
        (
            "mauricio",
            "Mauricio Keiser",
            "mauricio@techstock.com",
            generate_password_hash("user123"),
            "operador",
            "Técnico de Suporte",
        ),
    ]
    cursor.executemany(
        "INSERT INTO usuarios (usuario, nome, email, senha_hash, papel, cargo) VALUES (?, ?, ?, ?, ?, ?)",
        usuarios,
    )

    # 2. Categorias
    categorias = [
        ("Memória", "Módulos de memória RAM para servidores e desktops"),
        ("Armazenamento", "Dispositivos de armazenamento rápido SSD e HD"),
        ("Placa-mãe", "Placas-mãe e circuitos principais"),
        ("Energia", "Fontes de alimentação e nobreaks"),
        ("Refrigeração", "Coolers, fans e sistemas de water cooling"),
        ("Cabos", "Cabos de conexão, dados e energia"),
        ("Processador", "CPUs de alta performance"),
        ("Gabinete", "Chassis e gabinetes para montagem"),
    ]
    cursor.executemany("INSERT INTO categorias (nome, descritivo) VALUES (?, ?)", categorias)

    # 3. Empresas (Fabricantes / Fornecedores)
    empresas = [
        (
            "Kingston Technology",
            "Kingston Technology Brasil Ltda",
            "02.345.678/0001-11",
            "fabricante",
            "01001-000",
            "Praça da Sé",
            "Sé",
            "São Paulo",
            "SP",
        ),
        (
            "ASUS Brasil",
            "ASUS do Brasil Fabricação e Comércio",
            "05.123.456/0001-99",
            "fabricante",
            "13010-001",
            "Avenida Francisco Glicério",
            "Centro",
            "Campinas",
            "SP",
        ),
        (
            "AMD Semicondutores",
            "Advanced Micro Devices Brasil",
            "07.890.123/0001-44",
            "fabricante",
            "01310-100",
            "Avenida Paulista",
            "Bela Vista",
            "São Paulo",
            "SP",
        ),
    ]
    cursor.executemany(
        """INSERT INTO empresas (nome_fantasia, razao_social, cnpj, tipo, cep, logradouro, bairro, cidade, uf)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        empresas,
    )

    # 4. Fornecedores
    fornecedores = [
        (
            "Distribuidora Tech Brasil Ltda",
            "12.345.678/0001-90",
            "(11) 3456-7890",
            "01001-000",
            "Praça da Sé",
            "Sé",
            "São Paulo",
            "SP",
        ),
        (
            "Kingston Importadora & Distribuição",
            "98.765.432/0001-10",
            "(19) 3876-5432",
            "13010-001",
            "Avenida Francisco Glicério",
            "Centro",
            "Campinas",
            "SP",
        ),
        (
            "Pichau Informática Atacado",
            "45.678.901/0001-23",
            "(47) 3300-1122",
            "89201-000",
            "Rua das Palmeiras",
            "Centro",
            "Joinville",
            "SC",
        ),
    ]
    cursor.executemany(
        """INSERT INTO fornecedores (nome, cpf_cnpj, telefone, cep, logradouro, bairro, cidade, uf)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        fornecedores,
    )

    # 5. Ruas e Endereços Físicos
    ruas_data = [
        ("Rua A1", "Memória", "Corredor A - Vão 01", "A", "01"),
        ("Rua B2", "Armazenamento", "Corredor B - Vão 01", "B", "01"),
        ("Rua C3", "Energia", "Corredor C - Vão 01", "C", "01"),
        ("Rua D4", "Placa-mãe", "Corredor D - Vão 01", "D", "01"),
        ("Rua E5", "Refrigeração", "Corredor E - Vão 01", "E", "01"),
        ("Rua F6", "Cabos", "Corredor F - Vão 01", "F", "01"),
        ("Rua G7", "Processador", "Corredor G - Vão 01", "G", "01"),
        ("Rua H8", "Gabinete", "Corredor H - Vão 01", "H", "01"),
    ]

    rua_map = {}
    for nome_rua, tipo, desc, corr, prat in ruas_data:
        cursor.execute(
            "INSERT INTO ruas (nome, tipo, descricao, corredor, prateleira) VALUES (?, ?, ?, ?, ?)",
            (nome_rua, tipo, desc, corr, prat),
        )
        rua_map[nome_rua] = cursor.lastrowid

    # 6. Produtos
    cursor.execute("SELECT id, nome FROM categorias")
    cat_map = {row["nome"]: row["id"] for row in cursor.fetchall()}

    produtos_seed = [
        dict(nome="Memória RAM DDR4 8GB", sku="MEM-RAM-8G", categoria="Memória", preco=14990,
             minimo=10, maximo=60, rua="Rua A1", dia_cadastro=6, qtd_cadastro=50,
             reabastecimentos=[], saidas=[(2, 8)]),
        dict(nome="SSD NVMe 512GB", sku="SSD-NVME-512", categoria="Armazenamento", preco=22990,
             minimo=10, maximo=40, rua="Rua B2", dia_cadastro=5, qtd_cadastro=20,
             reabastecimentos=[], saidas=[(1, 12)]),
        dict(nome="Fonte 650W 80 Plus", sku="FONTE-650W", categoria="Energia", preco=28990,
             minimo=5, maximo=25, rua="Rua C3", dia_cadastro=5, qtd_cadastro=15,
             reabastecimentos=[(2, 5)], saidas=[(0, 1)]),
        dict(nome="Placa-mãe B450M", sku="PM-B450M", categoria="Placa-mãe", preco=45990,
             minimo=8, maximo=20, rua="Rua D4", dia_cadastro=4, qtd_cadastro=20,
             reabastecimentos=[], saidas=[(3, 9), (1, 8)]),
        dict(nome="Water Cooler 240mm", sku="WC-240", categoria="Refrigeração", preco=35990,
             minimo=5, maximo=15, rua="Rua E5", dia_cadastro=3, qtd_cadastro=12,
             reabastecimentos=[], saidas=[(1, 3)]),
        dict(nome="Cabo HDMI 2.0 1,5m", sku="CABO-HDMI-15", categoria="Cabos", preco=2990,
             minimo=15, maximo=50, rua="Rua F6", dia_cadastro=2, qtd_cadastro=40,
             reabastecimentos=[(1, 10)], saidas=[(0, 9)]),
        dict(nome="Processador Ryzen 5 5600", sku="CPU-R5-5600", categoria="Processador", preco=84990,
             minimo=5, maximo=15, rua="Rua G7", dia_cadastro=1, qtd_cadastro=15,
             reabastecimentos=[], saidas=[(2, 9)]),
        dict(nome="Gabinete Mid Tower ATX", sku="GAB-MID-ATX", categoria="Gabinete", preco=19990,
             minimo=5, maximo=15, rua="Rua H8", dia_cadastro=0, qtd_cadastro=10,
             reabastecimentos=[], saidas=[]),
    ]

    for p in produtos_seed:
        cat_id = cat_map.get(p["categoria"], 1)
        rua_id = rua_map[p["rua"]]
        cur = cursor.execute("""
            INSERT INTO produtos (nome, sku, preco, categoria, categoria_id, estoque_min, estoque_max, quantidade, quantidade_minima, criado_em, atualizado_em)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (p["nome"], p["sku"], p["preco"], p["categoria"], cat_id, p["minimo"], p["maximo"], p["qtd_cadastro"], p["minimo"],
              data_com_offset(p["dia_cadastro"], 8, 0), data_com_offset(p["dia_cadastro"], 8, 0)))
        produto_id = cur.lastrowid

        # Saldo inicial na tabela estoque
        cursor.execute("INSERT INTO estoque (produto_id, rua_id, quantidade) VALUES (?, ?, ?)",
                       (produto_id, rua_id, p["qtd_cadastro"]))

        # Entrada inicial
        cursor.execute("""
            INSERT INTO entradas (produto_id, rua_id, quantidade, tipo, usuario_id, data)
            VALUES (?, ?, ?, 'novo_produto', 1, ?)
        """, (produto_id, rua_id, p["qtd_cadastro"], data_com_offset(p["dia_cadastro"], 8, 0)))

        cursor.execute("""
            INSERT INTO movimento (produto_id, usuario_id, tipo, quantidade, observacao, criado_em)
            VALUES (?, 1, 'ENTRADA', ?, 'Cadastro inicial do produto', ?)
        """, (produto_id, p["qtd_cadastro"], data_com_offset(p["dia_cadastro"], 8, 0)))

        # Reabastecimentos
        for offset_dias, qtd in p["reabastecimentos"]:
            cursor.execute("UPDATE estoque SET quantidade = quantidade + ? WHERE produto_id = ? AND rua_id = ?",
                           (qtd, produto_id, rua_id))
            cursor.execute("""
                INSERT INTO entradas (produto_id, rua_id, quantidade, tipo, usuario_id, data)
                VALUES (?, ?, ?, 'reabastecimento', 1, ?)
            """, (produto_id, rua_id, qtd, data_com_offset(offset_dias, 10, 0)))
            cursor.execute("""
                INSERT INTO movimento (produto_id, usuario_id, tipo, quantidade, observacao, criado_em)
                VALUES (?, 1, 'ENTRADA', ?, 'Reabastecimento de estoque', ?)
            """, (produto_id, qtd, data_com_offset(offset_dias, 10, 0)))

        # Saídas
        for offset_dias, qtd in p["saidas"]:
            cursor.execute("UPDATE estoque SET quantidade = quantidade - ? WHERE produto_id = ? AND rua_id = ?",
                           (qtd, produto_id, rua_id))
            cursor.execute("""
                INSERT INTO saidas (produto_id, rua_id, quantidade, motivo, usuario_id, data)
                VALUES (?, ?, ?, 'Venda / Despacho balcão', 1, ?)
            """, (produto_id, rua_id, qtd, data_com_offset(offset_dias, 15, 0)))
            cursor.execute("""
                INSERT INTO movimento (produto_id, usuario_id, tipo, quantidade, observacao, criado_em)
                VALUES (?, 1, 'SAIDA', ?, 'Venda / Despacho balcão', ?)
            """, (produto_id, qtd, data_com_offset(offset_dias, 15, 0)))

        # Atualiza a coluna agregada produtos.quantidade
        saldo_atual = cursor.execute("SELECT COALESCE(SUM(quantidade), 0) AS total FROM estoque WHERE produto_id = ?", (produto_id,)).fetchone()["total"]
        cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (saldo_atual, produto_id))

    # 7. Endereço de Estoque & Estoque Local
    enderecos = [
        ("Corredor A - Vão 01", "vao", "A", "01", None, "A/01", 1),
        ("Corredor B - Vão 01", "vao", "B", "01", None, "B/01", 1),
        ("Corredor C - Vão 01", "vao", "C", "01", None, "C/01", 1),
        ("Corredor D - Vão 01", "vao", "D", "01", None, "D/01", 1),
    ]
    cursor.executemany(
        """INSERT INTO endereco_estoque (nome, tipo, corredor, prateleira, parent_id, caminho, em_uso)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        enderecos,
    )

    cursor.execute("SELECT id FROM empresas LIMIT 1")
    emp_row = cursor.fetchone()
    emp_id = emp_row["id"] if emp_row else 1

    for prod_id, end_id, qtd in [(1, 1, 42), (2, 2, 8), (3, 3, 19), (4, 4, 3)]:
        cursor.execute(
            "INSERT INTO estoque_local (produto_id, endereco_estoque_id, empresa_id, quantidade) VALUES (?, ?, ?, ?)",
            (prod_id, end_id, emp_id, qtd),
        )

    conn.commit()
    conn.close()
    print("Sucesso: Banco de dados techstock.db inicializado e popularizado com dados completos!")


if __name__ == "__main__":
    seed()
