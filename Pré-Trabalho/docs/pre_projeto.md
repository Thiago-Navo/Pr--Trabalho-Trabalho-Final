# Pré-Projeto — Sistema de Controle de Estoque de Peças de Informática

## 1. Identificação da Equipe

### Nome do Projeto
**TechStock** (nome provisório)

### Integrantes

| Nome | GitHub | Responsabilidade |
|------|---------|------------------|
| Thiago Rodrigues | https://github.com/thiago-navo | Front-end (HTML, CSS e JavaScript e lógica do sistema) | 
| Mauricio Keiser | https://github.com/mauriciokeiser | Back-end (Flask, banco de dados e lógica do sistema) |

---

## 2. Elevator Pitch

Para empresas e setores de estoque de informática que precisam controlar seus produtos, o **TechStock** é uma aplicação web que permite cadastrar, consultar e gerenciar peças de informática de forma simples e organizada. Diferente de planilhas ou anotações manuais, o sistema centraliza todas as informações em um único lugar, tornando o controle do estoque mais rápido, seguro e eficiente.

---

## 3. Público-Alvo e Contexto

### Público-Alvo

- Empresas de informática.
- Lojas de computadores.
- Centros de distribuição.
- Setores de estoque de empresas como a Pichau.

### Contexto de Uso

O sistema será utilizado em computadores do setor de estoque durante o recebimento, conferência, armazenamento e movimentação de peças de informática.

### Por que é melhor que planilhas ou papel?

- Todas as informações ficam centralizadas.
- Facilita a busca de produtos.
- Reduz erros de atualização.
- Mantém o estoque sempre atualizado.
- Permite consultar rapidamente a quantidade disponível.

---

## 4. Funcionalidades Principais

- Como usuário, quero cadastrar peças de informática para controlar os produtos disponíveis no estoque.
- Como usuário, quero pesquisar produtos por nome ou categoria para encontrá-los rapidamente.
- Como usuário, quero registrar entradas e saídas de produtos para manter o estoque atualizado.
- Como usuário, quero editar ou excluir produtos cadastrados para corrigir informações.
- Como usuário, quero visualizar um relatório do estoque atual para acompanhar a quantidade de cada produto.

---

## 5. Escopo Negativo

O projeto **não terá**:

- Sistema de vendas.
- Controle financeiro.
- Pagamentos online.
- Aplicativo mobile nativo.
- Integração com marketplaces.
- Controle por código de barras.
- Notificações por e-mail.
- Login com redes sociais.

---

## 6. Modelo de Dados Preliminar

### PRODUTO

| Campo |
|--------|
| id |
| nome |
| categoria |
| marca |
| modelo |
| quantidade |
| preço |
| fornecedor |

### MOVIMENTACAO

| Campo |
|--------|
| id |
| produto_id |
| tipo (Entrada ou Saída) |
| quantidade |
| data |

### Relacionamento

Um **Produto** pode possuir várias **Movimentações**.

---

## 7. Wireframes

Serão anexados:

### Tela para Computador

- Menu lateral.
- Lista de produtos.
- Campo de pesquisa.
- Botão "Cadastrar Produto".
- Botões para editar e excluir.

### Tela para Celular

- Menu simplificado.
- Lista de produtos.
- Campo de pesquisa.
- Botão para cadastrar produto.

*(Os wireframes serão desenvolvidos no Figma ou Draw.io e anexados ao projeto.)*

---

## 8. Stack Confirmado

### Flask + Jinja2

Será utilizado para desenvolver o back-end e gerar páginas dinâmicas.

### SQLite

Será utilizado como banco de dados por ser simples, leve e adequado ao tamanho do projeto.

### HTML + CSS Grid + JavaScript Vanilla

Serão utilizados para desenvolver a interface responsiva da aplicação.

### GitHub com Pull Requests

Será utilizado para controle de versão e organização do desenvolvimento.

### Biblioteca adicional

**SQLAlchemy**

Será utilizada para facilitar a comunicação entre a aplicação e o banco de dados utilizando ORM.

---

## 9. Autoavaliação de Riscos

### Qual é a parte que vocês mais temem implementar?

Garantir que as movimentações de entrada e saída atualizem corretamente a quantidade dos produtos sem gerar inconsistências.

### O que acontece se um membro da equipe sumir uma semana antes da entrega?

As tarefas serão redistribuídas entre os demais integrantes, priorizando as funcionalidades essenciais para garantir a entrega do projeto.

### Qual é o "caminho feliz" mínimo?

Mesmo que funcionalidades extras não sejam concluídas, o sistema deverá permitir:

- Cadastro de produtos.
- Pesquisa de produtos.
- Registro de entrada.
- Registro de saída.
- Atualização automática da quantidade em estoque.

Com essas funcionalidades, o sistema já será capaz de controlar o estoque de peças de informática de forma eficiente.