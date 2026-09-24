from __future__ import annotations
import math
from typing import List, Any, Optional

class Paginacao:
    """Classe utilitária para controle de paginação de consultas com cálculo inteligente de páginas."""

    def __init__(self, itens: List[Any], pagina: int, por_pagina: int, total_itens: int):
        self.itens = itens
        self.por_pagina = max(1, por_pagina)
        self.total_itens = max(0, total_itens)
        self.total_paginas = max(1, math.ceil(self.total_itens / self.por_pagina)) if self.total_itens > 0 else 1
        self.pagina = max(1, min(pagina, self.total_paginas))

        self.tem_anterior = self.pagina > 1
        self.tem_proximo = self.pagina < self.total_paginas
        self.pagina_anterior = self.pagina - 1 if self.tem_anterior else None
        self.proxima_pagina = self.pagina + 1 if self.tem_proximo else None

    @property
    def inicio_registro(self) -> int:
        if self.total_itens == 0:
            return 0
        return (self.pagina - 1) * self.por_pagina + 1

    @property
    def fim_registro(self) -> int:
        if self.total_itens == 0:
            return 0
        return min(self.pagina * self.por_pagina, self.total_itens)

    @property
    def range_paginas(self) -> List[Any]:
        """Gera sequência inteligente de números com elipses '...' quando houver muitas páginas."""
        if self.total_paginas <= 7:
            return list(range(1, self.total_paginas + 1))

        paginas = {1, self.total_paginas}
        for p in range(max(1, self.pagina - 2), min(self.total_paginas + 1, self.pagina + 3)):
            paginas.add(p)

        ordenadas = sorted(list(paginas))
        resultado = []
        for i, num in enumerate(ordenadas):
            if i > 0 and num > ordenadas[i - 1] + 1:
                resultado.append("...")
            resultado.append(num)
        return resultado
