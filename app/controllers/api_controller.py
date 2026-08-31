from flask import Blueprint, request, jsonify
import sqlite3
from app.database import database
from app.database.viacep import buscar_endereco_por_cep

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ==================================================
# 0. ROTA AUXILIAR - VIACEP
# ==================================================
@api_bp.route('/consulta-cep/<string:cep>', methods=['GET'])
def consulta_cep(cep):
    resultado = buscar_endereco_por_cep(cep)
    if "erro" in resultado:
        return jsonify(resultado), 400
    return jsonify(resultado), 200


# ==================================================
# 1. CRUD - EMPRESAS
# ==================================================
@api_bp.route('/empresas', methods=['GET'])
def listar_empresas():
    conn = database.get_connection()
    empresas = conn.execute('SELECT * FROM empresas').fetchall()
    conn.close()
    return jsonify([dict(row) for row in empresas]), 200

@api_bp.route('/empresas/<int:id>', methods=['GET'])
def obter_empresa(id):
    conn = database.get_connection()
    empresa = conn.execute('SELECT * FROM empresas WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not empresa:
        return jsonify({"erro": "Empresa não encontrada"}), 404
    return jsonify(dict(empresa)), 200

@api_bp.route('/empresas', methods=['POST'])
def criar_empresa():
    dados = request.get_json() or {}
    nome_fantasia = dados.get('nome_fantasia')
    cnpj = dados.get('cnpj')
    cep = dados.get('cep')

    if not nome_fantasia or not cnpj:
        return jsonify({"erro": "Campos 'nome_fantasia' e 'cnpj' são obrigatórios"}), 400

    endereco = {}
    if cep:
        endereco = buscar_endereco_por_cep(cep)
        if "erro" in endereco:
            return jsonify(endereco), 400

    conn = database.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO empresas (nome_fantasia, cnpj, cep, logradouro, bairro, cidade, uf)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            nome_fantasia, cnpj,
            endereco.get('cep', cep),
            endereco.get('logradouro'),
            endereco.get('bairro'),
            endereco.get('cidade'),
            endereco.get('uf')
        ))
        conn.commit()
        novo_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"erro": "CNPJ já cadastrado"}), 400
    finally:
        conn.close()

    return jsonify({"mensagem": "Empresa criada com sucesso", "id": novo_id}), 201

@api_bp.route('/empresas/<int:id>', methods=['PUT'])
def atualizar_empresa(id):
    dados = request.get_json() or {}
    conn = database.get_connection()
    empresa = conn.execute('SELECT * FROM empresas WHERE id = ?', (id,)).fetchone()

    if not empresa:
        conn.close()
        return jsonify({"erro": "Empresa não encontrada"}), 404

    cep = dados.get('cep', empresa['cep'])
    endereco = {}
    if cep and cep != empresa['cep']:
        endereco = buscar_endereco_por_cep(cep)
        if "erro" in endereco:
            conn.close()
            return jsonify(endereco), 400

    conn.execute('''
        UPDATE empresas
        SET nome_fantasia = ?, cnpj = ?, cep = ?, logradouro = ?, bairro = ?, cidade = ?, uf = ?
        WHERE id = ?
    ''', (
        dados.get('nome_fantasia', empresa['nome_fantasia']),
        dados.get('cnpj', empresa['cnpj']),
        endereco.get('cep', cep),
        endereco.get('logradouro', empresa['logradouro']),
        endereco.get('bairro', empresa['bairro']),
        endereco.get('cidade', empresa['cidade']),
        endereco.get('uf', empresa['uf']),
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Empresa atualizada com sucesso"}), 200

@api_bp.route('/empresas/<int:id>', methods=['DELETE'])
def deletar_empresa(id):
    conn = database.get_connection()
    res = conn.execute('DELETE FROM empresas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    if res.rowcount == 0:
        return jsonify({"erro": "Empresa não encontrada"}), 404
    return jsonify({"mensagem": "Empresa removida com sucesso"}), 200


# ==================================================
# 2. CRUD - FORNECEDORES
# ==================================================
@api_bp.route('/fornecedores', methods=['GET'])
def listar_fornecedores():
    conn = database.get_connection()
    fornecedores = conn.execute('SELECT * FROM fornecedores').fetchall()
    conn.close()
    return jsonify([dict(row) for row in fornecedores]), 200

@api_bp.route('/fornecedores/<int:id>', methods=['GET'])
def obter_fornecedor(id):
    conn = database.get_connection()
    fornecedor = conn.execute('SELECT * FROM fornecedores WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not fornecedor:
        return jsonify({"erro": "Fornecedor não encontrado"}), 404
    return jsonify(dict(fornecedor)), 200

@api_bp.route('/fornecedores', methods=['POST'])
def criar_fornecedor():
    dados = request.get_json() or {}
    nome = dados.get('nome')
    cpf_cnpj = dados.get('cpf_cnpj')
    telefone = dados.get('telefone')
    cep = dados.get('cep')

    if not nome or not cpf_cnpj:
        return jsonify({"erro": "Campos 'nome' e 'cpf_cnpj' são obrigatórios"}), 400

    endereco = {}
    if cep:
        endereco = buscar_endereco_por_cep(cep)
        if "erro" in endereco:
            return jsonify(endereco), 400

    conn = database.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO fornecedores (nome, cpf_cnpj, telefone, cep, logradouro, bairro, cidade, uf)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            nome, cpf_cnpj, telefone,
            endereco.get('cep', cep),
            endereco.get('logradouro'),
            endereco.get('bairro'),
            endereco.get('cidade'),
            endereco.get('uf')
        ))
        conn.commit()
        novo_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"erro": "CPF/CNPJ já cadastrado"}), 400
    finally:
        conn.close()

    return jsonify({"mensagem": "Fornecedor criado com sucesso", "id": novo_id}), 201

