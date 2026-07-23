# Cronograma de Desenvolvimento — TechStock
**Prazo de Entrega Final:** 22/09/2026  
**Meta de Conclusão Técnica e Documentação:** 15/09/2026 *(Garantindo 1 semana de folga para revisão e testes finais)*

---

## 📅 Etapas do Projeto e Atribuições

### Fase 1: Fundação, Banco de Dados, Prototipagem e Arquitetura MVC
* **Período:** 16/07/2026 a 11/08/2026 (2 semanas)
* **Responsáveis:** 
  * **Mauricio Keiser:** Criação do script de povoamento `seed.py` para testes imediatos. iniciação das conexões do modelos com o banco de dados, para cada model ter as funções que recebem parametros para executar Criação, Edição, visualização, listagem e exclusão.
  * **Thiago Rodrigues:**  Criação da prototipagem completa das telas (wireframes desktop e mobile no Figma/Draw.io).
  * **Pâmela Cristina:** Configuração do banco de dados SQLite, modelagem inicial, criação do `schema.sql` e estruturação oficial do padrão MVC, desenho dos diagramas didáticos de arquitetura e fluxo de dados.
* **Atividades:**
  * Configuração do ambiente Flask com `venv`, `requirements.txt` e SQLAlchemy.
  * Modelagem das tabelas e geração do script `seed.py` com dados de exemplo.
  * Criação dos protótipos de tela visando semântica e acessibilidade W3C/WCAG.
  * Definição dos diagramas de classe/fluxo.

### Fase 2: Core do Sistema (CRUDs), API Externa e Front-end Base
* **Período:** 11/08/2026 a 01/09/2026 (3 semanas)
* **Responsáveis:** 
  * **Thiago Rodrigues:** Desenvolvimento do Front-end em HTML semântico, CSS Grid (responsivo PC/Mobile) e JS Vanilla usando `fetch()` assíncrono para consumir as rotas JSON.
  * **Mauricio Keiser:** Implementação das rotas CRUD (Back-end) e **integração com API de Terceiros** (ex: ViaCEP para busca automática de endereço de Fornecedores/Empresas).
  * **Pâmela Cristina:** Revisão de Pull Requests, controle de qualidade de código e implementação das páginas de erro HTTP customizadas (`404.html` e `500.html`).
* **Atividades:**
  * Desenvolvimento das telas responsivas e integração com as rotas Flask.
  * Consumo assíncrono de API REST no front-end.
  * Implementação da integração com a API externa.
  * Garantia de tratamento de exceções e proteção contra SQL Injection.

### Fase 3: Regras de Negócio, Permissões, Standalone e Dashboard
* **Período:** 01/09/2026 a 15/09/2026 (2 semanas)
* **Responsáveis:** 
  * **Pâmela Cristina:** 
    * Implementação do controle de permissões de usuários (RBAC / Decorators no Flask por perfil/cargo).
    * Lógica da **Dashboard** e rotas da API REST.
    * Desenvolvimento do endpoint de **Exportação Standalone** (relatório HTML estático com JS/dados embutidos para execução offline).
    * Implementação dos **3 Testes Unitários mínimos** cobrindo regras de negócio/permissões.
* **Atividades:**
  * Lógica de atualização atômica de saldo no estoque (entradas/saídas).
  * Criação das travas de autenticação (hash de senha na sessão) e autorização por cargo.
  * Criação da funcionalidade de exportação de relatório offline.
  * Escrita e validação dos testes unitários em Python (`unittest`/`pytest`).

### Fase 4: Integração Geral, Testes e Correção de Bugs ("Caminho Feliz")
* **Período:** 08/09/2026 a 15/09/2026 (Paralelo à reta final da Fase 3 / 1 semana dedicada)
* **Responsáveis:** **Equipe Inteira** 
* **Atividades:**
  * Teste do fluxo completo ("caminho feliz"): cadastro $\rightarrow$ API CEP $\rightarrow$ movimentação de estoque $\rightarrow$ atualização do Dashboard $\rightarrow$ exportação standalone.
  * Auditoria rápida de acessibilidade (contraste, foco visível e navegação).
  * Validação final dos Pull Requests e aprovações no GitHub.

### Fase 5: Documentação Completa, GitHub Pages e Slides
* **Período:** 08/09/2026 a 15/09/2026 (1 semana)
* **Responsável:** **Pâmela** *(com apoio do Mauricio e Thiago nas informações técnicas)*.
* **Atividades:**
  * **README.md oficial:** Instruções claras de instalação, execução, lista de tecnologias e divisão de tarefas.
  * **Relatório de Processo (`RELATORIO.md`):** Registro de ferramentas externas/IAs utilizadas, desafios, autoavaliação dos membros e sugestões sobre o curso.
  * **GitHub Pages:** Criação de uma página estática informativa e bem ilustrada sobre o TechStock para o portfólio.
  * **Slides de Apresentação:** Montagem do material visual para o Pitch final.

---

## 🛡️ Folga, Ensaio e Ajustes Finais
* **Período:** 15/09/2026 a 22/09/2026 (1 semana de folga estratégica)
* **Responsáveis:** **Equipe Inteira** (Pâmela, Thiago e Mauricio).
* **Objetivo:** 
  * Ensaio do Pitch de apresentação.
  * Execução do projeto em um ambiente limpo (clonar do zero usando o `seed.py`) para simular a avaliação do professor.
  * Envio do link oficial do repositório no dia **22/09/2026**.