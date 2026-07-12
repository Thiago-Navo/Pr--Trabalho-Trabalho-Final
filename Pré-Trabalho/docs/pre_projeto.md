# Pré-Projeto — Inventory Flow (Sistema de Gerenciamento de Estoque de Componentes de Informática para Varejistas

## 1. Identificação da Equipe

### Nome do Projeto

- **TechStock:** Destaca o fluxo inteligente de mercadorias.


### Integrantes

| Nome | GitHub | Responsabilidade |
| - | - | - |
| Thiago Rodrigues | [https://github.com/thiago-navo](https://github.com/thiago-navo) | Front-end (HTML, CSS e JavaScript e lógica do sistema) |
| Mauricio Keiser | [https://github.com/mauriciokeiser](https://github.com/mauriciokeiser) | Back-end (Flask, banco de dados e lógica do sistema) |
| Pâmela Cristina Rodrigues Barbosa |  |  |


## 2. Elevator Pitch

Uma aplicação simples funcional para pequenas empresas e setores de estoque de informática no ramo varejista que precisam controlar seus produtos, o **TechStock** é uma aplicação web que permite cadastrar, consultar e gerenciar peças de informática de forma simples e organizada. Diferente de planilhas ou anotações manuais, o sistema centraliza todas as informações em um único lugar, tornando o controle do estoque mais rápido, seguro e eficiente, **trazendo agilidade.**

## 3. Público-Alvo e Contexto

### Público-Alvo

**	Quem vai usar: encarregados ou gerentes de estoque, conferentes, recebedores e despachadores, operadores e movimentadores de estoque.**

	**Em que situação:** dentro de pequenos galpões ou salas comerciais.

- Empresas de informática.

- Lojas de computadores.

- Pequenos centros de distribuição.

- Setores de estoque de empresas como exemplo: Pichau.

### Contexto de Uso

	O sistema será utilizado em computadores do setor de estoque durante o recebimento, conferência, armazenamento, movimentação e envio de componentes de informática.

### Por que é melhor que planilhas ou papel?

- Todas as informações ficam centralizadas.

- Facilita a busca de produtos.

- Reduz erros de atualização.

- Mantém o estoque sempre atualizado.

- Permite consultar rapidamente a quantidade disponível.

## 4. Funcionalidades Principais

- Como recebedor, quero cadastrar componentes de informática para controlar os produtos disponíveis no estoque.

- Como conferente, quero pesquisar produtos por nome ou categoria para encontrá-los rapidamente.

- Como estoquista operador e recebedor ou despachador, quero registrar entradas e retiradas de produtos para manter o estoque atualizado.

- Como gerente de estoque ou estoquista operador, quero editar ou excluir produtos cadastrados para corrigir informações.

- Como gerente de estoque, quero visualizar um relatório do estoque atual para acompanhar a quantidade de cada produto.

## 5. Escopo Negativo

O projeto **não terá**:

- Sistema de vendas ou emissão de notas fiscais.

- Controle financeiro complexo.

- Pagamentos online.

- Aplicativo mobile nativo (apenas web responsiva)

- Integração com marketplaces.

- Controle por código de barras.

- Notificações por e-mail.

- Login com redes sociais.

## 6. Modelo de Dados Preliminar – Banco de Dados Sqlite3

### LOGIN

| Campo |
| - |
| id |
| nome |
| email |
| celular |
| cargo |
| poder |
| senhahash |
| criadodata |
| atualizadodata |
| atividadeonline |
| deletadodata |


### EMPRESA

| Campo |
| - |
| id |
| nfantasiaempr |
| emprcnpj |
| emprnome |
| emprtelefixo |
| emprcelular |
| empremail |
| empcep |
| emprestado |
| emprcidade |
| emprlogradouro |
| emprnr |
| emprcompl |
| empreobs |
| dtcadastro |
| dtatual |
| ativonline |
| dtdel |

### PRODUTO

| Campo |
| - |
| id |
| nomeprod |
| altura |
| largura |
| peso |
| corpredomin |
| categoria\_id |
| fabricante\_id |
| marca\_id |
| modelo\_id |
| fornecedor\_id |
| entrada\_id |
| retirada\_id |
| movimento\_id |
| estoque\_id |
| login\_id |


### CATEGORIA

| Campo |
| - |
| id |
| nomecateg |
| subcategoria |
| descritivo |


### FABRICANTE

| Campo |
| - |
| id |
| nomefabr |
| nacionalidade |
| sitefabric |
| emailsuporte |


### MARCA

| Campo |
| - |
| id |
| nomemarca |
| anocriado |
| fabricante\_id |


### MODELO

| Campo |
| - |
| id |
| nomemodelo |
| anoproduzido |
| descritivo |
| marca\_id |
| fabricante\_id |


### FORNECEDOR

| Campo |
| - |
| id |
| cnpj |
| nomefantasia |
| nomeforn |
| telecelular |
| telefixo |
| emailforn |
| suporteforn |
| cep |
| estado |
| cidade |
| logradouro |
| nr |
| complemento |
| login\_id |


### ENTRADA

| Campo |
| - |
| id |
| dataentrada |
| qtdentrada |
| valorentrada |
| tipoentrada |
| obsentrada |
| produto\_id |
| login\_id |


### RETIRADA

| Campo |
| - |
| id |
| dataretirada |
| qtdretirada |
| valorretirada |
| tiporetirada |
| obsretirada |
| produto\_id |
| login\_id |


### MOVIMENTO

| Campo |
| - |
| id |
| data |
| internomov |
| entrada\_id |
| retirada\_id |
| produto\_id |
| login\_id |


### ESTOQUE

| Campo |
| - |
| id |
| saldo |
| valor |
| qtdmin |
| produto\_id |


### Relacionamento

Um **Produto** pode possuir várias **Movimentações**.

## 7. Wireframes

Serão anexados:

### Cronograma com atividades a serem elaboradas durante o projeto

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

