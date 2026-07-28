"""Modelo Produto — a ser implementado pelo desenvolvedor.

Deve conter funções para CRUD da tabela produto utilizando as funções
do módulo app.database.db (execute, fetch_one, fetch_all):
    - contar_total()           -> int
    - listar_todos()           -> list[sqlite3.Row]
    - buscar_por_id(id)        -> sqlite3.Row
    - criar(dados: dict)       -> int (id)
    - atualizar(id, dados)     -> UPDATE
    - deletar(id)              -> DELETE
"""


class Produto:
    """Operações com a tabela produto."""

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
    def criar(dados: dict) -> int:
        raise NotImplementedError

    @staticmethod
    def atualizar(id: int, dados: dict):
        raise NotImplementedError

    @staticmethod
    def deletar(id: int):
        raise NotImplementedError
