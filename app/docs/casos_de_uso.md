# Casos de Uso do Sistema TechStock (WMS)

Este documento especifica todos os **Casos de Uso (Use Cases)** do **TechStock**, detalhando os fluxos principais, fluxos de exceção, regras de negócio e **critérios de aceite em formato BDD (Given-When-Then)** para guiar a implementação dos testes unitários e de integração (com `pytest` ou `unittest`).

---

## 👥 Atores do Sistema

| Ator | Descrição | Permissões Típicas |
| :--- | :--- | :--- |
| **Operador de Estoque** | Usuário operacional responsável pelo galpão | Consulta estoque, registra entradas, saídas e transferências |
| **Administrador / Supervisor** | Gestor responsável pelas configurações do sistema | Acesso total + cadastro de novos usuários, criação/exclusão de ruas e produtos |
| **Sistema / Backend** | Processamento automático de regras e validações | Atualização de saldos, disparo de alertas de estoque baixo, travas de categoria |

---

## 📑 Sumário dos Casos de Uso

- **Módulo 1: Autenticação & Usuários**
  - [UC01: Autenticar Usuário (Login)](#uc01-autenticar-usuário-login)
  - [UC02: Encerrar Sessão (Logout)](#uc02-encerrar-sessão-logout)
  - [UC03: Cadastrar Novo Usuário](#uc03-cadastrar-novo-usuário)
- **Módulo 2: Gestão de Ruas & Endereçamento**
  - [UC04: Cadastrar Nova Rua](#uc04-cadastrar-nova-rua)
  - [UC05: Listar Ruas e Ocupação](#uc05-listar-ruas-e-ocupação)
  - [UC06: Excluir Rua](#uc06-excluir-rua)
- **Módulo 3: Catálogo de Produtos**
  - [UC07: Cadastrar Produto com Trava de Rua](#uc07-cadastrar-produto-com-trava-de-rua)
  - [UC08: Pesquisar e Filtrar Produtos](#uc08-pesquisar-e-filtrar-produtos)
  - [UC09: Editar Produto (Estoque Mínimo e Máximo)](#uc09-editar-produto-estoque-mínimo-e-máximo)
  - [UC10: Excluir Produto](#uc10-excluir-produto)
- **Módulo 4: Movimentações de Estoque**
  - [UC11: Registrar Entrada de Mercadoria (Reabastecimento)](#uc11-registrar-entrada-de-mercadoria-reabastecimento)
  - [UC12: Registrar Saída de Mercadoria (Baixa de Estoque)](#uc12-registrar-saída-de-mercadoria-baixa-de-estoque)
  - [UC13: Transferir Produto entre Ruas/Drives](#uc13-transferir-produto-entre-ruasdrives)
  - [UC14: Consultar Histórico e Rastreabilidade de Movimentações](#uc14-consultar-histórico-e-rastreabilidade-de-movimentações)
- **Módulo 5: Dashboard & Relatórios**
  - [UC15: Visualizar KPIs e Itens em Nível Crítico](#uc15-visualizar-kpis-e-itens-em-nível-crítico)
  - [UC16: Consultar API de Estoque do Produto](#uc16-consultar-api-de-estoque-do-produto)

---

# Módulo 1: Autenticação & Usuários

---

### UC01: Autenticar Usuário (Login)

* **Objetivo:** Permitir que operadores e administradores acessem o sistema de forma segura.
* **Atores:** Operador de Estoque, Administrador.
* **Pré-condições:** Usuário previamente cadastrado na tabela `usuarios`.

#### Fluxo Principal (Caminho Feliz):
1. O usuário acessa a rota `/login`.
2. O sistema exibe o formulário de login (`login.html`).
3. O usuário preenche seu e-mail e senha e clica em "Entrar".
4. O backend busca o usuário pelo e-mail e valida a senha com `check_password_hash`.
5. O sistema grava a sessão do usuário no Flask (`session['usuario_id'] = user.id`).
6. O sistema exibe a mensagem de sucesso `"Login efetuado com sucesso!"` e redireciona para `/dashboard`.

#### Fluxos de Exceção:
* **1a. E-mail não encontrado ou senha incorreta:**
  - O sistema recarrega a página `/login` com a mensagem flash de erro `"E-mail ou senha inválidos."` (HTTP 401 ou 200 com flash danger).
* **1b. Usuário inativo:**
  - O sistema impede o login e exibe `"Usuário inativo. Contate o administrador."`.

#### Cenários de Teste (BDD):
```gherkin
Cenário: Login com credenciais válidas
  Dado que existe um usuário "pamela@techstock.com" com senha "admin123"
  Quando o usuário envia POST para "/login" com email "pamela@techstock.com" e senha "admin123"
  Então o status code deve ser 302 redirecionando para "/dashboard"
  E a sessão deve conter o id do usuário autenticado

Cenário: Tentativa de login com senha incorreta
  Dado que existe um usuário "pamela@techstock.com" com senha "admin123"
  Quando o usuário envia POST para "/login" com email "pamela@techstock.com" e senha "senha_errada"
  Então o status code deve ser 200 (ou 401)
  E a mensagem "E-mail ou senha inválidos" deve ser exibida
```

---

### UC02: Encerrar Sessão (Logout)

* **Objetivo:** Encerrar a sessão ativa do usuário e remover dados da memória.
* **Atores:** Qualquer usuário autenticado.
* **Pré-condições:** Usuário com sessão ativa no sistema.

#### Fluxo Principal:
1. O usuário clica no botão "Sair" na sidebar (`/logout`).
2. O backend limpa o dicionário `session.clear()`.
3. O sistema adiciona mensagem flash `"Sessão encerrada com sucesso."` e redireciona para `/login`.

---

### UC03: Cadastrar Novo Usuário

* **Objetivo:** Permitir a criação de novos operadores ou administradores.
* **Atores:** Administrador.
* **Pré-condições:** Usuário logado com papel `admin`.

#### Fluxo Principal:
1. O administrador acessa a tela `/cadastro`.
2. O sistema exibe o formulário com campos: Nome, E-mail, Cargo e Senha.
3. O administrador preenche os dados e submete via POST.
4. O backend gera o hash da senha (`generate_password_hash`) e persiste na tabela `usuarios`.
5. O sistema exibe mensagem de sucesso e redireciona para a listagem ou tela de login.

#### Fluxos de Exceção:
* **3a. E-mail já cadastrado:**
  - O sistema impede o INSERT e exibe `"Este e-mail já está em uso por outro colaborador."`.
* **3b. Senha com menos de 6 caracteres:**
  - O sistema rejeita o cadastro e solicita senha mais forte.

---

# Módulo 2: Gestão de Ruas & Endereçamento

---

### UC04: Cadastrar Nova Rua

* **Objetivo:** Criar um novo endereço físico no galpão para armazenar produtos.
* **Atores:** Administrador / Operador.
* **Regra de Negócio (RN01 - Trava de Categoria):** Uma rua nasce livre. Ao guardar o primeiro produto nela, a rua fica travada para a categoria daquele produto, impedindo a mistura de categorias incompatíveis (ex: não misturar Memórias com Fontes).

#### Fluxo Principal:
1. O usuário acessa `/ruas` e clica em "Nova rua".
2. O sistema abre o modal com campos: Nome da Rua (ex: "Rua 05") e Descrição/Finalidade.
3. O usuário preenche e confirma o formulário via POST `/ruas/nova`.
4. O backend executa o `INSERT INTO ruas (nome, descricao) VALUES (?, ?)`.
5. O sistema recarrega `/ruas` exibindo a nova rua na tabela.

#### Fluxos de Exceção:
* **4a. Nome da rua em branco ou duplicado:**
  - O sistema valida e retorna `"Nome da rua é obrigatório e deve ser único."`.

---

### UC05: Listar Ruas e Ocupação

* **Objetivo:** Exibir a lista de todas as ruas, a categoria travada nela, a quantidade de produtos distintos e o total de peças guardadas.
* **Atores:** Todos os usuários.
* **Fluxo Principal:**
  1. O usuário acessa `/ruas`.
  2. O backend consulta o banco agregando produtos por rua:
     - Nome da Rua
     - Categoria travada (ou `"Livre"` se vazia)
     - Total de produtos distintos
     - Soma de quantidades (`SUM(quantidade)`)
  3. O template `ruas.html` renderiza os dados na tabela.

---

### UC06: Excluir Rua

* **Objetivo:** Remover uma rua que não será mais utilizada no galpão.
* **Regra de Negócio (RN02 - Proteção de Exclusão):** Uma rua **NÃO** pode ser excluída se possuir produtos com saldo maior que zero armazenados nela.

#### Fluxo Principal:
1. O administrador clica no botão de lixeira ao lado de uma rua vazia.
2. O sistema exibe o modal de confirmação: *"Tem certeza que deseja excluir esta rua?"*.
3. O usuário confirma via POST `/ruas/<id>/excluir`.
4. O backend verifica se há produtos vinculados. Como a quantidade é zero, executa `DELETE FROM ruas WHERE id = ?`.
5. Mensagem de confirmação é exibida: `"Rua excluída com sucesso!"`.

#### Fluxo de Exceção:
* **6a. Rua possui produtos armazenados:**
  - O backend bloqueia a exclusão e exibe: `"Não é possível excluir esta rua pois ela contém produtos em estoque. Mova os produtos antes de excluir."`.

---

# Módulo 3: Catálogo de Produtos

---

### UC07: Cadastrar Produto com Trava de Rua

* **Objetivo:** Inserir um novo componente no catálogo e associá-lo a um endereço físico.
* **Regra de Negócio (RN03 - SKU Único):** Todo produto deve ter um código SKU exclusivo (ex: `SKU-0231`).
* **Regra de Negócio (RN04 - Compatibilidade de Rua):** Se a rua escolhida já possuir uma categoria travada diferente da categoria do produto, o sistema deve rejeitar o cadastro.

#### Fluxo Principal:
1. O usuário acessa `/produtos` e clica em "Novo produto".
2. O modal solicita:
   - Nome do Produto (ex: "Memória RAM 16GB DDR4")
   - SKU (ex: "SKU-0992")
   - Categoria (ex: "Memória")
   - Rua de Destino (ex: "Rua 01")
   - Estoque Mínimo (ex: 10) e Estoque Máximo (ex: 100)
3. O usuário envia o formulário POST para `/produtos/novo`.
4. O backend valida:
   - Unicidade do SKU
   - Compatibilidade da categoria com a rua escolhida
5. O backend executa o `INSERT INTO produtos` e comita a transação.
6. O sistema exibe flash `"Produto cadastrado com sucesso!"` e atualiza a listagem.

#### Fluxos de Exceção:
* **7a. SKU Duplicado:**
  - O sistema impede a gravação e notifica `"Já existe um produto com este SKU."`.
* **7b. Rua incompatível com a categoria:**
  - O sistema impede a gravação e notifica `"A Rua 01 está travada para a categoria Placa-mãe e não aceita produtos da categoria Memória."`.
* **7c. Estoque Mínimo maior que Estoque Máximo:**
  - O sistema valida: `"O estoque mínimo não pode ser superior ao estoque máximo."`.

#### Cenários de Teste (BDD):
```gherkin
Cenário: Cadastro de produto com sucesso
  Dado que existe a categoria "Memória" e a rua "Rua 01" está livre
  Quando o usuário envia POST para "/produtos/novo" com:
    | nome          | Memória RAM 16GB DDR4 |
    | sku           | SKU-0992              |
    | categoria_id  | 1                     |
    | rua_id        | 1                     |
    | estoque_min   | 10                    |
    | estoque_max   | 100                   |
  Então o produto deve ser gravado na tabela "produtos"
  E a rua "Rua 01" deve travar na categoria "Memória"

Cenário: Rejeição de SKU duplicado
  Dado que já existe um produto com SKU "SKU-0231"
  Quando o usuário tenta cadastrar outro produto com SKU "SKU-0231"
  Então o sistema não deve criar novo registro
  E deve retornar mensagem de erro sobre duplicidade
```

---

### UC08: Pesquisar e Filtrar Produtos

* **Objetivo:** Localizar rapidamente componentes pelo nome, código SKU ou categoria.
* **Fluxo Principal:**
  1. O usuário digita `"NVMe"` no campo de busca do topo ou da tela `/produtos?q=NVMe`.
  2. O backend executa query com `WHERE nome LIKE '%NVMe%' OR sku LIKE '%NVMe%' OR categoria LIKE '%NVMe%'`.
  3. A tabela exibe apenas os produtos correspondentes.
  4. Se a busca for limpa, todos os produtos voltam a ser exibidos.

---

### UC09: Editar Produto (Estoque Mínimo e Máximo)

* **Objetivo:** Alterar parâmetros de alerta de estoque de um componente existente.
* **Regra de Negócio (RN05 - Integridade de Tipo):** SKU e Categoria não podem ser alterados diretamente na edição rápida para não violar a trava física da rua.
* **Fluxo Principal:**
  1. O usuário clica no botão "Editar" de um produto na listagem.
  2. O modal abre preenchido com: Nome, Estoque Mínimo e Estoque Máximo.
  3. O usuário ajusta os valores e submete POST para `/produtos/<id>/editar`.
  4. O backend executa `UPDATE produtos SET nome = ?, estoque_min = ?, estoque_max = ? WHERE id = ?`.
  5. A lista é atualizada com a mensagem `"Produto #ID atualizado com sucesso!"`.

---

### UC10: Excluir Produto

* **Objetivo:** Remover produto obsoleto ou cadastrado por engano.
* **Regra de Negócio (RN06):** Produtos com histórico de movimentações vinculadas devem ser arquivados (`soft delete`) ou validados para não quebrar integridade referencial.

---

# Módulo 4: Movimentações de Estoque

---

### UC11: Registrar Entrada de Mercadoria (Reabastecimento)

* **Objetivo:** Dar entrada de novas unidades de um produto já cadastrado, somando ao saldo do galpão.
* **Atores:** Operador de Estoque, Administrador.

#### Fluxo Principal:
1. O usuário acessa a tela `/entradas`.
2. No painel "Nova entrada", seleciona:
   - Produto (ex: "Memória RAM 8GB DDR4")
   - Rua de Destino compatível
   - Quantidade recebida (ex: 20 unidades)
   - Observação / Nota Fiscal (ex: "NF 10492 - Lote Kingston")
3. O usuário clica em "Salvar entrada" (POST `/entradas/nova`).
4. O backend executa em uma transação única (`atomic transaction`):
   - `UPDATE produtos SET quantidade = quantidade + ? WHERE id = ?`
   - `INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade, observacao) VALUES (?, ?, 'ENTRADA', ?, ?)`
   - `db.commit()`
5. O sistema atualiza o saldo do produto e exibe a entrada no topo do histórico.

#### Fluxos de Exceção:
* **11a. Quantidade menor ou igual a zero:**
  - O sistema rejeita: `"A quantidade de entrada deve ser maior que zero."`.

#### Cenários de Teste (BDD):
```gherkin
Cenário: Entrada de estoque com soma correta de saldo
  Dado que o produto "SSD NVMe 512GB" possui saldo atual de 9 unidades
  Quando o operador registra uma ENTRADA de 15 unidades para este produto
  Então o saldo do produto no banco de dados deve ser 24 unidades
  E deve existir um registro em "movimentacoes" com tipo "ENTRADA" e quantidade 15
```

---

### UC12: Registrar Saída de Mercadoria (Baixa de Estoque)

* **Objetivo:** Dar baixa em peças do estoque por motivo de venda, chamado técnico, defeito ou uso interno.
* **Regra de Negócio (RN07 - Estoque Não-Negativo):** A quantidade de saída **NUNCA** pode ser maior do que o saldo atual disponível do produto no galpão.

#### Fluxo Principal:
1. O usuário acessa `/saidas`.
2. Seleciona o produto, a quantidade a retirar (ex: 4 unidades) e o motivo (ex: "Chamado técnico #402").
3. O usuário submete o formulário via POST `/saidas/nova`.
4. O backend verifica: `saldo_atual >= quantidade_solicitada`.
5. O backend executa na mesma transação:
   - `UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?`
   - `INSERT INTO movimentacoes (produto_id, usuario_id, tipo, quantidade, observacao) VALUES (?, ?, 'SAIDA', ?, ?)`
   - `db.commit()`
6. O sistema notifica `"Saída registrada com sucesso!"` e atualiza os saldos.

#### Fluxos de Exceção:
* **12a. Quantidade solicitada excede o saldo em estoque:**
  - O sistema impede a baixa e exibe mensagem de erro: `"Saldo insuficiente. Estoque atual: 2 unidades. Quantidade solicitada: 5 unidades."`.

#### Cenários de Teste (BDD):
```gherkin
Cenário: Tentativa de saída com saldo insuficiente
  Dado que o produto "Fonte ATX 550W" possui saldo atual de 0 unidades
  Quando o operador tenta registrar uma SAÍDA de 2 unidades
  Então a operação deve ser rejeitada
  E o saldo do produto deve permanecer 0 unidades
  E nenhuma movimentação de saída deve ser registrada
```

---

### UC13: Transferir Produto entre Ruas/Drives

* **Objetivo:** Mover caixas/itens de uma rua para outra dentro do galpão por reorganização física.
* **Regra de Negócio (RN08 - Validação da Rua de Destino):** A rua de destino deve ser da mesma categoria do produto ou estar livre.

---

### UC14: Consultar Histórico e Rastreabilidade de Movimentações

* **Objetivo:** Permitir auditoria completa de quem moveu, quando, qual produto, qual tipo (entrada/saída) e o motivo.
* **Fluxo Principal:**
  1. O usuário acessa `/movimentacoes`.
  2. O sistema lista a tabela ordenada cronologicamente (da mais recente para a mais antiga) contendo:
     - Data e Hora formatadas
     - Nome do Produto e SKU
     - Usuário responsável pela ação
     - Tipo (tag verde `ENTRADA` ou vermelha `SAÍDA`)
     - Quantidade movimentada
     - Observação / Motivo

---

# Módulo 5: Dashboard & Relatórios

---

### UC15: Visualizar KPIs e Itens em Nível Crítico

* **Objetivo:** Apresentar em tempo real a saúde geral do armazém e disparar alertas visuais para compras/reposição.
* **Atores:** Gerentes, Supervisores, Operadores.
* **Regra de Negócio (RN09 - Cálculo de Estoque Baixo):** Um produto entra em estado de **Atenção/Estoque Baixo** se `quantidade <= estoque_min`.

#### Fluxo Principal:
1. O usuário acessa `/dashboard` (ou a raiz `/`).
2. O backend calcula:
   - **Total de Produtos Cadastrados** (`SELECT COUNT(*) FROM produtos`)
   - **Total de Categorias** (`SELECT COUNT(*) FROM categorias`)
   - **Itens em Estoque Baixo** (`SELECT COUNT(*) FROM produtos WHERE quantidade <= quantidade_minima`)
   - **Total de Entradas dos últimos 7 dias** (`SUM(quantidade) WHERE tipo = 'ENTRADA' AND criado_em >= NOW - 7d`)
   - **Total de Saídas dos últimos 7 dias** (`SUM(quantidade) WHERE tipo = 'SAIDA' AND criado_em >= NOW - 7d`)
   - **Distribuição por Categoria** para o gráfico Doughnut.
   - **Lista de Produtos em Atenção** com barra de progresso visual.
3. O template `dashboard.html` renderiza os cards de KPI, gráficos Chart.js e a tabela de alerta.

---

### UC16: Consultar API de Estoque do Produto

* **Objetivo:** Endpoint JSON consumido pelo JavaScript da tela para preencher dinamicamente selects e travas de rua sem recarregar a página.
* **Rota:** `GET /api/produtos/<int:produto_id>/estoque`
* **Resposta Esperada (JSON 200):**
```json
{
  "categoria": "Memória",
  "locais_origem": [
    {
      "rua_id": 1,
      "rua_nome": "Rua 01 — Memórias",
      "quantidade": 148
    }
  ],
  "ruas_destino": [
    { "id": 1, "nome": "Rua 01", "tipo": "Memória" },
    { "id": 4, "nome": "Rua 04", "tipo": "" }
  ]
}
```
* **Resposta de Erro (JSON 404):**
```json
{
  "error": "Produto não encontrado"
}
```

---

## 🧪 Matriz de Rastreabilidade para Testes Futuros

| Caso de Uso | Tipo de Teste Recomendado | Arquivo de Teste Sugerido |
| :--- | :--- | :--- |
| **UC01 / UC02** | Teste de Integração (Sessão & Flash) | `tests/test_auth.py` |
| **UC04 / UC06** | Teste Unitário & Integração (CRUD Ruas + Foreign Keys) | `tests/test_ruas.py` |
| **UC07 / UC09 / UC10** | Teste Unitário (Validação de SKU, travas de categoria) | `tests/test_produtos.py` |
| **UC11 / UC12 / UC13** | Teste de Regra de Negócio (Saldos não-negativos, transações) | `tests/test_movimentacoes.py` |
| **UC15 / UC16** | Teste de Endpoint / API JSON (Status 200, JSON Schema) | `tests/test_dashboard_api.py` |

---

> **Documento versionado em:** `app/docs/casos_de_uso.md`  
> **TechStock WMS** — Engenharia de Software e Qualidade de Código.
