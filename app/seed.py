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
    """Cria a estrutura de tabelas necessária para a aplicação."""
    cursor = conn.cursor()

    cursor.executescript(
        """
        DROP TABLE IF EXISTS movimentacoes;
        DROP TABLE IF EXISTS produtos;
        DROP TABLE IF EXISTS drives;
        DROP TABLE IF EXISTS ruas;
        DROP TABLE IF EXISTS categorias;
        DROP TABLE IF EXISTS fornecedores;
        DROP TABLE IF EXISTS empresas;
        DROP TABLE IF EXISTS usuarios;

        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT,
            senha_hash TEXT,
            cargo TEXT DEFAULT 'Operador'
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
            nome TEXT NOT NULL,
            descricao TEXT,
            corredor TEXT,
            prateleira TEXT
        );

        CREATE TABLE drives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rua_id INTEGER NOT NULL,
            codigo TEXT UNIQUE NOT NULL,
            categoria_sugerida TEXT,
            ocupacao_pct INTEGER DEFAULT 0,
            FOREIGN KEY (rua_id) REFERENCES ruas (id) ON DELETE CASCADE
        );

        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sku TEXT UNIQUE,
            preco INTEGER DEFAULT 0,
            categoria_id INTEGER,
            fornecedor_id INTEGER,
            drive_id INTEGER,
            quantidade INTEGER NOT NULL DEFAULT 0,
            quantidade_minima INTEGER NOT NULL DEFAULT 0,
            descricao TEXT,
            atualizado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoria_id) REFERENCES categorias (id),
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id),
            FOREIGN KEY (drive_id) REFERENCES drives (id)
        );

        CREATE TABLE movimentacoes (
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
    """
    )
    conn.commit()


