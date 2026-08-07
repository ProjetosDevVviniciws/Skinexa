# Consulta e normaliza o inventário do usuário da Steam

from dataclasses import dataclass
from typing import Any

import requests
from flask import current_app

APP_ID_CS2 = 730
CONTEXTO_INVENTARIO_CS2 = 2
LIMITE_ITENS_POR_PAGINA = 2000
LIMITE_MAXIMO_PAGINAS = 20

class ErroInventarioSteam(RuntimeError):
    """Erro genérico durante a consulta do inventário Steam."""

class InventarioSteamPrivado(ErroInventarioSteam):
    """O inventário não está disponível publicamente."""

class InventarioSteamIndisponivel(ErroInventarioSteam):
    """O serviço de inventário da Steam está indisponível."""

class LimiteSteamExcedido(ErroInventarioSteam):
    """A Steam limitou temporariamente as requisições."""

class RespostaInventarioInvalida(ErroInventarioSteam):
    """A Steam retornou uma resposta inesperada."""

@dataclass(frozen=True, slots=True)
class InventarioSteamBruto:
    """Resultado bruto consolidado da consulta do inventário."""

    steam_id: str
    app_id: int
    contexto_id: int
    total_informado: int | None
    ativos: tuple[dict[str, Any], ...]
    descricoes: tuple[dict[str, Any], ...]

def buscar_inventario_publico(
    steam_id: str,
    *,
    app_id: int = APP_ID_CS2,
    contexto_id: int = CONTEXTO_INVENTARIO_CS2,
) -> InventarioSteamBruto:
    """
    Consulta todas as páginas do inventário público do usuário.

    A função apenas valida e consolida o JSON bruto. A normalização
    dos itens será realizada por outra camada.
    """

    _validar_steam_id(steam_id)

    ativos: list[dict[str, Any]] = []
    descricoes: list[dict[str, Any]] = []

    proximo_asset_id: str | None = None
    total_informado: int | None = None
    paginas_consultadas = 0

    while True:
        paginas_consultadas += 1

        if paginas_consultadas > LIMITE_MAXIMO_PAGINAS:
            raise RespostaInventarioInvalida(
                "O inventário ultrapassou o limite de páginas "
                "permitido para uma única consulta."
            )

        pagina = _buscar_pagina_inventario(
            steam_id=steam_id,
            app_id=app_id,
            contexto_id=contexto_id,
            asset_id_inicial=proximo_asset_id,
        )

        ativos.extend(pagina.get("assets", []))
        descricoes.extend(pagina.get("descriptions", []))

        if total_informado is None:
            total = pagina.get("total_inventory_count")

            if isinstance(total, int) and total >= 0:
                total_informado = total

        possui_mais_itens = pagina.get("more_items") is True

        if not possui_mais_itens:
            break

        ultimo_asset_id = pagina.get("last_assetid")

        if not isinstance(ultimo_asset_id, str):
            ultimo_asset_id = str(ultimo_asset_id or "")

        if not ultimo_asset_id:
            raise RespostaInventarioInvalida(
                "A Steam informou que existem mais itens, "
                "mas não retornou last_assetid."
            )

        if ultimo_asset_id == proximo_asset_id:
            raise RespostaInventarioInvalida(
                "A paginação do inventário não avançou."
            )

        proximo_asset_id = ultimo_asset_id

    return InventarioSteamBruto(
        steam_id=steam_id,
        app_id=app_id,
        contexto_id=contexto_id,
        total_informado=total_informado,
        ativos=tuple(ativos),
        descricoes=tuple(descricoes),
    )

def _buscar_pagina_inventario(
    *,
    steam_id: str,
    app_id: int,
    contexto_id: int,
    asset_id_inicial: str | None,
) -> dict[str, Any]:
    """Consulta e valida uma página do inventário."""

    url = (
        "https://steamcommunity.com/inventory/"
        f"{steam_id}/{app_id}/{contexto_id}"
    )

    parametros: dict[str, str | int] = {
        "l": "brazilian",
        "count": LIMITE_ITENS_POR_PAGINA,
    }

    if asset_id_inicial:
        parametros["start_assetid"] = asset_id_inicial

    timeout = current_app.config.get(
        "STEAM_REQUEST_TIMEOUT",
        10,
    )

    try:
        resposta = requests.get(
            url,
            params=parametros,
            timeout=timeout,
            headers={
                "Accept": "application/json",
                "User-Agent": "Skinexa/1.0",
            },
        )
    except requests.Timeout as erro:
        raise InventarioSteamIndisponivel(
            "A consulta do inventário excedeu o tempo limite."
        ) from erro
    except requests.RequestException as erro:
        raise InventarioSteamIndisponivel(
            "Não foi possível consultar o inventário Steam."
        ) from erro

    if resposta.status_code in {401, 403}:
        raise InventarioSteamPrivado(
            "O inventário do usuário não está público."
        )

    if resposta.status_code == 429:
        raise LimiteSteamExcedido(
            "A Steam limitou temporariamente as consultas."
        )

    if resposta.status_code >= 500:
        raise InventarioSteamIndisponivel(
            "O serviço de inventário da Steam está indisponível."
        )

    try:
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.RequestException as erro:
        raise ErroInventarioSteam(
            "A Steam rejeitou a consulta do inventário."
        ) from erro
    except ValueError as erro:
        raise RespostaInventarioInvalida(
            "A Steam não retornou um JSON válido."
        ) from erro

    return _validar_pagina(dados)

def _validar_pagina(
    dados: Any,
) -> dict[str, Any]:
    """Valida a estrutura mínima esperada em uma página."""

    if not isinstance(dados, dict):
        raise RespostaInventarioInvalida(
            "A resposta do inventário não é um objeto JSON."
        )

    if dados.get("success") not in {1, True}:
        raise RespostaInventarioInvalida(
            "A Steam não confirmou o sucesso da consulta."
        )

    ativos = dados.get("assets", [])
    descricoes = dados.get("descriptions", [])

    if not isinstance(ativos, list):
        raise RespostaInventarioInvalida(
            "O campo assets possui formato inválido."
        )

    if not isinstance(descricoes, list):
        raise RespostaInventarioInvalida(
            "O campo descriptions possui formato inválido."
        )

    if not all(isinstance(item, dict) for item in ativos):
        raise RespostaInventarioInvalida(
            "A lista assets contém um item inválido."
        )

    if not all(
        isinstance(descricao, dict)
        for descricao in descricoes
    ):
        raise RespostaInventarioInvalida(
            "A lista descriptions contém um item inválido."
        )

    return dados

def _validar_steam_id(steam_id: str) -> None:
    """Valida o formato básico de um SteamID de 64 bits."""

    if not steam_id.isdigit() or len(steam_id) != 17:
        raise ValueError(
            "O SteamID deve possuir exatamente 17 dígitos."
        )