from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EstoqueLocal:
    id: int
    produto_id: int
    endereco_estoque_id: int
    quantidade: int = 0