def seed():
    conn = get_db()
    init_db(conn)
    cursor = conn.cursor()

    # 1. Usuários
    usuarios = [
        (
            "Pâmela Cristina",
            "pamela@techstock.com",
            generate_password_hash("admin123"),
            "Administradora",
        ),
        (
            "Thiago Rodrigues",
            "thiago@techstock.com",
            generate_password_hash("user123"),
            "Operador de Estoque",
        ),
        (
            "Mauricio Keiser",
            "mauricio@techstock.com",
            generate_password_hash("user123"),
            "Técnico de Suporte",
        ),
    ]
    cursor.executemany(
        "INSERT INTO usuarios (nome, email, senha_hash, cargo) VALUES (?, ?, ?, ?)",
        usuarios,
    )

    # 2. Categorias
    categorias = [
        ("Memória",),
        ("Armazenamento",),
        ("Placa-mãe",),
        ("Fonte",),
        ("Refrigeração",),
        ("Processador",),
    ]
    cursor.executemany("INSERT INTO categorias (nome) VALUES (?)", categorias)

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
            "AMD Semimodutores",
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

    # Mapeamento auxiliar de Categoria ID
    cursor.execute("SELECT id, nome FROM categorias")
    cat_map = {row["nome"]: row["id"] for row in cursor.fetchall()}

    # 3. Ruas e Drives
    ruas_data = [
        (
            "Rua 01",
            "Memórias e Processadores",
            [
                ("A1", "Memória RAM DDR4", 62),
                ("A2", "Memória RAM DDR5", 88),
                ("A3", "Processadores Intel", 20),
                ("A4", "Processadores AMD", 100),
                ("A5", "Vazio", 0),
                ("A6", "Coolers de CPU", 45),
                ("A7", "Pasta térmica", 70),
                ("A8", "Suportes e brackets", 92),
            ],
        ),
        (
            "Rua 02",
            "Armazenamento",
            [
                ("B1", "SSD SATA", 55),
                ("B2", "SSD NVMe", 30),
                ("B3", "HD 3.5\"", 12),
                ("B4", "HD 2.5\"", 95),
                ("B5", "Gabinetes externos", 40),
                ("B6", "Cabos SATA", 100),
                ("B7", "Adaptadores M.2", 8),
                ("B8", "Vazio", 0),
                ("B9", "Pendrives", 66),
                ("B10", "Cartões de memória", 77),
            ],
        ),
        (
            "Rua 03",
            "Placas-mãe",
            [
                ("C1", "Placas-mãe ATX", 48),
                ("C2", "Placas-mãe Micro-ATX", 60),
                ("C3", "Placas-mãe Mini-ITX", 90),
                ("C4", "Baterias CMOS", 25),
                ("C5", "Parafusos e espaçadores", 100),
                ("C6", "Cabos flat", 15),
                ("C7", "Vazio", 0),
            ],
        ),
        (
            "Rua 04",
            "Fontes e Coolers",
            [
                ("D1", "Fontes ATX 500W", 33),
                ("D2", "Fontes ATX 650W", 58),
                ("D3", "Fontes modulares", 80),
                ("D4", "Coolers a ar", 12),
                ("D5", "Water coolers", 47),
                ("D6", "Fitas e conectores", 100),
                ("D7", "Ventoinhas 120mm", 5),
                ("D8", "Vazio", 0),
                ("D9", "Cabos de força", 68),
            ],
        ),
    ]

    drive_map = {}
    for nome_rua, desc, drives in ruas_data:
        cursor.execute(
            "INSERT INTO ruas (nome, descricao) VALUES (?, ?)", (nome_rua, desc)
        )
        rua_id = cursor.lastrowid
        for codigo, cat_sugerida, ocupacao in drives:
            cursor.execute(
                "INSERT INTO drives (rua_id, codigo, categoria_sugerida, ocupacao_pct) VALUES (?, ?, ?, ?)",
                (rua_id, codigo, cat_sugerida, ocupacao),
            )
            drive_map[codigo] = cursor.lastrowid

    # 4. Produtos
    now = datetime.now()
    produtos = [
        (
            "Memória RAM 8GB DDR4 3200MHz",
            "SKU-0231",
            14990,
            cat_map["Memória"],
            drive_map["A1"],
            148,
            20,
            "Módulo de memória desktop DDR4 3200MHz",
            (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "SSD NVMe 512GB",
            "SKU-0119",
            22990,
            cat_map["Armazenamento"],
            drive_map["B2"],
            9,
            15,
            "SSD M.2 NVMe PCIe 3.0 leitura até 3000MB/s",
            (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "Fonte ATX 550W 80 Plus",
            "SKU-0087",
            28990,
            cat_map["Fonte"],
            drive_map["D1"],
            0,
            5,
            "Fonte PFC Ativo com certificação 80 Plus Bronze",
            (now - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "Placa-mãe B450M Gaming",
            "SKU-0054",
            45990,
            cat_map["Placa-mãe"],
            drive_map["C2"],
            31,
            10,
            "Socket AM4 suporte a Ryzen Séries 3000/4000/5000",
            (now - timedelta(days=1, hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "Cooler Master Hyper 212",
            "SKU-0176",
            17990,
            cat_map["Refrigeração"],
            drive_map["A6"],
            17,
            8,
            "Air cooler para CPU presilha multi-socket Intel/AMD",
            (now - timedelta(days=1, hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            "Processador Ryzen 5 5600",
            "SKU-0212",
            84990,
            cat_map["Processador"],
            drive_map["A4"],
            6,
            10,
            "6 Cores, 12 Threads, 3.5GHz (4.4GHz Turbo)",
            (now - timedelta(days=2, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
    ]

    cursor.executemany(
        """INSERT INTO produtos 
           (nome, sku, preco, categoria_id, drive_id, quantidade, quantidade_minima, descricao, atualizado_em) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        produtos,
    )

    # Mapeamentos para Movimentações
    cursor.execute("SELECT id, nome FROM usuarios")
    usr_map = {row["nome"]: row["id"] for row in cursor.fetchall()}

    cursor.execute("SELECT id, sku FROM produtos")
    prod_map = {row["sku"]: row["id"] for row in cursor.fetchall()}

    # 5. Movimentações
    movimentacoes = [
        (
            prod_map["SKU-0231"],
            usr_map["Thiago Rodrigues"],
            "ENTRADA",
            20,
            "Recebimento de lote via NF-10492",
            (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            prod_map["SKU-0119"],
            usr_map["Mauricio Keiser"],
            "SAIDA",
            4,
            "Atendimento de chamado técnico #402",
            (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            prod_map["SKU-0087"],
            usr_map["Pâmela Cristina"],
            "SAIDA",
            2,
            "Substituição de fontes queimadas setor comercial",
            (now - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            prod_map["SKU-0054"],
            usr_map["Thiago Rodrigues"],
            "ENTRADA",
            10,
            "Reposição de estoque fornecedor",
            (now - timedelta(days=1, hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            prod_map["SKU-0176"],
            usr_map["Mauricio Keiser"],
            "SAIDA",
            1,
            "Montagem de workstation laboratório",
            (now - timedelta(days=1, hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
        (
            prod_map["SKU-0212"],
            usr_map["Pâmela Cristina"],
            "ENTRADA",
            8,
            "Entrada via compra direta",
            (now - timedelta(days=2, hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
        ),
    ]

    cursor.executemany(
        """INSERT INTO movimentacoes 
           (produto_id, usuario_id, tipo, quantidade, observacao, criado_em) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        movimentacoes,
    )

    conn.commit()
    conn.close()
    print("Sucesso: Banco de dados inicializado e popularizado com dados do seed!")


if __name__ == "__main__":
    seed()
