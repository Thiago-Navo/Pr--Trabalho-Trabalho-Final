"""Modelo Categoria — a ser implementado pelo desenvolvedor.

Deve conter funções para CRUD da tabela categoria utilizando as funções
do módulo app.database.db (execute, fetch_one, fetch_all):
    - contar_total()    -> int
    - listar_todos()    -> list[sqlite3.Row]
    - buscar_por_id(id) -> sqlite3.Row
    - criar(nome, subcategoria, descritivo) -> int (id)
    - atualizar(id, nome, subcategoria, descritivo)
    - deletar(id)       -> desativa o registro (ativo = 0)
"""


class Categoria:
    """Operações com a tabela categoria."""

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
    def criar(nome: str, subcategoria: str = None, descritivo: str = None) -> int:
        raise NotImplementedError

    @staticmethod
    def atualizar(id: int, nome: str = None, subcategoria: str = None, descritivo: str = None):
        raise NotImplementedError

    @staticmethod
    def deletar(id: int):
        raise NotImplementedError
