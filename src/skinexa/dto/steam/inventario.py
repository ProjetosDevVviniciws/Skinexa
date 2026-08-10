from dataclasses import dataclass
from typing import Any

from datetime import datetime
from decimal import Decimal

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
    
@dataclass(frozen=True, slots=True)
class ItemInventarioDTO:
    instancia_id: int
    item_catalogo_id: int

    asset_id: str

    nome_mercado: str
    nome_exibicao: str

    tipo_item: str
    nome_arma: str | None
    nome_acabamento: str | None
    estado_exterior: str | None

    raridade: str | None
    qualidade: str | None
    colecao: str | None

    url_icone: str | None
    url_icone_grande: str | None

    valor_float: Decimal | None

    stattrak: bool
    souvenir: bool
    trocavel: bool
    comercializavel: bool

    quantidade: int
    bloqueado_ate: datetime | None
    ultima_visualizacao_em: datetime

    @classmethod
    def criar_de_registro(
        cls,
        registro: dict[str, Any],
    ) -> "ItemInventarioDTO":
        return cls(
            instancia_id=int(registro["instancia_id"]),
            item_catalogo_id=int(
                registro["item_catalogo_id"]
            ),
            asset_id=registro["asset_id"],
            nome_mercado=registro["nome_mercado"],
            nome_exibicao=registro["nome_exibicao"],
            tipo_item=registro["tipo_item"],
            nome_arma=registro["nome_arma"],
            nome_acabamento=registro["nome_acabamento"],
            estado_exterior=registro["estado_exterior"],
            raridade=registro["raridade"],
            qualidade=registro["qualidade"],
            colecao=registro["colecao"],
            url_icone=registro["url_icone"],
            url_icone_grande=registro[
                "url_icone_grande"
            ],
            valor_float=registro["valor_float"],
            stattrak=bool(registro["stattrak"]),
            souvenir=bool(registro["souvenir"]),
            trocavel=bool(registro["trocavel"]),
            comercializavel=bool(
                registro["comercializavel"]
            ),
            quantidade=int(registro["quantidade"]),
            bloqueado_ate=registro["bloqueado_ate"],
            ultima_visualizacao_em=registro[
                "ultima_visualizacao_em"
            ],
        )