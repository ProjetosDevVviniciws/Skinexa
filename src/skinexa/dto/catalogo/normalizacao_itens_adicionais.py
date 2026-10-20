from dataclasses import dataclass

from skinexa.dto.catalogo.importacao import (
    ItemImportacaoCatalogoDTO,
)
from skinexa.dto.catalogo.variante import VarianteImportacaoCatalogoDTO

@dataclass(frozen=True, slots=True)
class RegistroPendenteCatalogoDTO:
    """Representa um registro sem identidade comercial conhecida."""

    categoria: str
    indice: int
    id_externo: str
    nome_exibicao: str

@dataclass(frozen=True, slots=True)
class ErroNormalizacaoItemAdicionalDTO:
    """Representa uma falha na normalização de um registro."""

    categoria: str
    indice: int
    id_externo: str | None
    motivo: str

@dataclass(frozen=True, slots=True)
class RelatorioItensAdicionaisDTO:
    """Consolida a normalização de uma categoria adicional."""

    categoria: str

    total_recebidos: int
    total_normalizados: int
    total_sem_identidade_comercial: int
    total_rejeitados: int
    total_duplicados: int

    itens: tuple[ItemImportacaoCatalogoDTO, ...]
    variantes: tuple[VarianteImportacaoCatalogoDTO, ...]
    
    pendentes: tuple[RegistroPendenteCatalogoDTO, ...]
    erros: tuple[ErroNormalizacaoItemAdicionalDTO, ...]
    
    motivos_rejeicao: dict[str, int]
    
    total_variantes_normalizadas: int = 0
    total_variantes_duplicadas: int = 0