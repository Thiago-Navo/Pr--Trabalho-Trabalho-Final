# Guia de Correções da API CRUD — TechStock WMS

Este documento detalha os ajustes técnicos necessários na branch `feat/api-crud-mauricio` para que a API fique 100% aderente ao banco de dados SQLite oficial (`seed.py`), à arquitetura do projeto e à integração com o Front-End (`PR 6`).

---

## 📌 Sumário dos Ajustes Necessários

1. **Método de Conexão com o Banco**: Substituir `database.get_db_connection()` por `database.get_connection()`.
2. **Compatibilização de Tabelas e Colunas**: Adequar os comandos SQL às tabelas do `seed.py` e `schema.sql`.
3. **Endpoint Obrigatório para o Front-End**: Implementar `GET /api/produtos/<int:id>/estoque`.
4. **Segurança de Senhas (RN10)**: Usar `generate_password_hash` ao cadastrar/atualizar senhas em `usuarios`.
5. **Organização do ViaCEP**: Manter a lógica do ViaCEP em módulo de serviço ou utilitário.

---

## 1. Conexão com o Banco de Dados

A classe `Database` em `app/database/connection.py` disponibiliza o método `get_connection()` gerenciado pela requisição Flask (`g.db`).

### ❌ Como estava:
```python
conn = database.get_db_connection()  # ERRO: método inexistente
# ...
conn.close()  # Conexão é gerenciada pelo ciclo da requisição
```

### ✅ Como deve ser:
```python
db = database.get_connection()
cursor = db.execute("SELECT * FROM produtos")
produtos = cursor.fetchall()
# Não precisa de conn.close() manual em cada rota
```

---

## 2. Estrutura Canônica das Tabelas (conforme `seed.py` / `requisitos_e_regras_de_negocio.md`)

O banco SQLite ativo utiliza as seguintes tabelas e colunas:

| Tabela | Colunas Principais | Observações |
| :--- | :--- | :--- |
| `usuarios` | `id`, `nome`, `email`, `senha_hash`, `cargo` | A senha **nunca** é gravada em texto plano. Usar `werkzeug.security.generate_password_hash`. |
| `categorias` | `id`, `nome` | Nome da categoria (ex: "Memória", "Armazenamento", etc.). |
| `ruas` | `id`, `nome`, `descricao` | Corredores físicos do galpão. |
| `drives` | `id`, `rua_id`, `codigo`, `categoria_sugerida`, `ocupacao_pct` | Posições físicas vinculadas a uma rua (`FOREIGN KEY (rua_id) REFERENCES ruas(id)`). |
| `produtos` | `id`, `nome`, `sku`, `categoria_id`, `drive_id`, `quantidade`, `quantidade_minima`, `descricao`, `atualizado_em` | **Não existe coluna `preco`**. `sku` é único. |
| `movimentacoes` | `id`, `produto_id`, `usuario_id`, `tipo`, `quantidade`, `observacao`, `criado_em` | `tipo` é `'ENTRADA'` ou `'SAIDA'`. Quantidade sempre positiva (`RN04`). |

---

## 3. Endpoint Obrigatório para Integração com o Front-End

O Front-End (telas `entradas.html`, `saidas.html` e `movimentacoes.html`) consome a rota:

### `GET /api/produtos/<int:id>/estoque`

**Objetivo**: Retornar os dados da categoria do produto, as ruas/locais onde ele possui saldo e as ruas compatíveis para receber o item (ruas livres ou que já possuem produtos da mesma categoria - `RN02`).

**Exemplo de Implementação**:
```python
@api_bp.route('/produtos/<int:id>/estoque', methods=['GET'])
def obter_estoque_produto(id):
    db = database.get_connection()
    
    # 1. Busca produto e categoria
    produto = db.execute('''
        SELECT p.id, p.nome, c.nome AS categoria
        FROM produtos p
        JOIN categorias c ON p.categoria_id = c.id
        WHERE p.id = ?
    ''', (id,)).fetchone()
    
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
        
    categoria_nome = produto["categoria"]
    
    # 2. Locais de origem onde o produto tem estoque
    locais_origem = db.execute('''
        SELECT r.id AS rua_id, r.nome AS rua_nome, p.quantidade AS quantidade
        FROM produtos p
        LEFT JOIN drives d ON p.drive_id = d.id
        LEFT JOIN ruas r ON d.rua_id = r.id
        WHERE p.id = ? AND p.quantidade > 0
    ''', (id,)).fetchall()
    
    # 3. Ruas de destino compatíveis (livres ou com a mesma categoria)
    ruas_destino = db.execute('''
        SELECT DISTINCT r.id, r.nome, d.categoria_sugerida AS tipo
        FROM ruas r
        LEFT JOIN drives d ON d.rua_id = r.id
        WHERE d.categoria_sugerida = ? OR d.categoria_sugerida IS NULL OR d.categoria_sugerida = 'Vazio'
    ''', (categoria_nome,)).fetchall()
    
    return jsonify({
        "categoria": categoria_nome,
        "locais_origem": [dict(row) for row in locais_origem],
        "ruas_destino": [dict(row) for row in ruas_destino]
    }), 200
```

---

## 4. Cadastro de Usuários com Senha Criptografada (`RN10`)

No CRUD de usuários:
```python
from werkzeug.security import generate_password_hash

@api_bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.get_json() or {}
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    cargo = dados.get('cargo', 'Operador')

    if not nome or not email or not senha:
        return jsonify({"erro": "Campos 'nome', 'email' e 'senha' são obrigatórios"}), 400

    senha_hash = generate_password_hash(senha)
    db = database.get_connection()
    try:
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha_hash, cargo)
            VALUES (?, ?, ?, ?)
        ''', (nome, email, senha_hash, cargo))
        db.commit()
        novo_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        return jsonify({"erro": "E-mail já cadastrado"}), 400

    return jsonify({"mensagem": "Usuário criado com sucesso", "id": novo_id}), 201
```

---

## 5. Checklist de Entrega para a PR

- [ ] Todas as chamadas de banco utilizam `database.get_connection()`.
- [ ] O endpoint `GET /api/produtos/<int:id>/estoque` está respondendo o JSON com `categoria`, `locais_origem` e `ruas_destino`.
- [ ] As tabelas consultadas batem com `usuarios`, `categorias`, `ruas`, `drives`, `produtos`, `movimentacoes`.
- [ ] O `app/__init__.py` não possui `static_folder="css"`.
- [ ] Executar os testes locais com `python run.py`.
