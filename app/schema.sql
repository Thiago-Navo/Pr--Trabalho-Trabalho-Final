-- =============================================================
--  TechStock WMS — DDL COMPLETO (SQLite 3)
--  Chaves estrangeiras ativas (PRAGMA foreign_keys = ON)
-- =============================================================

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

-- 1. USUARIOS
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

-- 2. EMPRESAS
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

-- 3. FORNECEDORES
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

-- 4. CATEGORIAS
CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    descritivo TEXT
);

-- 5. RUAS
CREATE TABLE ruas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE NOT NULL,
    tipo TEXT,
    descricao TEXT,
    corredor TEXT,
    prateleira TEXT,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 6. DRIVES
CREATE TABLE drives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rua_id INTEGER NOT NULL,
    codigo TEXT UNIQUE NOT NULL,
    categoria_sugerida TEXT,
    ocupacao_pct INTEGER DEFAULT 0,
    FOREIGN KEY (rua_id) REFERENCES ruas (id) ON DELETE CASCADE
);

-- 7. ENDEREÇO DE ESTOQUE
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

-- 8. PRODUTOS
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

-- 9. ESTOQUE
CREATE TABLE estoque (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
    rua_id INTEGER NOT NULL REFERENCES ruas(id) ON DELETE CASCADE,
    quantidade INTEGER NOT NULL DEFAULT 0,
    UNIQUE (produto_id, rua_id)
);

-- 10. ESTOQUE LOCAL
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

-- 11. MOVIMENTO (LOG GERAL)
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

-- 12. MOVIMENTACOES (ENTRE RUAS)
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

-- 13. SAIDAS
CREATE TABLE saidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
    rua_id INTEGER NOT NULL REFERENCES ruas(id),
    quantidade INTEGER NOT NULL,
    motivo TEXT,
    usuario_id INTEGER REFERENCES usuarios(id),
    data TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 14. ENTRADAS
CREATE TABLE entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL REFERENCES produtos(id) ON DELETE CASCADE,
    rua_id INTEGER NOT NULL REFERENCES ruas(id),
    quantidade INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('novo_produto', 'reabastecimento')),
    usuario_id INTEGER REFERENCES usuarios(id),
    data TEXT NOT NULL DEFAULT (datetime('now'))
);
