# TechStock

O **TechStock** é uma aplicação web para gestão de estoque de informática, desenvolvida para substituir planilhas manuais por um sistema organizado, seguro e visualmente simples. O software permite controlar produtos, movimentações, categorias e níveis de estoque em um único ambiente.

## Objetivo

Centralizar o controle de itens de informática em um sistema com autenticação, permissões por perfil e dashboard de indicadores.

## Funcionalidades principais

- Cadastro de usuários e autenticação
- Controle de acesso por perfil (admin e operador)
- Cadastro de ruas e produtos
- Gestão de entradas e saídas
- Movimentação entre ruas
- Dashboard com KPIs e gráficos
- Exportação do relatório em HTML standalone
- Banco SQLite local com seed inicial

## Tecnologias

- Python 3
- Flask
- SQLite
- Jinja2
- Werkzeug
- pytest

## Estrutura do projeto

- `app/` — aplicação principal
- `app/controllers/` — rotas e regras de negócio
- `app/database/` — conexão e API externa
- `app/templates/` — páginas HTML
- `app/static/` — CSS, JS e manifest
- `tests/` — testes automatizados
- `run.py` — ponto de entrada da aplicação

## Requisitos

- Python 3.10 ou superior
- Ambiente virtual recomendado

## Instalação

No terminal, na pasta do projeto:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Execução

```bash
python run.py
```

A aplicação fica disponível em:

```text
http://127.0.0.1:5001
```

## Login padrão

Usuário admin:

- usuário: `admin`
- senha: `admin123`

Também existe um usuário de exemplo:

- usuário: `pamela`
- senha: `admin123`

## Testes

```bash
.venv\Scripts\python -m pytest -q
```

## Observações

- O projeto utiliza SQLite local com seed automático em primeira execução.
- O dashboard e os relatórios são gerados com dados do banco do sistema.
- A exportação standalone gera um HTML pronto para visualização offline.

## Status do projeto

O TechStock está em fase de entrega final com funcionalidade principal implementada, testes automatizados e documentação básica concluída.

