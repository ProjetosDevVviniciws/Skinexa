from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True, slots=True)
class ItemCatalogoSteamDTO:
    """Representa um tipo genérico de item recebido da Steam."""

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
    float_minimo: float | None
    float_maximo: float | None

    variante_stattrak: bool
    variante_souvenir: bool
    comercializavel: bool
    trocavel: bool
    mercadoria_generica: bool

    steam_class_id: str
    steam_instance_id: str

    url_icone: str | None
    url_icone_grande: str | None

    tags: tuple[dict[str, Any], ...]
    metadados_origem: dict[str, Any]

@dataclass(frozen=True, slots=True)
class InstanciaItemSteamDTO:
    """Representa uma ocorrência específica no inventário do usuário."""

    steam_id_usuario: str

    app_id: int
    contexto_id: str
    asset_id: str
    class_id: str
    instance_id: str

    quantidade: int

    indice_definicao: int | None
    indice_pintura: int | None
    semente_pintura: int | None
    valor_float: float | None

    nome_personalizado: str | None
    link_inspecao: str | None

    stattrak: bool
    contador_stattrak: int | None
    souvenir: bool

    trocavel: bool
    comercializavel: bool
    bloqueado_ate: str | None

    fonte_dados: str
    metadados_origem: dict[str, Any]

@dataclass(frozen=True, slots=True)
class ItemInventarioSteamDTO:
    """
    Agrupa o cadastro genérico e a instância específica.

    Essa estrutura facilita a sincronização posterior com as tabelas
    itens_catalogo e instancias_itens.
    """

    catalogo: ItemCatalogoSteamDTO
    instancia: InstanciaItemSteamDTO