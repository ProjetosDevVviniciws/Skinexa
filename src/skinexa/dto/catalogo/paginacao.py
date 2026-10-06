from dataclasses import dataclass

from skinexa.dto.catalogo.item import (
    ItemCatalogoDTO,
)

@dataclass(frozen=True, slots=True)
class PaginaItensCatalogoDTO:
    """Representa uma página de itens do catálogo."""

    itens: list[ItemCatalogoDTO]
    pagina: int
    por_pagina: int
    total_itens: int
    total_paginas: int
    tem_anterior: bool
    tem_proxima: bool