@api_bp.route('/fornecedores/<int:id>', methods=['PUT'])
def atualizar_fornecedor(id):
    dados = request.get_json() or {}
    conn = database.get_connection()
    fornecedor = conn.execute('SELECT * FROM fornecedores WHERE id = ?', (id,)).fetchone()

    if not fornecedor:
        conn.close()
        return jsonify({"erro": "Fornecedor não encontrado"}), 404

    cep = dados.get('cep', fornecedor['cep'])
    endereco = {}
    if cep and cep != fornecedor['cep']:
        endereco = buscar_endereco_por_cep(cep)
        if "erro" in endereco:
            conn.close()
            return jsonify(endereco), 400

    conn.execute('''
        UPDATE fornecedores
        SET nome = ?, cpf_cnpj = ?, telefone = ?, cep = ?, logradouro = ?, bairro = ?, cidade = ?, uf = ?
        WHERE id = ?
    ''', (
        dados.get('nome', fornecedor['nome']),
        dados.get('cpf_cnpj', fornecedor['cpf_cnpj']),
        dados.get('telefone', fornecedor['telefone']),
        endereco.get('cep', cep),
        endereco.get('logradouro', fornecedor['logradouro']),
        endereco.get('bairro', fornecedor['bairro']),
        endereco.get('cidade', fornecedor['cidade']),
        endereco.get('uf', fornecedor['uf']),
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Fornecedor atualizado com sucesso"}), 200

@api_bp.route('/fornecedores/<int:id>', methods=['DELETE'])
def deletar_fornecedor(id):
    conn = database.get_connection()
    res = conn.execute('DELETE FROM fornecedores WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    if res.rowcount == 0:
        return jsonify({"erro": "Fornecedor não encontrado"}), 404
    return jsonify({"mensagem": "Fornecedor removido com sucesso"}), 200


# ==================================================
# 3. CRUD - PRODUTOS
# ==================================================
@api_bp.route('/produtos', methods=['GET'])
def listar_produtos():
    conn = database.get_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()
    return jsonify([dict(row) for row in produtos]), 200

@api_bp.route('/produtos/<int:id>', methods=['GET'])
def obter_produto(id):
    conn = database.get_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify(dict(produto)), 200

@api_bp.route('/produtos', methods=['POST'])
def criar_produto():
    dados = request.get_json() or {}
    nome = dados.get('nome')
    preco = dados.get('preco', 0.0)
    quantidade = dados.get('quantidade', 0)
    categoria_id = dados.get('categoria_id')

    if not nome:
        return jsonify({"erro": "O campo 'nome' é obrigatório"}), 400

    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO produtos (nome, preco, quantidade, categoria_id)
        VALUES (?, ?, ?, ?)
    ''', (nome, preco, quantidade, categoria_id))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()

    return jsonify({"mensagem": "Produto criado com sucesso", "id": novo_id}), 201

@api_bp.route('/produtos/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    dados = request.get_json() or {}
    conn = database.get_connection()
    produto = conn.execute('SELECT * FROM produtos WHERE id = ?', (id,)).fetchone()

    if not produto:
        conn.close()
        return jsonify({"erro": "Produto não encontrado"}), 404

    conn.execute('''
        UPDATE produtos
        SET nome = ?, preco = ?, quantidade = ?, categoria_id = ?
        WHERE id = ?
    ''', (
        dados.get('nome', produto['nome']),
        dados.get('preco', produto['preco']),
        dados.get('quantidade', produto['quantidade']),
        dados.get('categoria_id', produto['categoria_id']),
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Produto atualizado com sucesso"}), 200

@api_bp.route('/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    conn = database.get_connection()
    res = conn.execute('DELETE FROM produtos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    if res.rowcount == 0:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify({"mensagem": "Produto removido com sucesso"}), 200


# ==================================================
# 4. CRUD - CATEGORIAS
# ==================================================
@api_bp.route('/categorias', methods=['GET'])
def listar_categorias():
    conn = database.get_connection()
    categorias = conn.execute('SELECT * FROM categorias').fetchall()
    conn.close()
    return jsonify([dict(row) for row in categorias]), 200

@api_bp.route('/categorias/<int:id>', methods=['GET'])
def obter_categoria(id):
    conn = database.get_connection()
    cat = conn.execute('SELECT * FROM categorias WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not cat:
        return jsonify({"erro": "Categoria não encontrada"}), 404
    return jsonify(dict(cat)), 200

@api_bp.route('/categorias', methods=['POST'])
def criar_categoria():
    dados = request.get_json() or {}
    nome = dados.get('nome')
    if not nome:
        return jsonify({"erro": "O campo 'nome' é obrigatório"}), 400

    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO categorias (nome) VALUES (?)', (nome,))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"mensagem": "Categoria criada com sucesso", "id": novo_id}), 201

@api_bp.route('/categorias/<int:id>', methods=['PUT'])
def atualizar_categoria(id):
    dados = request.get_json() or {}
    conn = database.get_connection()
    cat = conn.execute('SELECT * FROM categorias WHERE id = ?', (id,)).fetchone()
    if not cat:
        conn.close()
        return jsonify({"erro": "Categoria não encontrada"}), 404

    conn.execute('UPDATE categorias SET nome = ? WHERE id = ?', (dados.get('nome', cat['nome']), id))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Categoria atualizada com sucesso"}), 200

@api_bp.route('/categorias/<int:id>', methods=['DELETE'])
def deletar_categoria(id):
    conn = database.get_connection()
    res = conn.execute('DELETE FROM categorias WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    if res.rowcount == 0:
        return jsonify({"erro": "Categoria não encontrada"}), 404
    return jsonify({"mensagem": "Categoria removida com sucesso"}), 200


# ==================================================
# 5. CRUD - USUÁRIOS
# ==================================================
@api_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conn = database.get_connection()
    usuarios = conn.execute('SELECT id, nome, email, cargo FROM usuarios').fetchall()
    conn.close()
    return jsonify([dict(row) for row in usuarios]), 200

@api_bp.route('/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    conn = database.get_connection()
    usuario = conn.execute('SELECT id, nome, email, cargo FROM usuarios WHERE id = ?', (id,)).fetchone()
    conn.close()
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify(dict(usuario)), 200

@api_bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.get_json() or {}
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    cargo = dados.get('cargo', 'Operador')

    if not nome or not email or not senha:
        return jsonify({"erro": "Campos 'nome', 'email' e 'senha' são obrigatórios"}), 400

    conn = database.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha, cargo)
            VALUES (?, ?, ?, ?)
        ''', (nome, email, senha, cargo))
        conn.commit()
        novo_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"erro": "E-mail já cadastrado"}), 400
    finally:
        conn.close()

    return jsonify({"mensagem": "Usuário criado com sucesso", "id": novo_id}), 201

