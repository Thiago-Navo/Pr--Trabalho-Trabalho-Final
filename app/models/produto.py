from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Produto:
    id: int
    nome: str
    descricao: Optional[str] = None
    altura: Optional[float] = None
    largura: Optional[float] = None
    peso: Optional[float] = None
    cor_predominante: Optional[str] = None
    qtd_min: int = 0
    qtd_max: Optional[int] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    categoria_id: Optional[int] = None
    fabricante_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
