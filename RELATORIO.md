# Relatório de Processo — TechStock

## 1. Visão Geral do Projeto

O **TechStock** foi desenvolvido como Projeto Integrador do curso Full Stack Python, com o objetivo de entregar uma aplicação web completa para gestão de estoque de informática (WMS - *Warehouse Management System*). O foco central foi eliminar o uso de planilhas manuais e criar uma ferramenta confiável, segura, esteticamente agradável e com arquitetura em camadas.

---

## 2. Fontes de Consulta e Ferramentas Extra-Aula

Para além das aulas regulares, a equipe utilizou diversas ferramentas de apoio e fontes técnicas:

### 2.1 Documentações Oficiais
- **Flask Documentation (v3.x)**: Consulta às seções de *Application Factory*, *Blueprints*, *Context Locals* (`g`, `session`) e integração de CLI commands (`@app.cli.command`).
- **SQLite Documentation**: Compreensão da ativação obrigatória de integridade referencial via `PRAGMA foreign_keys = ON` e particularidades de concorrência/file locks no Windows.
- **MDN Web Docs (Mozilla)**: Boas práticas de acessibilidade WCAG (atributos ARIA, contrastes e tags semânticas) e uso da API assíncrona `fetch()` com promises e tratamento de erros com `.catch()`.

### 2.2 Serviços de Inteligência Artificial
- **Claude & ChatGPT**: Utilizados no início para validação da modelagem relacional, apoio na criação dos schemas e geração de dados de exemplo variados para o povoamento do `seed.py`.
- **Google Antigravity / Gemini**: Utilizado na etapa final para auditoria estrita do checklist de entrega, refatoração de testes unitários no pytest, resolução de deadlocks em conexões no ambiente Windows e implementação do padrão Repository com POO.

### 2.3 Comunidade e Plataformas de Aprendizado
- **Stack Overflow**: Consulta indispensável para solução de erros e dúvidas técnicas do dia a dia, como tratamento de constraints e locks no SQLite em ambiente Windows, manipulação de sessões e cookies no Flask e depuração de chamadas assíncronas com a API `fetch()` no front-end.
- **YouTube**: Utilizado para reforço visual e estudo complementar, acompanhando tutoriais práticos de arquitetura Flask (Application Factory e Blueprints), estruturação de layouts modernos com CSS Grid/Flexbox e técnicas de responsividade mobile.

---

## 3. Dificuldades Encontradas e Soluções Adotadas

| Desafio Técnico | Como Foi Superado |
|---|---|
| **Concorrência de Arquivo no Windows (`PermissionError 32`)** | No ambiente Windows, o SQLite mantém handles abertos sobre arquivos `.db` se a conexão não for fechada antes de um `os.remove`. Superamos ajustando o teardown dos fixtures do pytest com encerramento forçado de conexões e tratamento de exceção seguro. |
| **Garantia de Senhas Seguras sem Quebrar Usuários Antigos** | A API precisava forçar hash forte (`scrypt`/`pbkdf2`), mas havia dados com formato misto. Criamos uma camada de checagem inteligente no login que autentica o usuário e migra automaticamente qualquer credencial antiga para hash seguro no primeiro acesso. |
| **Exportação Standalone 100% Funcional Offline** | O desafio de exportar um relatório que funcione sem servidor foi resolvido injetando os dados do estoque diretamente como um array JSON dentro de uma tag `<script>` no HTML retornado, com código JavaScript Vanilla embarcado para filtrar e buscar em tempo real na própria máquina do cliente. |
| **Desacoplamento de Rotas e Banco** | As consultas SQL estavam dispersas pelas controllers. A introdução do **Repository Pattern** (`ProdutoRepository`) e do modelo de domínio com regras de negócio em POO (`Produto`) isolou a persistência e facilitou a escrita de testes unitários. |

---

## 4. Autoavaliação Individual da Equipe

### Pâmela Cristina Rodrigues Barbosa
- **Atividades e Contribuições Desenvolvidas:**
  - **Documentação Técnica e de Negócio:** Elaboração completa dos requisitos funcionais, regras de negócio e casos de uso do sistema.
  - **Diagramas Técnicos:** Criação dos diagramas de arquitetura, fluxo de processos e modelagem relacional (Entidade-Relacionamento).
  - **Gestão e Cronograma:** Definição das etapas de desenvolvimento, marcos de entrega e acompanhamento do cronograma da equipe.
  - **Code Review e Correções:** Revisão criteriosa de Pull Requests da equipe, alinhamento de branches e resolução de bugs e inconsistências.
  - **Dashboard Gerencial:** Desenvolvimento e refino da tela de indicadores principais de estoque (KPIs, gráficos analíticos e alertas de reposição).
  - **Permissões e Segurança (RBAC):** Implementação do controle de acesso por papéis (Administrador e Operador) com decoradores de proteção de rotas (`@admin_required` e `@login_required`).
  - **Padrão MVC e Arquitetura:** Estruturação em camadas (Model-View-Controller) com divisão em Blueprints para desacoplamento e manutenibilidade.
  - **Apresentação e Slides:** Criação do roteiro e dos slides padrão para a apresentação final do projeto.
  - **Testes de Integração e Ambiente:** Condução de testes do fluxo integrado da API, validação da persistência relacional com chaves estrangeiras ativas e apoio nos ensaios de execução em ambiente limpo.
  - **Participação no povoamento e massa de testes (seed.py):** Elaboração e estruturação do script de seed automatizado para popular o banco de dados com empresas, fornecedores, produtos e movimentações realistas.
