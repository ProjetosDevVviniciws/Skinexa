from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class SugestaoItemCatalogoDTO:
    """Representa uma sugestão de item do catálogo."""

    id: int
    nome_mercado: str
    nome_exibicao: str
    tipo_item: str
    url_icone: str | None