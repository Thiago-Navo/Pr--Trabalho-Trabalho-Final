-- =============================================================
--  WMS — DDL COMPLETO
--  Ordem de criação respeita dependências (FK)
--  Banco: PostgreSQL 15+  (adapte SERIAL → AUTO_INCREMENT para MySQL)
-- =============================================================

-- -------------------------------------------------------------
-- 1. USUARIO
-- -------------------------------------------------------------
CREATE TABLE usuario (
    id               SERIAL        PRIMARY KEY,
    nome             VARCHAR(120)  NOT NULL,
    email            VARCHAR(120)  NOT NULL UNIQUE,
    celular          VARCHAR(20),
    cargo            VARCHAR(80),
    poder            SMALLINT      NOT NULL DEFAULT 1,  -- 1=operador 2=supervisor 3=admin
    senha_hash       VARCHAR(255)  NOT NULL,
    criado_em        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    atualizado_em    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    ativo            BOOLEAN       NOT NULL DEFAULT TRUE,
    deletado_em      TIMESTAMPTZ
);

-- -------------------------------------------------------------
-- 2. EMPRESA  (fabricante + fornecedor + endereço — flat)
-- -------------------------------------------------------------
CREATE TABLE empresa (
    id               SERIAL        PRIMARY KEY,
    tipo             VARCHAR(20)   NOT NULL CHECK (tipo IN ('fabricante','fornecedor','ambos')),
    cnpj             VARCHAR(18)   UNIQUE,
    razao_social     VARCHAR(160)  NOT NULL,
    nome_fantasia    VARCHAR(160),
    tel_fixo         VARCHAR(20),
    tel_celular      VARCHAR(20),
    email            VARCHAR(120),
    -- endereço flat (data-warehouse style)
    cep              VARCHAR(9),
    estado           CHAR(2),
    cidade           VARCHAR(80),
    logradouro       VARCHAR(160),
    numero           VARCHAR(10),
    complemento      VARCHAR(80),
    -- campos específicos de fabricante (nullable para fornecedor)
    nacionalidade    VARCHAR(60),
    site_fabric      VARCHAR(200),
    -- responsável (útil para fornecedor)
    usuario_id       INT           REFERENCES usuario(id) ON DELETE SET NULL,
    ativo_online     BOOLEAN       NOT NULL DEFAULT TRUE,
    dt_cadastro      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    dt_atualizado    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    dt_deletado      TIMESTAMPTZ
);

-- -------------------------------------------------------------
-- 3. CATEGORIA
-- -------------------------------------------------------------
CREATE TABLE categoria (
    id               SERIAL        PRIMARY KEY,
    nome             VARCHAR(80)   NOT NULL,
    subcategoria     VARCHAR(80),
    descritivo       TEXT,
    ativo            BOOLEAN       NOT NULL DEFAULT TRUE
);

-- -------------------------------------------------------------
-- 4. PRODUTO
-- -------------------------------------------------------------
CREATE TABLE produto (
    id               SERIAL        PRIMARY KEY,
    nome             VARCHAR(160)  NOT NULL,
    descricao        TEXT,
    altura           NUMERIC(8,2),
    largura          NUMERIC(8,2),
    peso             NUMERIC(8,3),
    cor_predominante VARCHAR(40),
    qtd_min          INT           NOT NULL DEFAULT 0,
    qtd_max          INT,
    marca            VARCHAR(80),
    modelo           VARCHAR(80),
    categoria_id     INT           REFERENCES categoria(id) ON DELETE SET NULL,
    fabricante_id    INT           REFERENCES empresa(id)   ON DELETE SET NULL,
    fornecedor_id    INT           REFERENCES empresa(id)   ON DELETE SET NULL
);