- **O que compreendi bem:** A estruturação completa do padrão arquitetural MVC em Flask, modelagem de bancos relacionais com SQLite e integridade referencial ativa, controle de permissões por perfil de usuário, elaboração de documentação viva e diagramas, condução de code reviews e a importância de testes automatizados para garantir a estabilidade do sistema.
- **O que ainda preciso aprimorar:** Desejo me aprofundar em ORMs mais complexos como SQLAlchemy em larga escala, pipelines de CI/CD automatizadas, migrações com Alembic e estratégias de cache distribuído com Redis.

### Thiago Rodrigues
- **Atividades e Contribuições Desenvolvidas:**
  - **Prototipagem e Wireframes:** Criação da prototipagem completa das interfaces no Figma e Draw.io, com foco em experiência do usuário (UX) em telas desktop e mobile.
  - **Desenvolvimento Front-end Responsivo:** Implementação de toda a interface do sistema com HTML5 semântico, CSS Grid e Flexbox, dispensando frameworks pesados e garantindo alta performance.
  - **Consumo Assíncrono da API:** Programação em JavaScript Vanilla utilizando a API assíncrona `fetch()` para comunicação fluida com o backend sem necessidade de recarregar a página (Single Page Experience).
  - **Temas e Acessibilidade (Dark/Light Mode):** Criação da alternância entre modo claro e escuro com persistência da preferência do usuário no `localStorage` e conformidade com diretrizes de acessibilidade W3C/WCAG.
  - **Mídias e Recursos PWA:** Implementação de Progressive Web Apps (PWA) com Service Workers, manifesto web e integração de playlist de áudio interativa com capas personalizadas.
  - **Validação de Interface e Testes do Usuário:** Execução de testes de usabilidade, auditorias de contraste visual e revisão do fluxo de ponta a ponta ("caminho feliz") da aplicação.
- **O que compreendi bem:** Estruturação de layouts modernos utilizando CSS Grid e Flexbox sem dependência de frameworks pesados, consumo assíncrono de rotas JSON com `fetch()` para atualizar a tela sem reload, Dark/Light Mode com persistência e implementação de Progressive Web Apps (PWA) com Service Workers.
- **O que ainda preciso aprimorar:** Quero aprofundar conhecimentos em acessibilidade avançada (auditorias automatizadas Lighthouse/Axe) e padrões de design system escaláveis.

### Maurício Keiser
- **Atividades e Contribuições Desenvolvidas:**
  - **Povoamento e Massa de Testes (`seed.py`):** Elaboração e estruturação do script de seed automatizado para popular o banco de dados com empresas, fornecedores, produtos e movimentações realistas.
  - **Conexões e Mapeamento de Dados:** Inicialização das camadas de acesso a dados no SQLite, preparando os métodos de CRUD (criação, edição, visualização, listagem e exclusão).
  - **Desenvolvimento da API REST (Back-end):** Implementação completa dos endpoints RESTful em Flask para Empresas, Fornecedores e Produtos com respostas em formato JSON e códigos de status HTTP semânticos (200, 201, 400, 404).
  - **Integração com API Externa (ViaCEP):** Integração com o webservice do ViaCEP para preenchimento automatizado de endereços (logradouro, bairro, cidade, UF) a partir do CEP cadastrado.
  - **Segurança de Consultas e Tratamento de Erros:** Implementação de queries parametrizadas para proteção contra SQL Injection e tratamento robusto de exceções nas operações de banco.
- **O que compreendi bem:** Desenvolvimento de rotas RESTful em Flask com retorno de status HTTP adequados (200, 201, 400, 404), estruturação de scripts de seed para recriação rápida de dados de teste e integração com APIs externas (ViaCEP).
- **O que ainda preciso aprimorar:** Gostaria de estudar autenticação federada com OAuth2/JWT e testes automatizados de carga em endpoints de APIs de alta concorrência.

---

## 5. Sugestões e Avaliação do Curso

- **Avaliação Geral:** O curso proporcionou uma base sólida e prática, integrando de forma realista o ecossistema Python desde a modelagem de banco de dados e backend com Flask até as interfaces web responsivas. A exigência de colaboração real com Git e PRs simulou bem o dia a dia de um time profissional de tecnologia.
- **Sugestões:**
  1. Incluir uma aula dedicada exclusivamente a Docker e deploy contínuo em nuvem (ex.: Render, Railway ou VPS).
  2. Dedicar mais tempo a padrões arquiteturais em Python (como Repository e Clean Architecture) antes da entrega final, para que os alunos possam planejar o código já com essa separação desde a primeira semana.
