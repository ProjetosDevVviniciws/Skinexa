import pytest

from skinexa.integrations.steam.normalizador_inventario import (
    ErroNormalizacaoInventarioSteam,
    InventarioSteamBruto,
    normalizar_inventario_steam,
)

STEAM_ID_TESTE = "76561198000000001"

def criar_inventario_teste() -> InventarioSteamBruto:
    return InventarioSteamBruto(
        steam_id=STEAM_ID_TESTE,
        app_id=730,
        contexto_id=2,
        total_informado=1,
        ativos=(
            {
                "appid": 730,
                "contextid": "2",
                "assetid": "1001",
                "classid": "2001",
                "instanceid": "0",
                "amount": "1",
            },
        ),
        descricoes=(
            {
                "appid": 730,
                "classid": "2001",
                "instanceid": "0",
                "market_hash_name": (
                    "AK-47 | Redline (Field-Tested)"
                ),
                "name": "AK-47 | Redline",
                "type": "Rifle",
                "tradable": 1,
                "marketable": 1,
                "commodity": 0,
                "icon_url": "imagem-pequena",
                "icon_url_large": "imagem-grande",
                "tags": [
                    {
                        "category": "Weapon",
                        "localized_tag_name": "AK-47",
                    },
                    {
                        "category": "Exterior",
                        "localized_tag_name": "Field-Tested",
                    },
                    {
                        "category": "Rarity",
                        "localized_tag_name": "Classified",
                    },
                    {
                        "category": "ItemSet",
                        "localized_tag_name": (
                            "The Phoenix Collection"
                        ),
                    },
                ],
                "actions": [
                    {
                        "link": (
                            "steam://rungame/730/"
                            "76561202255233023/+csgo_econ_action_preview "
                            "S%owner_steamid%A%assetid%D123"
                        )
                    }
                ],
            },
        ),
    )

def test_normalizar_item_do_inventario():
    """Teste que valida a normalização de um item do inventário da Steam."""
    inventario = criar_inventario_teste()

    resultado = normalizar_inventario_steam(
        inventario
    )

    assert len(resultado) == 1

    item = resultado[0]

    assert item.catalogo.nome_mercado == (
        "AK-47 | Redline (Field-Tested)"
    )
    assert item.catalogo.nome_arma == "AK-47"
    assert item.catalogo.nome_acabamento == "Redline"
    assert item.catalogo.estado_exterior == "Field-Tested"
    assert item.catalogo.raridade == "Classified"
    assert item.catalogo.colecao == (
        "The Phoenix Collection"
    )

    assert item.catalogo.comercializavel is True
    assert item.catalogo.trocavel is True

    assert item.instancia.asset_id == "1001"
    assert item.instancia.quantidade == 1
    assert item.instancia.valor_float is None

    assert STEAM_ID_TESTE in (
        item.instancia.link_inspecao or ""
    )
    assert "1001" in (
        item.instancia.link_inspecao or ""
    )

def test_rejeitar_asset_sem_descricao():
    """Teste que valida que um ativo sem descrição correspondente
    é rejeitado durante a normalização do inventário da Steam."""
    inventario = InventarioSteamBruto(
        steam_id=STEAM_ID_TESTE,
        app_id=730,
        contexto_id=2,
        total_informado=1,
        ativos=(
            {
                "assetid": "1001",
                "classid": "9999",
                "instanceid": "0",
                "amount": "1",
            },
        ),
        descricoes=(),
    )

    with pytest.raises(
        ErroNormalizacaoInventarioSteam
    ):
        normalizar_inventario_steam(inventario)

def test_rejeitar_asset_sem_asset_id():
    """Teste que valida que um ativo sem asset_id é rejeitado
    durante a normalização do inventário da Steam."""
    inventario = InventarioSteamBruto(
        steam_id=STEAM_ID_TESTE,
        app_id=730,
        contexto_id=2,
        total_informado=1,
        ativos=(
            {
                "classid": "2001",
                "instanceid": "0",
                "amount": "1",
            },
        ),
        descricoes=(
            {
                "classid": "2001",
                "instanceid": "0",
                "market_hash_name": "Item de Teste",
                "name": "Item de Teste",
            },
        ),
    )

    with pytest.raises(
        ErroNormalizacaoInventarioSteam
    ):
        normalizar_inventario_steam(inventario)