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

def criar_inventario_com_adesivos() -> InventarioSteamBruto:
    """Cria inventário Steam com adesivos aplicados."""

    return InventarioSteamBruto(
        steam_id=STEAM_ID_TESTE,
        app_id=730,
        contexto_id=2,
        total_informado=1,
        ativos=(
            {
                "appid": 730,
                "contextid": "2",
                "assetid": "52314340648",
                "classid": "242017550",
                "instanceid": "8583567976",
                "amount": "1",
            },
        ),
        descricoes=(
            {
                "appid": 730,
                "classid": "242017550",
                "instanceid": "8583567976",
                "market_hash_name": (
                    "M4A1-S | Nitro (Factory New)"
                ),
                "name": "M4A1-S | Nitro",
                "type": "Rifle (Restrito)",
                "tradable": 1,
                "marketable": 1,
                "commodity": 0,
                "icon_url": "imagem-m4a1-s",
                "tags": [
                    {
                        "category": "Weapon",
                        "localized_tag_name": "M4A1-S",
                    },
                    {
                        "category": "Exterior",
                        "localized_tag_name": (
                            "Nova de Fábrica"
                        ),
                    },
                    {
                        "category": "Rarity",
                        "localized_tag_name": "Restrito",
                    },
                ],
                "descriptions": [
                    {
                        "name": "exterior_wear",
                        "type": "html",
                        "value": (
                            "Exterior: Nova de Fábrica"
                        ),
                    },
                    {
                        "name": "sticker_info",
                        "type": "html",
                        "value": (
                            '<br><div id="sticker_info">'
                            "<center>"
                            '<img width="64" height="48" '
                            'src="https://cdn.steamstatic.com/'
                            'getright.png" '
                            'title="Adesivo: GeT_RiGhT | '
                            'Colônia 2015">'
                            '<img width="64" height="48" '
                            'src="https://cdn.steamstatic.com/'
                            'nip.png" '
                            'title="Adesivo: Ninjas in '
                            'Pyjamas | Colônia 2015">'
                            "<br>"
                            "Adesivo: GeT_RiGhT | "
                            "Colônia 2015, "
                            "Ninjas in Pyjamas | "
                            "Colônia 2015"
                            "</center>"
                            "</div>"
                        ),
                    },
                ],
                "actions": [
                    {
                        "link": (
                            "steam://run/730//"
                            "+csgo_econ_action_preview%20"
                            "%propid:6%"
                        ),
                        "name": "Inspecionar no jogo...",
                    },
                ],
            },
        ),
    )

def test_normalizar_adesivos_do_inventario():
    """Testa a normalização de adesivos aplicados ao item."""

    inventario = criar_inventario_com_adesivos()

    resultado = normalizar_inventario_steam(
        inventario
    )

    assert len(resultado) == 1

    item = resultado[0]

    assert item.catalogo.nome_mercado == (
        "M4A1-S | Nitro (Factory New)"
    )

    assert len(item.acessorios) == 2

    primeiro = item.acessorios[0]

    assert primeiro.tipo_acessorio == "adesivo"
    assert primeiro.nome_exibicao == (
        "GeT_RiGhT | Colônia 2015"
    )
    assert primeiro.url_icone == (
        "https://cdn.steamstatic.com/getright.png"
    )
    assert primeiro.posicao == 0
    assert primeiro.desgaste is None
    assert primeiro.fonte_dados == "steam"

    segundo = item.acessorios[1]

    assert segundo.tipo_acessorio == "adesivo"
    assert segundo.nome_exibicao == (
        "Ninjas in Pyjamas | Colônia 2015"
    )
    assert segundo.url_icone == (
        "https://cdn.steamstatic.com/nip.png"
    )
    assert segundo.posicao == 1
    assert segundo.desgaste is None
    assert segundo.fonte_dados == "steam"
    assert primeiro.identificador_externo is None
    assert primeiro.nome_mercado is None
    assert primeiro.variante is None
    assert primeiro.torneio is None
    assert primeiro.equipe is None
    assert primeiro.jogador is None
    assert primeiro.raridade is None

    assert primeiro.desgaste is None
    assert primeiro.rotacao is None
    assert primeiro.escala is None
    assert primeiro.deslocamento_x is None
    assert primeiro.deslocamento_y is None

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
    assert item.acessorios == ()   
    
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