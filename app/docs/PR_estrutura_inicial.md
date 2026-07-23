# feat: adiciona estrutura inicial da aplicação TechStock

### O que foi feito

Estrutura inicial do projeto **TechStock** — aplicação web para gestão de estoque de informática.

### Arquitetura

- MVC simplificado (sem camadas DTO, Repository ou Service)
- Dados carregados diretamente no template 
- Flask + Jinja2 + SQLite

### O que contém

- **`app/database/connection.py`** — Classe `Database` com conexão SQLite gerenciada pelo Flask
- **`app/models/`** — 8 dataclasses representando as entidades do MER:
  `Usuario`, `Empresa`, `Categoria`, `Produto`, `EnderecoEstoque`,
  `EstoqueLocal`, `Movimento`, `LogAcesso`
- **`app/controllers/main_controller.py`** — Rotas iniciais (`/` e `/sobre`)
- **`app/templates/`** — `index.html` e `sobre.html`
- **`app/css/style.css`** — Estilo base
- **`app/schema.sql`** — Script de criação do banco
- **`run.py`** — Ponto de entrada da aplicação
- **`.gitignore`** — Ignorando `__pycache__`, `.db`, `venv`, etc.
- **`requirements.txt`** — Flask >= 3.0.0

### Documentação

- `app/docs/padrao.md` — Documentação do padrão de arquitetura adotado
- `Pré-Trabalho/docs/pre_projeto.md` — Atualização do diagrama MER

### Como testar

```bash
pip install -r requirements.txt
python run.py
# Acessar http://localhost:5000
```
