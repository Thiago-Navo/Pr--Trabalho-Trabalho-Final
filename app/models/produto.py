from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class Produto:
    """Modelo de domínio para Produto com regras de negócio e validação."""

    id: Optional[int]
    nome: str
    sku: str
    preco: int = 0  # Preço em centavos inteiros (ex.: 1990 = R$ 19,90)
    categoria: Optional[str] = None
    categoria_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    drive_id: Optional[int] = None
    quantidade: int = 0
    estoque_min: int = 0
    estoque_max: int = 100
    quantidade_minima: int = 0
    descricao: Optional[str] = None
    criado_em: Optional[str] = None
    atualizado_em: Optional[str] = None

    def validar(self) -> None:
        """Aplica validações de negócio ao produto com proteção contra overflow e sobrecarga."""
        if not self.nome or len(self.nome.strip()) < 2:
            raise ValueError("O nome do produto deve ter ao menos 2 caracteres.")
        if len(self.nome) > 150:
            raise ValueError("O nome do produto não pode exceder 150 caracteres.")
        if not self.sku or len(self.sku.strip()) < 2:
            raise ValueError("O SKU do produto é obrigatório e deve ter ao menos 2 caracteres.")
        if len(self.sku) > 50:
            raise ValueError("O SKU do produto não pode exceder 50 caracteres.")
        if self.categoria and len(self.categoria) > 80:
            raise ValueError("A categoria do produto não pode exceder 80 caracteres.")

        # Proteção contra Integer Overflow em 64-bit SQLite
        LIMITE_MAX_UNIDADES = 1_000_000_000
        if self.quantidade > LIMITE_MAX_UNIDADES or self.estoque_max > LIMITE_MAX_UNIDADES or self.estoque_min > LIMITE_MAX_UNIDADES:
            raise ValueError("Os valores de quantidade e limites de estoque não podem exceder 1.000.000.000 unidades.")
        if self.preco > 1_000_000_000_00:
            raise ValueError("O preço do produto excede o limite operacional permitido.")

        if self.estoque_min < 0:
            raise ValueError("O estoque mínimo não pode ser negativo.")
        if self.estoque_max <= 0:
            raise ValueError("O estoque máximo deve ser maior que zero.")
        if self.estoque_max < self.estoque_min:
            raise ValueError("O estoque máximo não pode ser menor que o estoque mínimo.")
        if self.quantidade < 0:
            raise ValueError("A quantidade não pode ser negativa.")
        if self.quantidade > self.estoque_max:
            raise ValueError("A quantidade inicial não pode exceder a capacidade máxima do estoque configurada.")
        if self.preco < 0:
            raise ValueError("O preço não pode ser negativo.")

    def calcular_status_estoque(self, saldo_atual: int) -> str:
        """Determina o status de saúde do estoque baseado nos limites configurados."""
        if saldo_atual <= self.estoque_min:
            return "CRITICO"
        if saldo_atual <= self.estoque_min * 1.5:
            return "ATENCAO"
        return "OK"

    def esta_em_ponto_de_pedido(self, saldo_atual: int) -> bool:
        """Retorna True se o item precisa de reposição emergencial."""
        return saldo_atual <= self.estoque_min

    @property
    def preco_reais(self) -> float:
        """Converte centavos para valor decimal em reais."""
        return (self.preco or 0) / 100.0

    @property
    def preco_formatado(self) -> str:
        """Formata o preço em padrão brasileiro (R$ 0,00)."""
        return f"R$ {self.preco_reais:.2f}".replace(".", ",")

    def to_dict(self) -> dict[str, Any]:
        """Serializa o produto para formato compatível com API JSON."""
        return {
            "id": self.id,
            "nome": self.nome,
            "sku": self.sku,
            "preco": self.preco,
            "preco_reais": self.preco_reais,
            "preco_formatado": self.preco_formatado,
            "categoria": self.categoria,
            "categoria_id": self.categoria_id,
            "fornecedor_id": self.fornecedor_id,
            "drive_id": self.drive_id,
            "quantidade": self.quantidade,
            "estoque_min": self.estoque_min,
            "estoque_max": self.estoque_max,
            "descricao": self.descricao,
            "criado_em": self.criado_em,
            "atualizado_em": self.atualizado_em,
        }

    @classmethod
    def from_row(cls, row: Any) -> Produto:
        """Cria uma instância de Produto a partir de um sqlite3.Row ou dicionário."""
        r = dict(row)
        return cls(
            id=r.get("id"),
            nome=r.get("nome", ""),
            sku=r.get("sku", ""),
            preco=r.get("preco", 0) or 0,
            categoria=r.get("categoria"),
            categoria_id=r.get("categoria_id"),
            fornecedor_id=r.get("fornecedor_id"),
            drive_id=r.get("drive_id"),
            quantidade=r.get("quantidade", 0) or 0,
            estoque_min=r.get("estoque_min", 0) or 0,
            estoque_max=r.get("estoque_max", 100) or 100,
            quantidade_minima=r.get("quantidade_minima", 0) or 0,
            descricao=r.get("descricao"),
            criado_em=str(r.get("criado_em", "")) if r.get("criado_em") else None,
            atualizado_em=str(r.get("atualizado_em", "")) if r.get("atualizado_em") else None,
        )
