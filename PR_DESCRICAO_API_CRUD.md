# PR: Implementação do CRUD da API e Integração com Front-End

## 📋 Descrição do Pull Request

Esta branch (`feat/api-crud-mauricio`) organiza a camada de API do TechStock (`app/controllers/api_controller.py`) para fornecer operações CRUD e endpoints JSON para as telas do sistema.

---

## 🛠️ O que esta PR deve implementar / corrigir

1. **Correção de Conexão com SQLite**:
   - Utilizar `db = database.get_connection()` em todas as rotas (a classe `Database` não possui `get_db_connection`).
   - Evitar `conn.close()` manual (o ciclo de vida da conexão é gerenciado pelo Flask via `g.db`).

2. **Compatibilidade com o Banco Oficial (`seed.py`)**:
   - `usuarios`: Utilizar `senha_hash` com `generate_password_hash` (`RN10`).
   - `produtos`: Ajustar colunas para `id`, `nome`, `sku`, `categoria_id`, `drive_id`, `quantidade`, `quantidade_minima`, `descricao` (remover `preco`).
   - `categorias`: Operações na tabela `categorias` (`id`, `nome`).
   - `ruas` e `drives`: Operações nas tabelas de endereçamento físico do galpão.
   - `movimentacoes`: Registro de entradas e saídas na tabela `movimentacoes` (`id`, `produto_id`, `usuario_id`, `tipo`, `quantidade`, `observacao`).

3. **Endpoint Obrigatório para o Front-End (PR 6)**:
   - `GET /api/produtos/<int:id>/estoque`: Retorna JSON com:
     - `categoria`: Nome da categoria do produto.
     - `locais_origem`: Ruas e quantidades onde o produto tem saldo.
     - `ruas_destino`: Ruas compatíveis para reabastecimento ou transferência (`RN02`).

4. **Configuração da Aplicação (`app/__init__.py`)**:
   - O `__init__.py` já está configurado registrando `front_bp` e `api_bp`, utilizando o diretório padrão `app/static/`.

---

## 🧪 Como Testar

```bash
# 1. Popular o banco com os dados iniciais
python app/seed.py

# 2. Iniciar o servidor Flask
python run.py

# 3. Testar os endpoints via curl ou Postman:
curl -X GET http://localhost:5000/api/produtos
curl -X GET http://localhost:5000/api/produtos/1/estoque
curl -X GET http://localhost:5000/api/categorias
```

---

## 📖 Documentação de Referência
- Consulte o guia completo em `app/docs/guia_correcoes_api_mauricio.md`.
