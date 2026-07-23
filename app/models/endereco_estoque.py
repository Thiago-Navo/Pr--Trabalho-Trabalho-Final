from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class EnderecoEstoque:
    id: int
    nome: str
    tipo: str  # 'corredor', 'modulo', 'nivel', 'vao'
    parent_id: Optional[int] = None
    caminho: str = ""
    em_uso: bool = True
