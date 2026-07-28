"""Modelo EstoqueLocal — a ser implementado pelo desenvolvedor.

Deve conter funções para operações na tabela estoque_local (produto x endereço)
utilizando as funções do módulo app.database.db (execute, fetch_one, fetch_all):
    - contar_total()                              -> int
    - listar_todos()                              -> list[sqlite3.Row]
    - buscar_por_id(id)                           -> sqlite3.Row
    - criar(produto_id, endereco_estoque_id, qtd) -> int (id)
    - atualizar_quantidade(id, quantidade)
"""


class EstoqueLocal:
    """Operações com a tabela estoque_local."""

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
    def criar(produto_id: int, endereco_estoque_id: int, quantidade: int = 0) -> int:
        raise NotImplementedError

    @staticmethod
    def atualizar_quantidade(id: int, quantidade: int):
        raise NotImplementedError
