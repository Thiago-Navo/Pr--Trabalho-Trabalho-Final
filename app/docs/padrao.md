# Padrão de Arquitetura — TechStock

## Filosofia

O projeto segue um padrão **simplificado**:
- Sem DTOs, repositories ou services
- Os **models são apenas containers de dados** (dataclasses) com get/set e campos e funções de banco de dados
- As **controllers carregam os models e passam diretamente aos templates**
- O banco é acessado via uma única classe de conexão (`Database`)
- As queries SQL são escritas diretamente nas funções dos models (não há camada extra)

---

## Estrutura de Pastas

```
app/
├── __init__.py              # Factory do Flask
├── database/
│   ├── __init__.py          # Instância global do Database
│   └── connection.py        # Classe Database (conexão SQLite)
├── models/
│   ├── __init__.py          # Re-exporta todos os models
│   ├── usuario.py           # Dataclass Usuario
│   ├── empresa.py           # Dataclass Empresa
│   ├── categoria.py         # Dataclass Categoria
│   ├── produto.py           # Dataclass Produto
│   ├── endereco_estoque.py  # Dataclass EnderecoEstoque
│   ├── estoque_local.py     # Dataclass EstoqueLocal
│   ├── movimento.py         # Dataclass Movimento
│   └── log_acesso.py        # Dataclass LogAcesso
├── controllers/
│   └── main_controller.py   # Blueprint com as rotas
├── templates/               # Jinja2 templates
├── css/                     # Estilos
├── schema.sql               # DDL do banco
└── docs/
    └── padrao.md            # Esta documentação
```

---

## Models (Dataclasses)

Cada model é uma `@dataclass(slots=True)` com os campos da tabela correspondente.

**Regras:**
- Apenas campos e tipos — **sem métodos** (sem `to_dict()`, sem validação, sem regras de negócio)
- Campos opcionais usam `Optional[T]` com valor padrão `None`
- Os campos seguem **exatamente** os nomes das colunas no `schema.sql`
- O construtor (`__init__`) é gerado automaticamente pelo `@dataclass`

### Exemplo

```python
@dataclass(slots=True)
class Produto:
    id: int
    nome: str
    descricao: Optional[str] = None
    altura: Optional[float] = None
    largura: Optional[float] = None
    peso: Optional[float] = None
    cor_predominante: Optional[str] = None
    qtd_min: int = 0
    qtd_max: Optional[int] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    categoria_id: Optional[int] = None
    fabricante_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
```

---

## Database (Conexão)

A classe `Database` usa o padrão **Flask `g`** para gerenciar uma única conexão por requisição.

```python
from app.database import database

# Dentro do model:
db = database.get_connection()
resultado = db.execute("SELECT * FROM produto").fetchall()
```

**Métodos:**
| Método | Descrição |
|--------|-----------|
| `get_connection()` | Retorna a conexão ativa (cria se não existir) |
| `close_connection(exception)` | Fecha a conexão ao final da requisição |

---

## Controller

A controller **não separa API de frontend**. Tudo é feito no mesmo fluxo:

1. Abre conexão com o banco
2. Executa a query SQL
3. Passa os dados para o template Jinja2

### Exemplo

```python
@front_bp.route("/produtos")
def listar_produtos():
    db = database.get_connection()
    produtos = db.execute("SELECT * FROM produto").fetchall()
    return render_template("produtos.html", produtos=produtos)
```

Não há:
- Rotas `/api/...`
- Retorno de JSON
- Separação frontend/backend via JS

---

## Fluxo Completo (Exemplo)

```
Usuário acessa "/produtos"
        ↓
Controller `listar_produtos()` 
        ↓
db = database.get_connection()
        ↓
db.execute("SELECT * FROM produto")
        ↓
render_template("produtos.html", produtos=dados)
        ↓
Template Jinja2 renderiza a página com os dados
```

---

## Models Disponíveis

| Model | Tabela | Descrição |
|-------|--------|-----------|
| `Usuario` | `usuario` | Usuários do sistema |
| `Empresa` | `empresa` | Fabricantes e fornecedores |
| `Categoria` | `categoria` | Categorias e subcategorias |
| `Produto` | `produto` | Itens do estoque |
| `EnderecoEstoque` | `endereco_estoque` | Hierarquia do estoque (corredor → modulo → nivel → vao) |
| `EstoqueLocal` | `estoque_local` | Vínculo produto ↔ endereço com quantidade |
| `Movimento` | `movimento` | Entradas, saídas, transferências e ajustes |
| `LogAcesso` | `log_acesso` | Auditoria geral do sistema |
