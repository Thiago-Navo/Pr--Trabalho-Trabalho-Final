"""Modelo Usuario — a ser implementado pelo desenvolvedor.

Deve conter funções para CRUD da tabela usuario utilizando as funções
do módulo app.database.db (execute, fetch_one, fetch_all):
    - contar_total()              -> int
    - listar_todos()              -> list[sqlite3.Row]
    - buscar_por_id(id)           -> sqlite3.Row
    - buscar_por_email(email)     -> sqlite3.Row (usado no login)
    - criar(nome, email, senha_hash, cargo, celular) -> int (id)
    - atualizar(id, dados)        -> UPDATE
    - deletar(id)                 ->  delete sem apagar do banco so adicionando o horario deletado que via filtrar na listagem padrão (deletado_em, ativo = 0)
"""


class Usuario:
    """Operações com a tabela usuario."""

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
    def buscar_por_email(email: str):
        raise NotImplementedError

    @staticmethod
    def criar(nome: str, email: str, senha_hash: str, cargo: str = None, celular: str = None) -> int:
        raise NotImplementedError

    @staticmethod
    def atualizar(id: int, dados: dict):
        raise NotImplementedError

    @staticmethod
    def deletar(id: int):
        raise NotImplementedError
