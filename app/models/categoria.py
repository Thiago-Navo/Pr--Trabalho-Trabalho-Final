from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Categoria:
    id: int
    nome: str
    subcategoria: Optional[str] = None
    descritivo: Optional[str] = None
    ativo: bool = True