@api_bp.route('/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    dados = request.get_json() or {}
    conn = database.get_connection()
    usr = conn.execute('SELECT * FROM usuarios WHERE id = ?', (id,)).fetchone()
    if not usr:
        conn.close()
        return jsonify({"erro": "Usuário não encontrado"}), 404

    conn.execute('''
        UPDATE usuarios
        SET nome = ?, email = ?, senha = ?, cargo = ?
        WHERE id = ?
    ''', (
        dados.get('nome', usr['nome']),
        dados.get('email', usr['email']),
        dados.get('senha', usr['senha']),
        dados.get('cargo', usr['cargo']),
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensagem": "Usuário atualizado com sucesso"}), 200

@api_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    conn = database.get_connection()
    res = conn.execute('DELETE FROM usuarios WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    if res.rowcount == 0:
        return jsonify({"erro": "Usuário não encontrado"}), 404
    return jsonify({"mensagem": "Usuário removido com sucesso"}), 200


# ==================================================
# 6. CRUD - ENDEREÇO DE ESTOQUE
# ==================================================
@api_bp.route('/enderecos-estoque', methods=['GET'])
def listar_enderecos_estoque():
    conn = database.get_connection()
    enderecos = conn.execute('SELECT * FROM endereco_estoque').fetchall()
    conn.close()
    return jsonify([dict(row) for row in enderecos]), 200

@api_bp.route('/enderecos-estoque', methods=['POST'])
def criar_endereco_estoque():
    dados = request.get_json() or {}
    corredor = dados.get('corredor')
    prateleira = dados.get('prateleira')

    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO endereco_estoque (corredor, prateleira) VALUES (?, ?)', (corredor, prateleira))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"mensagem": "Endereço de estoque criado com sucesso", "id": novo_id}), 201

@api_bp.route('/enderecos-estoque/<int:id>', methods=['DELETE'])
def deletar_endereco_estoque(id):
    conn = database.get_connection()
    res = conn.execute('DELETE FROM endereco_estoque WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    if res.rowcount == 0:
        return jsonify({"erro": "Endereço não encontrado"}), 404
    return jsonify({"mensagem": "Endereço de estoque removido com sucesso"}), 200


# ==================================================
# 7. CRUD - ESTOQUE LOCAL
# ==================================================
@api_bp.route('/estoque-local', methods=['GET'])
def listar_estoque_local():
    conn = database.get_connection()
    estoque = conn.execute('SELECT * FROM estoque_local').fetchall()
    conn.close()
    return jsonify([dict(row) for row in estoque]), 200

@api_bp.route('/estoque-local', methods=['POST'])
def registrar_estoque_local():
    dados = request.get_json() or {}
    produto_id = dados.get('produto_id')
    empresa_id = dados.get('empresa_id')
    quantidade = dados.get('quantidade', 0)

    if not produto_id or not empresa_id:
        return jsonify({"erro": "Campos 'produto_id' e 'empresa_id' são obrigatórios"}), 400

    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO estoque_local (produto_id, empresa_id, quantidade)
        VALUES (?, ?, ?)
    ''', (produto_id, empresa_id, quantidade))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"mensagem": "Estoque local registrado com sucesso", "id": novo_id}), 201


# ==================================================
# 8. MOVIMENTO (HISTÓRICO / REGISTRO)
# ==================================================
@api_bp.route('/movimento', methods=['GET'])
def listar_movimento():
    conn = database.get_connection()
    movimento = conn.execute('SELECT * FROM movimento').fetchall()
    conn.close()
    return jsonify([dict(row) for row in movimento]), 200

@api_bp.route('/movimento', methods=['POST'])
def registrar_movimento():
    dados = request.get_json() or {}
    produto_id = dados.get('produto_id')
    tipo = dados.get('tipo')
    quantidade = dados.get('quantidade')

    if not produto_id or not tipo or not quantidade:
        return jsonify({"erro": "Campos 'produto_id', 'tipo' e 'quantidade' são obrigatórios"}), 400

    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO movimento (produto_id, tipo, quantidade)
        VALUES (?, ?, ?)
    ''', (produto_id, tipo, quantidade))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return jsonify({"mensagem": "Movimentação registrada com sucesso", "id": novo_id}), 201
