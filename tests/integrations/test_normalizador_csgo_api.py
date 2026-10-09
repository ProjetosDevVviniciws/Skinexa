"""Testes de normalização dos itens da CSGO-API."""

from copy import deepcopy

from decimal import Decimal

import pytest

from skinexa.integrations.catalogo.normalizador_csgo_api import (
    ErroNormalizacaoCSGOAPI,
    normalizar_item_skin_csgo_api,
)

@pytest.fixture
def registro_skin():
    """Representa um item real do conjunto de skins da CSGO-API."""

    return {
        "id": "skin-e757fd7191f9_0",
        "skin_id": "skin-e757fd7191f9",
        "market_hash_name": (
            "★ Hand Wraps | Spruce DDPAT (Factory New)"
        ),
        "name": (
            "★ Hand Wraps | Spruce DDPAT (Factory New)"
        ),
        "category": {
            "id": "sfui_invpanel_filter_gloves",
            "name": "Gloves",
        },
        "weapon": {
            "id": "leather_handwraps",
            "name": "Hand Wraps",
        },
        "pattern": {
            "id": "handwrap_camo_grey",
            "name": "Spruce DDPAT",
        },
        "wear": {
            "id": "SFUI_InvTooltip_Wear_Amount_0",
            "name": "Factory New",
        },
        "rarity": {
            "id": "rarity_ancient",
            "name": "Extraordinary",
        },
        "paint_index": "10010",
        "min_float": 0.06,
        "max_float": 0.8,
        "stattrak": False,
        "souvenir": False,
        "image": "https://example.com/skin.png",
        "description": "Hand wraps.",
    }

def test_normalizar_item_skin_valido(registro_skin):
    """Testa a normalização dos atributos de um item válido."""

    item = normalizar_item_skin_csgo_api(registro_skin)

    assert item.app_id == 730
    assert item.tipo_item == "luva"

    assert item.nome_mercado == (
        "★ Hand Wraps | Spruce DDPAT (Factory New)"
    )

    assert item.nome_arma == "Hand Wraps"
    assert item.nome_acabamento == "Spruce DDPAT"
    assert item.estado_exterior == "Factory New"
    assert item.raridade == "Extraordinary"

    assert item.indice_pintura == 10010

    assert item.float_minimo == Decimal("0.06")
    assert item.float_maximo == Decimal("0.8")

    assert item.variante_stattrak is False
    assert item.variante_souvenir is False

    assert item.metadados_origem == {
        "fonte": "csgo_api",
        "id_externo": "skin-e757fd7191f9_0",
        "skin_id": "skin-e757fd7191f9",
    }

def test_normalizar_item_skin_sem_nome_mercado(
    registro_skin,
):
    """Testa a rejeição de itens sem nome de mercado."""

    registro = deepcopy(registro_skin)
    registro.pop("market_hash_name")

    with pytest.raises(
        ErroNormalizacaoCSGOAPI,
        match="market_hash_name",
    ):
        normalizar_item_skin_csgo_api(registro)

def test_normalizar_item_skin_categoria_desconhecida(
    registro_skin,
):
    """Testa a rejeição de categorias não mapeadas."""

    registro = deepcopy(registro_skin)

    registro["category"] = {
        "id": "categoria_desconhecida",
        "name": "Unknown",
    }

    with pytest.raises(
        ErroNormalizacaoCSGOAPI,
        match="Categoria ainda não mapeada",
    ):
        normalizar_item_skin_csgo_api(registro)

def test_normalizar_item_skin_float_invalido(
    registro_skin,
):
    """Testa a rejeição de valores de float fora do intervalo permitido."""

    registro = deepcopy(registro_skin)
    registro["min_float"] = 1.5

    with pytest.raises(
        ErroNormalizacaoCSGOAPI,
        match="O float deve estar entre 0 e 1",
    ):
        normalizar_item_skin_csgo_api(registro)

def test_normalizar_item_skin_intervalo_float_invalido(
    registro_skin,
):
    """Testa a rejeição de intervalos de float inconsistentes."""

    registro = deepcopy(registro_skin)
    registro["min_float"] = 0.9
    registro["max_float"] = 0.1

    with pytest.raises(
        ErroNormalizacaoCSGOAPI,
        match="Intervalo de float inválido",
    ):
        normalizar_item_skin_csgo_api(registro)

def test_normalizar_item_skin_indice_pintura_invalido(
    registro_skin,
):
    """Testa a rejeição de índices de pintura inválidos."""

    registro = deepcopy(registro_skin)
    registro["paint_index"] = "invalido"

    with pytest.raises(
        ErroNormalizacaoCSGOAPI,
        match="Índice de pintura inválido",
    ):
        normalizar_item_skin_csgo_api(registro)

def test_normalizar_item_skin_stattrak_invalido(
    registro_skin,
):
    """Testa a rejeição de valores não booleanos para StatTrak."""

    registro = deepcopy(registro_skin)
    registro["stattrak"] = "false"

    with pytest.raises(
        ErroNormalizacaoCSGOAPI,
        match="O campo stattrak deve ser booleano",
    ):
        normalizar_item_skin_csgo_api(registro)

def test_normalizar_item_skin_preserva_registro_original(
    registro_skin,
):
    """Testa se a normalização preserva os dados originais da fonte."""

    registro_original = deepcopy(registro_skin)

    normalizar_item_skin_csgo_api(registro_skin)

    assert registro_skin == registro_original

@pytest.mark.parametrize(
    ("categoria_id", "tipo_esperado"),
    [
        (
            "csgo_inventory_weapon_category_pistols",
            "pistola",
        ),
        (
            "csgo_inventory_weapon_category_rifles",
            "rifle",
        ),
        (
            "csgo_inventory_weapon_category_smgs",
            "submetralhadora",
        ),
        (
            "csgo_inventory_weapon_category_heavy",
            "pesada",
        ),
        (
            "loadoutslot_equipment",
            "equipamento",
        ),
        (
            "sfui_invpanel_filter_gloves",
            "luva",
        ),
        (
            "sfui_invpanel_filter_melee",
            "faca",
        ),
    ],
)

def test_normalizar_item_skin_categorias_reais(
    registro_skin,
    categoria_id,
    tipo_esperado,
):
    """Testa o mapeamento das categorias reais da API."""

    registro = deepcopy(registro_skin)

    registro["category"] = {
        "id": categoria_id,
        "name": "Categoria de teste",
    }

    item = normalizar_item_skin_csgo_api(registro)

    assert item.tipo_item == tipo_esperado