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
- **O que compreendi bem:** A estruturação de bancos relacionais com SQLite, uso de chaves estrangeiras ativas, regras de controle de acesso por papel (RBAC com decorators em Flask) e a importância de testes automatizados para evitar regressões.
- **O que ainda preciso aprimorar:** Desejo me aprofundar em ORMs mais complexos como SQLAlchemy em larga escala, migrações com Alembic e estratégias avançadas de cache com Redis.

### Thiago Rodrigues
- **O que compreendi bem:** Estruturação de layouts modernos utilizando CSS Grid e Flexbox sem dependência de frameworks pesados, consumo assíncrono de rotas JSON com `fetch()` para atualizar a tela sem reload, Dark/Light Mode com persistência e implementação de Progressive Web Apps (PWA) com Service Workers.
- **O que ainda preciso aprimorar:** Quero aprofundar conhecimentos em acessibilidade avançada (auditorias automatizadas Lighthouse/Axe) e padrões de design system escaláveis.

### Maurício Keiser
- **O que compreendi bem:** Desenvolvimento de rotas RESTful em Flask com retorno de status HTTP adequados (200, 201, 400, 404), estruturação de scripts de seed para recriação rápida de dados de teste e integração com APIs externas (ViaCEP).
- **O que ainda preciso aprimorar:** Gostaria de estudar autenticação federada com OAuth2/JWT e testes automatizados de carga em endpoints de APIs de alta concorrência.

---

## 5. Sugestões e Avaliação do Curso

- **Avaliação Geral:** O curso proporcionou uma base sólida e prática, integrando de forma realista o ecossistema Python desde a modelagem de banco de dados e backend com Flask até as interfaces web responsivas. A exigência de colaboração real com Git e PRs simulou bem o dia a dia de um time profissional de tecnologia.
- **Sugestões:**
  1. Incluir uma aula dedicada exclusivamente a Docker e deploy contínuo em nuvem (ex.: Render, Railway ou VPS).
  2. Dedicar mais tempo a padrões arquiteturais em Python (como Repository e Clean Architecture) antes da entrega final, para que os alunos possam planejar o código já com essa separação desde a primeira semana.
