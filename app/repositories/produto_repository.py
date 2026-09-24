from __future__ import annotations

import logging
from typing import Optional, List, Dict, Any
from app.database import database
from app.models.produto import Produto

logger = logging.getLogger("techstock.repository")


class ProdutoRepository:
    """Repository Pattern para abstração e centralização das operações de banco de Produtos."""

    def __init__(self, conn=None):
        self._conn = conn

    @property
    def conn(self):
        return self._conn if self._conn is not None else database.get_connection()

    def listar_todos(self, categoria: Optional[str] = None, busca: Optional[str] = None) -> List[Produto]:
        """Retorna todos os produtos filtrados por categoria ou termo de busca."""
        query = "SELECT * FROM produtos WHERE 1=1"
        params: List[Any] = []

        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if busca:
            termo = f"%{busca.strip()}%"
            query += " AND (nome LIKE ? OR sku LIKE ? OR categoria LIKE ?)"
            params.extend([termo, termo, termo])

        query += " ORDER BY nome ASC"
        rows = self.conn.execute(query, params).fetchall()
        return [Produto.from_row(r) for r in rows]

    def buscar_por_id(self, produto_id: int) -> Optional[Produto]:
        """Localiza um produto pelo seu identificador primário."""
        row = self.conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        return Produto.from_row(row) if row else None

    def buscar_por_sku(self, sku: str) -> Optional[Produto]:
        """Localiza um produto pelo SKU único."""
        row = self.conn.execute("SELECT * FROM produtos WHERE LOWER(sku) = LOWER(?)", (sku.strip(),)).fetchone()
        return Produto.from_row(row) if row else None

    def obter_saldos_detalhados(self) -> List[Dict[str, Any]]:
        """Retorna produtos acompanhados da soma real de estoque em todas as ruas."""
        linhas = self.conn.execute("""
            SELECT p.*,
                   COALESCE(SUM(e.quantidade), 0) AS qtd_total
            FROM produtos p
            LEFT JOIN estoque e ON e.produto_id = p.id
            GROUP BY p.id
            ORDER BY p.nome ASC
        """).fetchall()

        resultado = []
        for row in linhas:
            prod = Produto.from_row(row)
            qtd_total = row["qtd_total"]
            resultado.append({
                "produto": prod,
                "qtd_total": qtd_total,
                "status": prod.calcular_status_estoque(qtd_total),
                "em_ponto_de_pedido": prod.esta_em_ponto_de_pedido(qtd_total),
            })
        return resultado

    def salvar(self, produto: Produto, rua_id: Optional[int] = None, qtd_inicial: int = 0) -> int:
        """Valida e persiste um novo produto no banco, criando saldo inicial na rua se fornecida."""
        produto.validar()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO produtos (
                nome, sku, preco, categoria, categoria_id, fornecedor_id, drive_id,
                quantidade, estoque_min, estoque_max, quantidade_minima, descricao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            produto.nome,
            produto.sku,
            produto.preco,
            produto.categoria,
            produto.categoria_id,
            produto.fornecedor_id,
            produto.drive_id,
            qtd_inicial,
            produto.estoque_min,
            produto.estoque_max,
            produto.estoque_min,
            produto.descricao,
        ))
        novo_id = cursor.lastrowid

        if rua_id and qtd_inicial > 0:
            cursor.execute(
                "INSERT INTO estoque (produto_id, rua_id, quantidade) VALUES (?, ?, ?)",
                (novo_id, rua_id, qtd_inicial)
            )
            cursor.execute("""
                INSERT INTO entradas (produto_id, rua_id, quantidade, tipo, usuario_id)
                VALUES (?, ?, ?, 'novo_produto', 1)
            """, (novo_id, rua_id, qtd_inicial))

        self.conn.commit()
        logger.info(f"Produto '{produto.nome}' (ID {novo_id}) cadastrado via ProdutoRepository.")
        return novo_id

    def atualizar_limites(self, produto_id: int, estoque_min: int, estoque_max: int) -> bool:
        """Atualiza estoques mínimo e máximo com validação."""
        if estoque_min < 0 or estoque_max < estoque_min:
            raise ValueError("Limites de estoque inválidos.")

        res = self.conn.execute("""
            UPDATE produtos
            SET estoque_min = ?, estoque_max = ?, atualizado_em = datetime('now')
            WHERE id = ?
        """, (estoque_min, estoque_max, produto_id))
        self.conn.commit()
        return res.rowcount > 0

    def excluir(self, produto_id: int) -> bool:
        """Exclui produto e registros relacionados em cascata."""
        res = self.conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        self.conn.commit()
        logger.info(f"Produto ID {produto_id} excluído via ProdutoRepository.")
        return res.rowcount > 0
