"""Modelo LogAcesso — a ser implementado pelo desenvolvedor.

Deve conter funções para operações na tabela log_acesso (auditoria)
utilizando as funções do módulo app.database.db (execute, fetch_all):
    - listar_todos(limite=100) -> list[sqlite3.Row]
    - registrar(acao, entidade, entidade_id, usuario_id,
                dados_anteriores, dados_novos, ip, user_agent) -> int (id)
"""


class LogAcesso:
    """Operações com a tabela log_acesso."""

    @staticmethod
    def listar_todos(limite: int = 100):
        raise NotImplementedError

    @staticmethod
    def registrar(
        acao: str,
        entidade: str,
        entidade_id: int = None,
        usuario_id: int = None,
        dados_anteriores: str = None,
        dados_novos: str = None,
        ip: str = None,
        user_agent: str = None,
    ) -> int:
        raise NotImplementedError
