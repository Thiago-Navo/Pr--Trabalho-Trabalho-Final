from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Empresa:
    id: int
    tipo: str
    razao_social: str
    cnpj: Optional[str] = None
    nome_fantasia: Optional[str] = None
    tel_fixo: Optional[str] = None
    tel_celular: Optional[str] = None
    email: Optional[str] = None
    cep: Optional[str] = None
    estado: Optional[str] = None
    cidade: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    nacionalidade: Optional[str] = None
    site_fabric: Optional[str] = None
    usuario_id: Optional[int] = None
    ativo_online: bool = True
    dt_cadastro: Optional[datetime] = None
    dt_atualizado: Optional[datetime] = None
    dt_deletado: Optional[datetime] = None
