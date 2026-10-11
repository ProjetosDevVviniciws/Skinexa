from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class VarianteImportacaoCatalogoDTO:
    """Representa uma variante identificada por uma fonte externa."""

    app_id: int
    nome_mercado: str

    fonte: str
    id_externo: str

    skin_id_externo: str | None = None
    indice_pintura: int | None = None

    identificador_acabamento: str | None = None
    nome_variante: str | None = None

    url_imagem: str | None = None