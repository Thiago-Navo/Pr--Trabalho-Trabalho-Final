"""Modelo EnderecoEstoque — a ser implementado pelo desenvolvedor.

Deve conter funções para CRUD da tabela endereco_estoque (hierarquia
corredor → modulo → nivel → vao) utilizando as funções do módulo
app.database.db (execute, fetch_one, fetch_all):
    - contar_total()           -> int
    - listar_todos()           -> list[sqlite3.Row]
    - buscar_por_id(id)        -> sqlite3.Row
    - criar(nome, tipo, parent_id) -> int (id)
    - desativar(id)            -> em_uso = 0
"""


class EnderecoEstoque:
    """Operações com a tabela endereco_estoque."""

    @staticmethod
    def contar_total() -> int:
        raise NotImplementedError

    @staticmethod
    def listar_todos():
        raise NotImplementedError

    @staticmethod
    def buscar_por_id(id: int):
        raise NotImplementedError

    @staticmethod
    def criar(nome: str, tipo: str, parent_id: int = None) -> int:
        raise NotImplementedError

    @staticmethod
    def desativar(id: int):
        raise NotImplementedError
