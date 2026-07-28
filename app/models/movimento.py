"""Modelo Movimento — a ser implementado pelo desenvolvedor.

Deve conter funções para operações na tabela movimento (entrada/saída/
transferência/ajuste) utilizando as funções do módulo app.database.db
(execute, fetch_one, fetch_all):
    - contar_total()                                                   -> int
    - listar_todos()                                                   -> list[sqlite3.Row]
    - buscar_por_id(id)                                                -> sqlite3.Row
    - criar(produto_id, qtd, tipo, origem_id, destino_id, usuario_id,
            observacao)                                                -> int (id)
"""


class Movimento:
    """Operações com a tabela movimento."""

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
    def criar(
        produto_id: int,
        quantidade: int,
        tipo_movimento: str,
        origem_id: int = None,
        destino_id: int = None,
        usuario_id: int = None,
        observacao: str = None,
    ) -> int:
        raise NotImplementedError
