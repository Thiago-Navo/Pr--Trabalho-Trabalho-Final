from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Usuario:
    id: int
    nome: str
    email: str
    celular: Optional[str] = None
    cargo: Optional[str] = None
    poder: int = 1
    senha_hash: str = ""
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None
    ativo: bool = True
    deletado_em: Optional[datetime] = None
