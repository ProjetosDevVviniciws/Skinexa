from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class ItemCatalogoDTO:
    """Representa um item do catálogo interno do Skinexa."""

    id: int
    app_id: int

    nome_mercado: str
    nome_exibicao: str
    tipo_item: str

    nome_arma: str | None
    nome_acabamento: str | None
    estado_exterior: str | None

    raridade: str | None
    qualidade: str | None
    colecao: str | None
    descricao: str | None

    indice_pintura: int | None

    float_minimo: Decimal | None
    float_maximo: Decimal | None

    variante_stattrak: bool
    variante_souvenir: bool
    comercializavel: bool
    mercadoria_generica: bool

    steam_class_id: str | None
    steam_instance_id: str | None

    url_icone: str | None
    url_icone_grande: str | None

    tags: dict[str, Any] | list[Any] | None
    metadados_origem: dict[str, Any] | None