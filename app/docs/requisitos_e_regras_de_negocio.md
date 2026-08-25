# Requisitos e Regras de Negócio — TechStock (WMS)

Este documento especifica formalmente os **Requisitos Funcionais (RF)**, as **Regras de Negócio (RN)** e os **Requisitos Não-Funcionais (RNF)** do sistema **TechStock**, servindo como especificação canônica para o desenvolvimento, testes e entrega acadêmica/técnica.

---

## 📑 Sumário

1. [Requisitos Funcionais (RF)](#1-requisitos-funcionais-rf)
   - [Módulo de Autenticação & Acesso](#11-módulo-de-autenticação--acesso)
   - [Módulo de Endereçamento (Ruas & Galpão)](#12-módulo-de-endereçamento-ruas--galpão)
   - [Módulo de Catálogo de Produtos](#13-módulo-de-catálogo-de-produtos)
   - [Módulo de Movimentações de Estoque](#14-módulo-de-movimentações-de-estoque)
   - [Módulo de Dashboard, Indicadores & Relatórios](#15-módulo-de-dashboard-indicadores--relatórios)
   - [Módulo de API JSON](#16-módulo-de-api-json)
2. [Regras de Negócio (RN)](#2-regras-de-negócio-rn)
3. [Requisitos Não-Funcionais (RNF)](#3-requisitos-não-funcionais-rnf)
4. [Matriz de Rastreabilidade (RF ⟷ RN ⟷ UC)](#4-matriz-de-rastreabilidade-rf--rn--uc)

---

## 1. Requisitos Funcionais (RF)

Legenda de Prioridade:
- **[Essencial]**: Fundamental para o funcionamento mínimo do sistema (MVP).
- **[Importante]**: Agrega alto valor operacional e integridade aos dados.
- **[Desejável]**: Recurso de melhoria de usabilidade ou pós-MVP.

---

### 1.1. Módulo de Autenticação & Acesso

#### `RF01` — Autenticação de Usuário (Login) `[Essencial]`
* **Descrição:** O sistema deve permitir que usuários cadastrados realizem login fornecendo e-mail e senha.
* **Entradas:** E-mail corporativo (`VARCHAR`) e Senha em texto plano (`VARCHAR`).
* **Saídas:** Sessão autenticada no Flask, mensagem flash de boas-vindas e redirecionamento para o Dashboard (ou mensagem de credenciais inválidas).

#### `RF02` — Encerramento de Sessão (Logout) `[Essencial]`
* **Descrição:** O sistema deve permitir ao usuário autenticado encerrar sua sessão de trabalho a qualquer momento.
* **Saídas:** Limpeza da sessão (`session.clear()`) e redirecionamento para a tela de login.

#### `RF03` — Cadastro e Gestão de Usuários `[Importante]`
* **Descrição:** O sistema deve permitir que usuários administradores cadastrem novos colaboradores (Nome, E-mail, Cargo e Senha).
* **Entradas:** Nome completo, e-mail único, cargo e senha.
* **Saídas:** Registro gravado na tabela `usuarios` com senha criptografada.

---

### 1.2. Módulo de Endereçamento (Ruas & Galpão)

#### `RF04` — Cadastro de Ruas de Estoque `[Essencial]`
* **Descrição:** O sistema deve permitir o cadastro de ruas (corredores físicos do galpão) com nome e descrição/finalidade.
* **Entradas:** Nome da Rua (ex: "Rua 01") e Descrição opcional.
* **Saídas:** Novo registro persistido na tabela `ruas`.

#### `RF05` — Visualização e Status de Ocupação de Ruas `[Essencial]`
* **Descrição:** O sistema deve listar todas as ruas cadastradas exibindo: nome da rua, categoria travada (ou se está livre), total de produtos distintos e quantidade total de peças armazenadas.
* **Saídas:** Tabela detalhada na tela `/ruas`.

#### `RF06` — Edição e Exclusão de Ruas `[Importante]`
* **Descrição:** O sistema deve permitir atualizar a descrição de uma rua e excluí-la caso ela não contenha produtos vinculados.
* **Entradas:** ID da rua e novos dados.

---

### 1.3. Módulo de Catálogo de Produtos

#### `RF07` — Cadastro de Novos Produtos `[Essencial]`
* **Descrição:** O sistema deve permitir o cadastro de novos componentes de informática vinculados a uma categoria e a uma rua compatível.
* **Entradas:** Nome do Produto, Código SKU único, Categoria (ID), Rua de Destino (ID), Estoque Mínimo, Estoque Máximo e Descrição técnica.
* **Saídas:** Registro persistido na tabela `produtos` e trava automática da categoria na rua escolhida.

#### `RF08` — Consulta e Pesquisa Rápida de Produtos `[Essencial]`
* **Descrição:** O sistema deve disponibilizar campo de busca para filtrar produtos em tempo real por nome, código SKU ou categoria.
* **Entradas:** Termo de busca via query parameter `?q=...`.
* **Saídas:** Listagem filtrada na tabela de produtos com barra de nível de estoque e tags de status.

#### `RF09` — Edição Rápida de Estoque Mínimo e Máximo `[Importante]`
* **Descrição:** O sistema deve permitir ao usuário alterar o nome, estoque mínimo de segurança e estoque máximo de um produto através de modal de edição rápida.
* **Entradas:** ID do produto, novo nome, novo estoque mínimo e novo estoque máximo.

#### `RF10` — Exclusão de Produtos `[Importante]`
* **Descrição:** O sistema deve permitir a exclusão de um produto do catálogo através de modal de confirmação.

---

### 1.4. Módulo de Movimentações de Estoque

#### `RF11` — Registro de Entrada de Mercadoria (Reabastecimento) `[Essencial]`
* **Descrição:** O sistema deve permitir registrar o recebimento de itens de um produto existente, somando a quantidade ao saldo em estoque e gravando o lote no histórico.
* **Entradas:** ID do produto, Rua de destino, Quantidade recebida (> 0), Observação/Nota Fiscal.
* **Saídas:** Saldo do produto atualizado (`quantidade = quantidade + ?`) e novo registro na tabela `movimentacoes` (tipo `ENTRADA`).

#### `RF12` — Registro de Saída de Mercadoria (Baixa de Estoque) `[Essencial]`
* **Descrição:** O sistema deve permitir registrar a baixa de itens por venda, atendimento de chamado técnico, defeito ou uso interno.
* **Entradas:** ID do produto, Quantidade retirada (> 0), Motivo/Observação da saída.
* **Saídas:** Saldo do produto reduzido (`quantidade = quantidade - ?`) e novo registro na tabela `movimentacoes` (tipo `SAIDA`).

#### `RF13` — Histórico e Rastreabilidade de Movimentações `[Essencial]`
* **Descrição:** O sistema deve exibir o registro cronológico de todas as movimentações realizadas no galpão com data/hora, produto, operador responsável, tipo e motivo.
* **Saídas:** Tabela em ordem decrescente na tela `/movimentacoes`.

---

### 1.5. Módulo de Dashboard, Indicadores & Relatórios

#### `RF14` — Painel de Indicadores Principais (KPIs) `[Essencial]`
* **Descrição:** O sistema deve calcular e exibir no Dashboard:
  - Total de produtos cadastrados;
  - Total de categorias ativas;
  - Quantidade de produtos em nível crítico (estoque baixo);
  - Total de itens recebidos (entradas) nos últimos 7 dias;
  - Total de itens despachados (saídas) nos últimos 7 dias.

#### `RF15` — Gráficos de Tendência e Distribuição `[Importante]`
* **Descrição:** O sistema deve gerar dois gráficos interativos no Dashboard:
  - **Gráfico de Linha/Área:** Comparativo de Entradas vs Saídas nos últimos 7 dias.
  - **Gráfico Doughnut:** Distribuição proporcional da quantidade de itens por categoria.

#### `RF16` — Tabela de Alerta de Estoque Crítico `[Essencial]`
* **Descrição:** O sistema deve destacar no Dashboard os produtos cujo saldo atual esteja igual ou inferior ao estoque mínimo definido, exibindo barra de nível e localização física.

---

### 1.6. Módulo de API JSON

#### `RF17` — Endpoint de Consulta Dinâmica de Estoque `[Importante]`
* **Descrição:** O sistema deve fornecer a rota `GET /api/produtos/<id>/estoque` retornando os dados da categoria do produto, ruas onde ele se encontra e ruas de destino compatíveis no formato JSON.

---

## 2. Regras de Negócio (RN)

As Regras de Negócio definem as políticas de integridade, restrições e cálculos lógicos que o software deve fazer cumprir rigorosamente.

---

### `RN01` — Unicidade de Identificadores (SKU e E-mail)
* Todo produto deve possuir um código **SKU exclusivo** no sistema (ex: `SKU-0231`).
* Todo usuário deve possuir um **e-mail único** para autenticação.
* Tentativas de duplicidade devem ser abortadas com mensagem amigável de erro.

### `RN02` — Trava de Categoria por Rua (Galpão Organizado)
* Uma rua recém-criada encontra-se no estado **Livre**.
* No momento em que o primeiro produto for cadastrado ou armazenado na rua, essa rua assume e trava na categoria daquele produto.
* **Restrição:** É terminantemente proibido cadastrar ou transferir para uma rua produtos de categoria diferente da categoria travada nela (ex: uma rua travada em *Placa-mãe* não aceita *Memórias* nem *Fontes*).

### `RN03` — Saldo Não-Negativo (Estoque Mínimo Zero)
* O saldo (`quantidade`) de um produto nunca pode ser inferior a zero (`quantidade >= 0`).
* Em uma operação de **Saída (Baixa)**, se a `quantidade_solicitada > saldo_atual`, a operação deve ser bloqueada imediatamente com a mensagem: *"Saldo insuficiente. Estoque disponível: X unidades."*.

### `RN04` — Quantidade de Movimentação Estritamente Positiva
* Toda operação de Entrada ou Saída deve registrar um valor de quantidade **inteiro e estritamente maior que zero** (`quantidade > 0`). Não são permitidos valores nulos, negativos ou zerados.

### `RN05` — Atomicidade das Transações de Movimentação
* O registro de uma movimentação (Entrada/Saída) e a atualização do saldo do produto devem ocorrer obrigatoriamente dentro da **mesma transação de banco de dados** (`BEGIN ... COMMIT`).
* Caso ocorra qualquer falha durante a gravação, a transação inteira deve sofrer `ROLLBACK` para evitar discrepâncias entre o saldo e o histórico.

### `RN06` — Critério de Classificação de Estoque Baixo / Crítico
* O status de estoque de um componente é calculado dinamicamente com base no saldo e no limite mínimo:
  - **Crítico (Estoque Baixo):** `quantidade <= estoque_min` (badge vermelho / alerta prioritário).
  - **Atenção:** `quantidade > estoque_min` e `quantidade <= estoque_min * 1.5` (badge amarelo).
  - **Normal / OK:** `quantidade > estoque_min * 1.5` (badge verde).

### `RN07` — Consistência de Limites de Estoque
* No cadastro ou edição de produtos, o valor de **Estoque Mínimo** deve ser obrigatoriamente menor ou igual ao valor de **Estoque Máximo** (`estoque_min <= estoque_max`).

### `RN08` — Proteção contra Exclusão de Rua com Estoque
* Uma rua que possua produtos armazenados com saldo total maior que zero (`SUM(quantidade) > 0`) **NÃO** pode ser excluída. O usuário deve transferir ou zerar os produtos antes da exclusão.

### `RN09` — Imutabilidade de Histórico de Movimentações
* Os registros da tabela `movimentacoes` são dados de **auditoria permanente**. Não é permitido editar (`UPDATE`) nem excluir (`DELETE`) registros do histórico de movimentações. Qualquer ajuste posterior deve ser feito através de uma nova movimentação corretiva.

### `RN10` — Criptografia Obrigatória de Senhas
* Senhas de usuários nunca devem ser armazenadas em texto plano no banco de dados. Todas as senhas devem ser tratadas com algoritmo seguro de hash (ex: `werkzeug.security.generate_password_hash`) com salt antes do `INSERT`.

### `RN11` — Padrão de Nomenclatura no Plural para Tabelas
* As tabelas oficiais do banco de dados devem adotar nomes no plural (`usuarios`, `categorias`, `ruas`, `drives`, `produtos`, `movimentacoes`).

---

## 3. Requisitos Não-Funcionais (RNF)

| Identificador | Categoria | Descrição |
| :--- | :--- | :--- |
| **`RNF01`** | **Arquitetura** | O sistema deve ser desenvolvido em Python com **Flask**, utilizando o padrão de **Blueprints** para modularização de controllers e desacoplamento do código. |
| **`RNF02`** | **Banco de Dados** | O sistema deve utilizar **SQLite** para persistência local rápida em desenvolvimento e suportar **PostgreSQL** em produção através do `schema.sql` padronizado. |
| **`RNF03`** | **Interface & Responsividade** | A interface gráfica deve ser construída com HTML5 semântico, Jinja2, Bootstrap 5 e CSS customizado, adaptando-se a resoluções Desktop (monitores galpão) e Mobile (smartphones operadores). |
| **`RNF04`** | **Desempenho** | Consultas e carregamento de páginas devem responder em menos de **300ms** em condições normais de uso local. |
| **`RNF05`** | **Segurança (SQL Injection)** | Todas as operações SQL no backend devem ser executadas com consultas parametrizadas (`db.execute("... WHERE id = ?", (id,))`), sendo expressamente vedada a concatenação de strings. |
| **`RNF06`** | **Segurança de Sessão** | A aplicação deve configurar chave secreta (`app.secret_key`) para assinatura de cookies de sessão e proteção contra CSRF nas requisições. |
| **`RNF07`** | **Compatibilidade de Navegadores** | O sistema deve ser compatível com as versões recentes do Google Chrome, Mozilla Firefox, Microsoft Edge e Safari. |
| **`RNF08`** | **Manutenibilidade & Testabilidade** | O código deve possuir cobertura de testes automatizados com `pytest`/`unittest`, separando casos de sucesso e cenários de exceção baseados nos Casos de Uso. |

---

## 4. Matriz de Rastreabilidade (RF ⟷ RN ⟷ UC)

Esta matriz conecta os Requisitos Funcionais às suas Regras de Negócio e Casos de Uso, garantindo que nenhum requisito fique sem validação:

| Requisito Funcional (RF) | Regras de Negócio Aplicáveis (RN) | Caso de Uso (UC) Relacionado |
| :--- | :--- | :--- |
| **`RF01` — Login de Usuário** | `RN10` (Hash de Senha) | `UC01` |
| **`RF02` — Logout** | — | `UC02` |
| **`RF03` — Cadastro de Usuário** | `RN01` (E-mail Único), `RN10` (Hash) | `UC03` |
| **`RF04` — Cadastro de Rua** | `RN02` (Trava Inicial Livre) | `UC04` |
| **`RF05` — Visualizar Ruas** | `RN02` (Categoria Travada) | `UC05` |
| **`RF06` — Excluir Rua** | `RN08` (Não excluir rua com saldo) | `UC06` |
| **`RF07` — Cadastrar Produto** | `RN01` (SKU Único), `RN02` (Compatibilidade Rua), `RN07` (Mín <= Máx) | `UC07` |
| **`RF08` — Pesquisar Produtos** | `RN06` (Cálculo de Status) | `UC08` |
| **`RF09` — Editar Produto** | `RN07` (Mín <= Máx) | `UC09` |
| **`RF10` — Excluir Produto** | `RN09` (Integridade de Histórico) | `UC10` |
| **`RF11` — Registrar Entrada** | `RN04` (Qtd > 0), `RN05` (Transação Atômica), `RN09` (Imutabilidade) | `UC11` |
| **`RF12` — Registrar Saída** | `RN03` (Saldo >= 0), `RN04` (Qtd > 0), `RN05` (Atomicidade) | `UC12` |
| **`RF13` — Histórico Movimentações** | `RN09` (Imutabilidade e Auditoria) | `UC14` |
| **`RF14` — KPIs do Dashboard** | `RN06` (Cálculo Estoque Baixo) | `UC15` |
| **`RF15` — Gráficos do Dashboard** | `RN05` (Agregação temporal) | `UC15` |
| **`RF16` — Alerta Estoque Crítico** | `RN06` (Filtro `quantidade <= min`) | `UC15` |
| **`RF17` — API JSON Estoque** | `RN02` (Ruas compatíveis) | `UC16` |

---

> **Documento salvo em:** `app/docs/requisitos_e_regras_de_negocio.md`  
> **TechStock WMS** — Especificação de Requisitos e Engenharia de Software.
