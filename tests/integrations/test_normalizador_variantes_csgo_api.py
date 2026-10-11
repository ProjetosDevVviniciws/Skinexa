from copy import deepcopy

import pytest

from skinexa.integrations.catalogo.normalizador_csgo_api import (
    ErroNormalizacaoCSGOAPI,
)

from skinexa.integrations.catalogo.normalizador_variantes_csgo_api import (
    normalizar_variante_skin_csgo_api,
)

@pytest.fixture
def registro_variante():
    """Representa uma variante Doppler da CSGO-API."""

    return {
        "id": "skin-85646e9ca45c_0",
        "skin_id": "skin-85646e9ca45c",
        "market_hash_name": (
            "★ Bayonet | Doppler (Factory New)"
        ),
        "name": (
            "★ Bayonet | Doppler (Factory New)"
        ),
        "category": {
            "id": "sfui_invpanel_filter_melee",
            "name": "Knives",
        },
        "weapon": {
            "id": "weapon_bayonet",
            "name": "Bayonet",
        },
        "pattern": {
            "id": "am_doppler_phase2",
            "name": "Doppler",
        },
        "wear": {
            "name": "Factory New",
        },
        "paint_index": "419",
        "min_float": 0,
        "max_float": 0.08,
        "stattrak": False,
        "souvenir": False,
        "image": "https://example.com/bayonet.png",
        "original": {
            "name": "weapon_bayonet",
            "image_inventory": (
                "econ/default_generated/"
                "weapon_bayonet_am_doppler_phase2_light"
            ),
        },
    }

def test_normaliza_variante_doppler_phase2(
    registro_variante,
):
    """Verifica a normalização dos atributos de uma Doppler Phase 2."""

    variante = normalizar_variante_skin_csgo_api(
        registro_variante
    )

    assert variante.app_id == 730
    assert variante.nome_variante == "Phase 2"
    assert variante.indice_pintura == 419
    assert variante.identificador_acabamento == (
        "am_doppler_phase2"
    )
    assert variante.fonte == "csgo_api"

@pytest.mark.parametrize(
    ("identificador", "nome_esperado"),
    [
        ("am_ruby_marbleized", "Ruby"),
        ("am_sapphire_marbleized", "Sapphire"),
        ("am_blackpearl_marbleized", "Black Pearl"),
        ("am_doppler_phase1", "Phase 1"),
        ("am_doppler_phase2", "Phase 2"),
        ("am_doppler_phase3", "Phase 3"),
        ("am_doppler_phase4", "Phase 4"),
    ],
)

def test_reconhece_variantes_conhecidas(
    registro_variante,
    identificador,
    nome_esperado,
):
    """Verifica o reconhecimento dos nomes das variantes conhecidas."""

    registro_variante["original"]["image_inventory"] = (
        "econ/default_generated/"
        f"weapon_bayonet_{identificador}_light"
    )

    variante = normalizar_variante_skin_csgo_api(
        registro_variante
    )

    assert variante.nome_variante == nome_esperado

def test_variante_desconhecida_nao_inventa_nome(
    registro_variante,
):
    """Verifica que acabamentos desconhecidos não recebem nomes inventados."""

    registro_variante["original"]["image_inventory"] = (
        "econ/default_generated/"
        "weapon_bayonet_acabamento_desconhecido_light"
    )

    variante = normalizar_variante_skin_csgo_api(
        registro_variante
    )

    assert variante.nome_variante is None
    assert variante.identificador_acabamento is None

def test_rejeita_variante_sem_id(
    registro_variante,
):
    """Verifica a rejeição de variantes sem identificador externo."""

    registro_variante.pop("id")

    with pytest.raises(
        ErroNormalizacaoCSGOAPI,
        match="identificador externo",
    ):
        normalizar_variante_skin_csgo_api(
            registro_variante
        )

def test_rejeita_id_externo_muito_longo(
    registro_variante,
):
    """Verifica a rejeição de IDs externos acima do limite permitido."""

    registro_variante["id"] = "x" * 101

    with pytest.raises(
        ErroNormalizacaoCSGOAPI,
        match="excede 100",
    ):
        normalizar_variante_skin_csgo_api(
            registro_variante
        )

def test_aceita_variante_sem_paint_index(
    registro_variante,
):
    """Verifica a aceitação de variantes sem índice de pintura."""

    registro_variante["paint_index"] = None

    variante = normalizar_variante_skin_csgo_api(
        registro_variante
    )

    assert variante.indice_pintura is None

def test_nao_modifica_registro_original(
    registro_variante,
):
    """Verifica se a normalização preserva o registro de entrada."""

    original = deepcopy(registro_variante)

    normalizar_variante_skin_csgo_api(
        registro_variante
    )

    assert registro_variante == original