#!/usr/bin/env python3
"""Script de preenchimento de dados de exemplo do TechStock para execução na raiz."""

import sys
import os

# Adiciona o diretório atual ao sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.seed import seed

if __name__ == "__main__":
    print("[TechStock] Inicializando e populando banco de dados com dados de teste...")
    seed()
    print("[TechStock] Concluído com sucesso! Usuários disponíveis:")
    print(" - Administrador: admin / admin123")
    print(" - Operador: pamela / admin123")