-- -------------------------------------------------------------
-- 5. ENDERECO_ESTOQUE  (árvore via caminho materializado)
--    Hierarquia: corredor → modulo → nivel → vao
--    caminho = caminho_pai || '/' || id  (calculado após INSERT)
-- -------------------------------------------------------------
CREATE TABLE endereco_estoque (
    id               SERIAL        PRIMARY KEY,
    parent_id        INT           REFERENCES endereco_estoque(id) ON DELETE RESTRICT,
    nome             VARCHAR(80)   NOT NULL,
    tipo             VARCHAR(10)   NOT NULL CHECK (tipo IN ('corredor','modulo','nivel','vao')),
    -- caminho materializado, ex: "1", "1/3", "1/3/7", "1/3/7/12"
    -- preenchido via UPDATE logo após INSERT (veja função abaixo)
    caminho          VARCHAR(200)  NOT NULL DEFAULT '',
    em_uso           BOOLEAN       NOT NULL DEFAULT TRUE
);

-- Índice para buscas por subtree: WHERE caminho LIKE '1/3/%'
CREATE INDEX idx_ee_caminho ON endereco_estoque (caminho);
CREATE INDEX idx_ee_parent  ON endereco_estoque (parent_id);
CREATE INDEX idx_ee_tipo    ON endereco_estoque (tipo);

-- -------------------------------------------------------------
-- 6. ESTOQUE_LOCAL
--    Só deve apontar para endereços do tipo 'vao' (constraint via CHECK + trigger)
-- -------------------------------------------------------------
CREATE TABLE estoque_local (
    id                    SERIAL  PRIMARY KEY,
    produto_id            INT     NOT NULL REFERENCES produto(id)           ON DELETE RESTRICT,
    endereco_estoque_id   INT     NOT NULL REFERENCES endereco_estoque(id)  ON DELETE RESTRICT,
    quantidade            INT     NOT NULL DEFAULT 0 CHECK (quantidade >= 0),
    UNIQUE (produto_id, endereco_estoque_id)
);

CREATE INDEX idx_el_produto   ON estoque_local (produto_id);
CREATE INDEX idx_el_endereco  ON estoque_local (endereco_estoque_id);

-- -------------------------------------------------------------
-- 7. MOVIMENTO
-- -------------------------------------------------------------
CREATE TABLE movimento (
    id                    SERIAL        PRIMARY KEY,
    produto_id            INT           NOT NULL REFERENCES produto(id)          ON DELETE RESTRICT,
    quantidade            INT           NOT NULL CHECK (quantidade > 0),
    origem_id             INT           REFERENCES estoque_local(id)             ON DELETE SET NULL,
    destino_id            INT           REFERENCES estoque_local(id)             ON DELETE SET NULL,
    tipo_movimento        VARCHAR(20)   NOT NULL
                          CHECK (tipo_movimento IN ('entrada','saida','transferencia','ajuste')),
    usuario_id            INT           REFERENCES usuario(id)                   ON DELETE SET NULL,
    observacao            TEXT,
    criado_em             TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mov_produto  ON movimento (produto_id);
CREATE INDEX idx_mov_criado   ON movimento (criado_em DESC);

-- -------------------------------------------------------------
-- 8. LOG_ACESSO  (auditoria geral)
-- -------------------------------------------------------------
CREATE TABLE log_acesso (
    id               BIGSERIAL     PRIMARY KEY,
    usuario_id       INT           REFERENCES usuario(id) ON DELETE SET NULL,
    acao             VARCHAR(40)   NOT NULL,   -- ex: 'CREATE', 'UPDATE', 'DELETE', 'LOGIN'
    entidade         VARCHAR(60)   NOT NULL,   -- ex: 'produto', 'movimento'
    entidade_id      INT,
    dados_anteriores JSONB,
    dados_novos      JSONB,
    ip               VARCHAR(45),
    user_agent       VARCHAR(255),
    criado_em        TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_log_usuario  ON log_acesso (usuario_id);
CREATE INDEX idx_log_entidade ON log_acesso (entidade, entidade_id);
CREATE INDEX idx_log_criado   ON log_acesso (criado_em DESC);
