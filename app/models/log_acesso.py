from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class LogAcesso:
    id: int
    acao: str
    entidade: str
    entidade_id: Optional[int] = None
    usuario_id: Optional[int] = None
    dados_anteriores: Optional[str] = None
    dados_novos: Optional[str] = None
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    criado_em: Optional[datetime] = None
