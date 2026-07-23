from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Movimento:
    id: int
    produto_id: int
    quantidade: int
    tipo_movimento: str  # 'entrada', 'saida', 'transferencia', 'ajuste'
    origem_id: Optional[int] = None
    destino_id: Optional[int] = None
    usuario_id: Optional[int] = None
    observacao: Optional[str] = None
    criado_em: Optional[datetime] = None
