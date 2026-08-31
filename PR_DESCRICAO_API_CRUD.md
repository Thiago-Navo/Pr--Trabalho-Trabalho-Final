# PR: Implementação e Ajustes da API REST (CRUD) — TechStock WMS

## 📋 Resumo do Pull Request

Esta branch (`feat/api-crud-mauricio`) organiza a camada de API do TechStock (`app/controllers/api_controller.py`) para fornecer operações CRUD e endpoints JSON para as telas do sistema.

---

## 🔄 Ajustes Já Realizados na Base

1. **Conexão com SQLite**:
   - Todas as rotas foram atualizadas para utilizar `db = database.get_connection()`.
2. **Configuração da Aplicação (`app/__init__.py`)**:
   - Removido `static_folder="css"` para restaurar o diretório padrão `app/static/`, mantendo os blueprints `front_bp` e `api_bp` registrados.
3. **Banco de Dados e `seed.py` Atualizados**:
   - Tabela `produtos`: Campo `preco` adicionado como **`INTEGER` (armazenamento padrão em centavos inteiros)**.
   - Tabela `usuarios`: Suporte a `senha` e `senha_hash`, com `cargo DEFAULT 'Operador'`.
   - Tabela `ruas`: Campos `corredor` e `prateleira` adicionados para flexibilidade de endereçamento.
   - Tabela `movimentacoes`: `usuario_id` com valor padrão para permitir registros diretos via API.

---

## 🚦 Status Atual dos Endpoints

### ✅ Endpoints Funcionais (Testados com Sucesso)
* **`GET /api/consulta-cep/<cep>`** — Consulta de endereço via ViaCEP.
* **`GET, POST, PUT, DELETE /api/fornecedores`** — CRUD completo com preenchimento automático de endereço via ViaCEP.
* **`GET, POST, PUT, DELETE /api/categorias`** — CRUD completo na tabela `categorias`.
* **`GET, POST, PUT, DELETE /api/produtos`** — CRUD completo na tabela `produtos` (com preço em centavos e fornecedor).
* **`GET, POST, PUT, DELETE /api/usuarios`** — Listagem e gestão de usuários.
* **`GET, POST /api/movimentacoes`** (e alias `/api/movimento`) — Consulta e registro de entradas e saídas de estoque.

### ⚠️ Endpoints com Ajustes Pendentes
* **`/api/enderecos-estoque`** ➔ Adequar queries para apontar para as tabelas **`ruas`** e **`drives`** (a tabela `endereco_estoque` não existe no SQLite).
* **`/api/estoque-local`** ➔ Mapear para o saldo físico direto de `produtos` alocados nos `drives`.
* **`/api/empresas`** ➔ Tabela redundante com `fornecedores` — o CRUD oficial ativo para parceiros/lotes é **/api/fornecedores**.

---

## 🚨 Requisitos Obrigatórios e Pendências Críticas

### 1. Criptografia de Senhas (`RN10`) — *Requisito Obrigatório de Entrega*
> **IMPORTANTE:** O armazenamento de senhas em texto plano **viola o requisito obrigatório de segurança (`RN10`)** estipulado na documentação do projeto.  
> No cadastro e atualização de usuários (`POST` e `PUT /api/usuarios`), a senha deve ser obrigatoriamente criptografada com `werkzeug.security.generate_password_hash` antes de salvar em `senha_hash`.

### 2. Endpoint de Estoque Dinâmico para o Front-End (PR 6)
> O Front-End (telas de Entradas, Saídas e Transferências) depende da rota:
> **`GET /api/produtos/<int:id>/estoque`**
> Deve retornar JSON contendo: `categoria`, `locais_origem` (ruas com saldo do produto) e `ruas_destino` (ruas compatíveis/livres conforme `RN02`).

### 3. Remoção de `conn.close()` Manual
> A classe `Database` gerencia a abertura e fechamento da conexão automaticamente pelo ciclo da requisição Flask (`g.db`). Chamar `conn.close()` manualmente dentro das rotas pode gerar erros em requisições subsequentes.

---

## 🧪 Como Testar

```bash
# 1. Recriar o banco com os dados iniciais do seed
python app/seed.py

# 2. Iniciar o servidor
python run.py

# 3. Testar endpoints via curl:
curl -X GET http://localhost:5000/api/produtos
curl -X GET http://localhost:5000/api/categorias
curl -X GET http://localhost:5000/api/consulta-cep/01001000
```
