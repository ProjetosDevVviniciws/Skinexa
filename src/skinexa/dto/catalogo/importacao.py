from dataclasses import dataclass

from decimal import Decimal

from typing import Any

@dataclass(frozen=True, slots=True)
class ItemImportacaoCatalogoDTO:
    """Representa um item normalizado de uma fonte externa."""

    app_id: int
    nome_mercado: str
    nome_exibicao: str
    tipo_item: str

    nome_arma: str | None = None
    nome_acabamento: str | None = None
    estado_exterior: str | None = None
    raridade: str | None = None
    qualidade: str | None = None
    colecao: str | None = None
    descricao: str | None = None

    indice_pintura: int | None = None
    float_minimo: Decimal | None = None
    float_maximo: Decimal | None = None

    variante_stattrak: bool = False
    variante_souvenir: bool = False

    comercializavel: bool = False
    mercadoria_generica: bool = False

    steam_class_id: str | None = None
    steam_instance_id: str | None = None

    url_icone: str | None = None
    url_icone_grande: str | None = None

    tags: dict[str, Any] | list[Any] | None = None
    metadados_origem: dict[str, Any] | None = None