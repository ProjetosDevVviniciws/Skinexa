import responses

from skinexa.integrations.steam.inventario import (
    buscar_inventario_publico,
)

import pytest
import responses

from skinexa.integrations.steam.inventario import (
    InventarioSteamPrivado,
    buscar_inventario_publico,
)

from skinexa.integrations.steam.inventario import (
    LimiteSteamExcedido,
)

STEAM_ID_TESTE = "76561198000000001"

URL_INVENTARIO = (
    "https://steamcommunity.com/inventory/"
    f"{STEAM_ID_TESTE}/730/2"
)

@responses.activate
def test_buscar_inventario_de_uma_pagina(app):
    """Testa a função `buscar_inventario_publico` com uma página de inventário simulada."""
    responses.get(
        URL_INVENTARIO,
        json={
            "assets": [
                {
                    "appid": 730,
                    "contextid": "2",
                    "assetid": "1001",
                    "classid": "2001",
                    "instanceid": "0",
                    "amount": "1",
                }
            ],
            "descriptions": [
                {
                    "appid": 730,
                    "classid": "2001",
                    "instanceid": "0",
                    "market_hash_name": (
                        "Item de Teste (Field-Tested)"
                    ),
                    "name": "Item de Teste",
                    "tradable": 1,
                    "marketable": 1,
                }
            ],
            "total_inventory_count": 1,
            "success": 1,
            "more_items": False,
        },
        status=200,
    )

    with app.app_context():
        inventario = buscar_inventario_publico(
            STEAM_ID_TESTE
        )

    assert inventario.steam_id == STEAM_ID_TESTE
    assert inventario.app_id == 730
    assert inventario.contexto_id == 2
    assert inventario.total_informado == 1

    assert len(inventario.ativos) == 1
    assert len(inventario.descricoes) == 1

    assert inventario.ativos[0]["assetid"] == "1001"
    
@responses.activate
def test_buscar_inventario_com_paginacao(app):
    """Testa a função `buscar_inventario_publico` com uma página de inventário simulada que possui paginação."""
    responses.get(
        URL_INVENTARIO,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "l": "brazilian",
                    "count": "2000",
                }
            )
        ],
        json={
            "assets": [
                {
                    "appid": 730,
                    "contextid": "2",
                    "assetid": "1001",
                    "classid": "2001",
                    "instanceid": "0",
                    "amount": "1",
                }
            ],
            "descriptions": [],
            "total_inventory_count": 2,
            "success": 1,
            "more_items": True,
            "last_assetid": "1001",
        },
        status=200,
    )

    responses.get(
        URL_INVENTARIO,
        match=[
            responses.matchers.query_param_matcher(
                {
                    "l": "brazilian",
                    "count": "2000",
                    "start_assetid": "1001",
                }
            )
        ],
        json={
            "assets": [
                {
                    "appid": 730,
                    "contextid": "2",
                    "assetid": "1002",
                    "classid": "2002",
                    "instanceid": "0",
                    "amount": "1",
                }
            ],
            "descriptions": [],
            "total_inventory_count": 2,
            "success": 1,
            "more_items": False,
        },
        status=200,
    )

    with app.app_context():
        inventario = buscar_inventario_publico(
            STEAM_ID_TESTE
        )

    assert len(inventario.ativos) == 2
    assert inventario.total_informado == 2
    assert len(responses.calls) == 2 

@responses.activate
def test_rejeitar_inventario_privado(app):
    """Testa se a função `buscar_inventario_publico` lança a exceção correta quando o inventário é privado."""
    responses.get(
        URL_INVENTARIO,
        status=403,
    )

    with app.app_context():
        with pytest.raises(InventarioSteamPrivado):
            buscar_inventario_publico(STEAM_ID_TESTE)

@responses.activate
def test_identificar_limite_de_requisicoes(app):
    """Testa se a função `buscar_inventario_publico` lança a exceção correta quando o limite de requisições da Steam é excedido."""
    responses.get(
        URL_INVENTARIO,
        status=429,
    )

    with app.app_context():
        with pytest.raises(LimiteSteamExcedido):
            buscar_inventario_publico(STEAM_ID_TESTE)
            
def test_rejeitar_steam_id_invalido(app):
    """Testa se a função `buscar_inventario_publico` lança a exceção correta quando o Steam ID é inválido."""
    with app.app_context():
        with pytest.raises(ValueError):
            buscar_inventario_publico("123")