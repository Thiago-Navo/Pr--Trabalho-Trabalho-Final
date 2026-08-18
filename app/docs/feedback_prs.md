# Feedback e Alinhamento Técnico — PRs #5 e #6

Este documento reúne as orientações e revisões dos Pull Requests abertos para a equipe do **TechStock**.

---

## 📌 1. Feedback para o Mauricio (PR #5 — `app/seed.py`)

### 1.1. Padronização do Schema para Plural
Conforme alinhado com o time, vamos oficializar os nomes das tabelas no **plural** em todo o projeto.
O arquivo `app/seed.py` já utilizou nomes no plural (`usuarios`, `categorias`, `ruas`, `drives`, `produtos`, `movimentacoes`), o que agora se tornará o padrão oficial do banco de dados e do `app/schema.sql`.

* **Tabelas oficiais:**
  - `usuarios`
  - `categorias`
  - `ruas`
  - `drives` (se mantida a divisão por drives)
  - `produtos`
  - `movimentacoes`

---

### 1.2. Integração com `app/database/connection.py`
Para manter o projeto desacoplado e centralizar as configurações do SQLite, evite instanciar conexões manuais com `sqlite3.connect("techstock.db")` diretamente dentro dos scripts.

Utilize a classe/instância de banco em `app/database/`:

#### Exemplo de implementação recomendada no `seed.py`:

```python
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app.database import database  # Importa a instância centralizada

def get_db():
    """Obtém conexão usando as configurações centrais do banco."""
    conn = sqlite3.connect(database.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
```

> **Dica:** Centralizar o `database.db_path` garante que, se o caminho do banco for alterado nas variáveis de ambiente ou testes, o `seed.py` continuará funcionando perfeitamente sem necessidade de alterar código.

---

---

## 📌 2. Feedback para o Thiago (PR #6 — Templates HTML)

### 2.1. Arquivos Estáticos Faltantes (Onde e o que falta)
Os templates adicionados em `app/templates/` estão excelentes e modernos, porém alguns arquivos estáticos referenciados ainda não existem no repositório. Para que as páginas renderizem corretamente sem erros 404 no console, precisamos criar/adicionar os seguintes arquivos:

1. **CSS Completo:**
   - **Arquivo:** `app/static/css/style.css`
   - **Situação:** O arquivo atual possui apenas 22 linhas e não contém os estilos usados pelos templates (ex: classes `.app-shell`, `.sidebar`, `.kpi-grid`, `.card-panel`, `.table-custom`, `.stock-level`, `.badge-tag`, `.btn-primary-custom`, etc.).
   - **Ação:** Atualizar o `style.css` com as definições visuais completas do protótipo.

2. **Scripts JavaScript:**
   - `app/static/js/app.js` (gerencia alternância de tema dark/light, busca e interações)
   - `app/static/js/nav.js` (gerencia transições e navegação)
   - `app/static/js/playlist.js` (caso o player de áudio seja mantido)

3. **Imagens/Ícones:**
   - `app/static/img/covers/default-cover.svg` (capa padrão do player)

---

### 2.2. Aviso sobre a Criação das Rotas Flask
Como o projeto está sendo construído do zero, é esperado que as rotas ainda estejam pendentes. Apenas lembrando a lista de endpoints que precisaremos declarar nas controllers (`app/controllers/main_controller.py` ou novos blueprints) para atender aos `url_for(...)` dos templates:

* **Telas / Views:**
  - `login`, `logout`, `cadastro`
  - `dashboard`
  - `produtos`, `ruas`, `movimentacoes`, `entradas`, `saidas`
* **Ações de Formulário (POST):**
  - `novo_produto`, `excluir_produto` (e rota `/produtos/<id>/editar`)
  - `nova_rua`, `excluir_rua` (e rota `/ruas/<id>/editar`)
  - `nova_movimentacao`, `nova_entrada`, `nova_saida`
* **API JSON (usada no JS das telas):**
  - `/api/produtos/<id>/estoque`

---

### 2.3. Dúvida sobre o Player de Música (`base.html`)
Identificamos que no arquivo `app/templates/base.html` (linhas 39 a 58) foi incluído um componente de **reprodutor de música** na barra lateral (`<div class="music-player">` com botões de play, avançar, volume e tag `<audio id="audioFundo">`).

❓ **Pergunta para o Thiago:**
> *O player de música é uma funcionalidade que você realmente planeja incluir no sistema TechStock ou foi adicionado por engano/herança de algum template externo?*
> 
> Caso não vá ser utilizado, podemos remover essa seção e as referências a `playlist.js` e `default-cover.svg` para manter o código do projeto mais limpo e focado no WMS.
