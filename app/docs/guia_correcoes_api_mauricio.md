# Guia de Correções da API CRUD — TechStock WMS

Este documento detalha o status atual, a estrutura oficial do banco de dados e os ajustes necessários na branch `feat/api-crud-mauricio` para garantir que a API fique 100% funcional, aderente aos requisitos de entrega e integrada ao Front-End (`PR 6`).

---

## 📌 Sumário dos Ajustes

1. **Ajustes Já Realizados na Base**
2. **Estrutura Canônica das Tabelas (`seed.py`)**
3. **Status Atual dos Endpoints (Testes Reais)**
4. **Requisitos de Entrega & Pendências Críticas**
5. **Checklist Final para Aprovação da PR**

---

## 1. Ajustes Já Realizados na Base

- **Conexão com SQLite**: As rotas foram atualizadas para utilizar `db = database.get_connection()`.
- **Remoção de `conn.close()`**: A conexão é gerenciada pelo ciclo de vida da requisição Flask (`g.db`), não devendo ser fechada manualmente nas rotas.
- **Factory do Flask (`app/__init__.py`)**: Removido o parâmetro `static_folder="css"`, restaurando o caminho padrão `app/static/`.
- **Banco de Dados Atualizado (`seed.py`)**:
  - `produtos.preco`: Adicionado como **`INTEGER` (armazenamento em centavos inteiros — ex: 14990 = R$ 149,90)**.
  - `usuarios.senha` e `usuarios.senha_hash`: Ambos os campos suportados no schema.
  - `ruas.corredor` e `ruas.prateleira`: Adicionados para compatibilidade de endereçamento.
  - `movimentacoes.usuario_id`: Configurado com valor padrão (`DEFAULT 1`) para permitir chamadas diretas via API.

---

## 2. Estrutura Canônica das Tabelas (`techstock.db` / `seed.py`)

O banco SQLite ativo possui as seguintes tabelas estruturadas (conforme o pré-projeto e schema oficial):

| Tabela | Colunas | Observações Importantes |
| :--- | :--- | :--- |
| `empresas` | `id`, `nome_fantasia`, `razao_social`, `cnpj`, `tipo`, `cep`, `logradouro`, `bairro`, `cidade`, `uf`, `criado_em` | **Fabricantes e parceiros**; integração com ViaCEP para busca de endereço. |
| `fornecedores` | `id`, `nome`, `cpf_cnpj`, `telefone`, `cep`, `logradouro`, `bairro`, `cidade`, `uf`, `criado_em` | **Fornecedores de lotes**; integração com ViaCEP para preenchimento de endereço. |
| `usuarios` | `id`, `nome`, `email`, `senha`, `senha_hash`, `cargo` | `cargo` padrão é `'Operador'`. |
| `categorias` | `id`, `nome`, `descritivo` | Categorias de peças (ex: Memória, Armazenamento). |
| `ruas` | `id`, `nome`, `descricao`, `corredor`, `prateleira` | Endereços físicos do galpão. |
| `drives` | `id`, `rua_id`, `codigo`, `categoria_sugerida`, `ocupacao_pct` | Posições nas ruas (`FOREIGN KEY (rua_id) REFERENCES ruas(id)`). |
| `produtos` | `id`, `nome`, `sku`, `preco`, `categoria_id`, `fornecedor_id`, `drive_id`, `quantidade`, `quantidade_minima`, `descricao`, `atualizado_em` | **`preco` é inteiro em centavos**; vinculado ao fornecedor/lote. |
| `movimentacoes` | `id`, `produto_id`, `usuario_id`, `fornecedor_id`, `tipo`, `quantidade`, `observacao`, `criado_em` | `tipo` é `'ENTRADA'` ou `'SAIDA'`. Quantidade sempre > 0 (`RN04`). |

---

## 3. Status Atual dos Endpoints

### ✅ 100% Funcionais (Status 200 / 201)
- `GET /api/consulta-cep/<cep>` — Consulta externa ViaCEP.
- `GET, POST, PUT, DELETE /api/empresas` — CRUD completo de empresas/fabricantes integrado ao ViaCEP.
- `GET, POST, PUT, DELETE /api/fornecedores` — CRUD completo de fornecedores integrado ao ViaCEP.
- `GET, POST, PUT, DELETE /api/categorias` — CRUD completo.
- `GET, POST, PUT, DELETE /api/produtos` — CRUD completo (suporta preço em centavos, fornecedor e quantidade).
- `GET, POST, PUT, DELETE /api/usuarios` — Gestão de colaboradores.
- `GET, POST /api/movimentacoes` (e `/api/movimento`) — Consulta e registro de entradas e saídas de estoque.

### ⚠️ Rotas que Precisam de Ajuste de Nomenclatura SQL
- **`/api/enderecos-estoque`**: Mapear as consultas para as tabelas oficiais **`ruas`** e **`drives`** (a tabela `endereco_estoque` não existe no SQLite).
- **`/api/estoque-local`**: O saldo físico no WMS fica diretamente em `produtos.quantidade` associado a `produtos.drive_id`.

---

## 4. Requisitos Obrigatórios & Pendências Críticas

### A. Criptografia de Senhas (`RN10`) — *Requisito Obrigatório do Projeto*
> **ATENÇÃO:** O armazenamento de senhas em texto plano **não é aceito na entrega do projeto** e viola a regra de negócio canônica `RN10`.  
> No cadastro e edição de usuários (`POST` e `PUT /api/usuarios`), utilize sempre `generate_password_hash` da biblioteca `werkzeug.security` para gerar o hash antes de persistir no banco.

Exemplo de uso:
```python
from werkzeug.security import generate_password_hash

senha_hash = generate_password_hash(dados.get('senha'))
# Gravar senha_hash na coluna usuarios.senha_hash
```

---

### B. Endpoint de Estoque para o Front-End (`RF17` / PR 6)
> As telas de **Entradas**, **Saídas** e **Transferências** do Front-End realizam requisições automáticas para:
> **`GET /api/produtos/<int:id>/estoque`**

O endpoint deve retornar um JSON com a seguinte estrutura:
```json
{
  "categoria": "Memória",
  "locais_origem": [
    { "rua_id": 1, "rua_nome": "Rua 01", "quantidade": 20 }
  ],
  "ruas_destino": [
    { "id": 1, "nome": "Rua 01", "tipo": "Memória" },
    { "id": 2, "nome": "Rua 02", "tipo": null }
  ]
}
```

---

## 5. Checklist Final para Aprovação da PR

- [x] Conexão com banco via `database.get_connection()`.
- [x] Configuração correta de pasta estática no `__init__.py`.
- [x] `seed.py` com preços em centavos e campos de compatibilidade.
- [ ] Senhas de usuários criptografadas com `generate_password_hash` (`RN10`).
- [ ] Endpoint `GET /api/produtos/<int:id>/estoque` implementado.
- [ ] Queries de movimentação apontando para `movimentacoes` (plural).
- [ ] Execução limpa do `python app/seed.py` e testes com `python run.py`.
