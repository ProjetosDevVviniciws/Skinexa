from dataclasses import dataclass

from skinexa.dto.catalogo.importacao import (
    ItemImportacaoCatalogoDTO,
)

from skinexa.dto.catalogo.variante import (
    VarianteImportacaoCatalogoDTO,
)

@dataclass(frozen=True, slots=True)
class ErroItemCatalogoDTO:
    """Representa um registro rejeitado na normalização."""

    indice: int
    identificador_externo: str | None
    motivo: str

@dataclass(frozen=True, slots=True)
class RelatorioNormalizacaoCatalogoDTO:
    """Representa o resultado da normalização em lote."""

    total_recebidos: int
    total_normalizados: int
    total_rejeitados: int
    total_duplicados: int
    
    itens: tuple[ItemImportacaoCatalogoDTO, ...]
    erros: tuple[ErroItemCatalogoDTO, ...]
    
    motivos_rejeicao: dict[str, int]
    
    total_variantes_normalizadas: int = 0
    total_variantes_duplicadas: int = 0

    variantes: tuple[VarianteImportacaoCatalogoDTO, ...] = ()