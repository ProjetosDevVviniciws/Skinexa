import pytest

from skinexa.integrations.catalogo.normalizador_variantes_itens_adicionais_csgo_api import (
    ErroNormalizacaoVarianteAdicionalCSGOAPI,
    normalizar_variante_item_adicional_csgo_api,
)

def test_normalizar_variante_adesivo():
    """Testa o identificador externo de um adesivo."""

    registro = {
        "id": "sticker-13",
        "name": "Sticker | Lucky 13",
        "market_hash_name": "Sticker | Lucky 13",
        "image": "https://exemplo.com/sticker.png",
    }

    variante = normalizar_variante_item_adicional_csgo_api(
        registro,
        categoria="adesivos",
    )

    assert variante.app_id == 730
    assert variante.nome_mercado == "Sticker | Lucky 13"
    assert variante.fonte == "csgo_api"
    assert variante.id_externo == "sticker-13"
    assert variante.url_imagem == "https://exemplo.com/sticker.png"

    assert variante.skin_id_externo is None
    assert variante.indice_pintura is None
    assert variante.identificador_acabamento is None
    assert variante.nome_variante is None

def test_normalizar_variante_caixa():
    """Testa o identificador externo de um contêiner."""

    registro = {
        "id": "crate-1210",
        "name": "Gift Package",
        "market_hash_name": "Gift Package",
        "image": "https://exemplo.com/caixa.png",
    }

    variante = normalizar_variante_item_adicional_csgo_api(
        registro,
        categoria="caixas",
    )

    assert variante.app_id == 730
    assert variante.nome_mercado == "Gift Package"
    assert variante.fonte == "csgo_api"
    assert variante.id_externo == "crate-1210"
    assert variante.url_imagem == "https://exemplo.com/caixa.png"
    assert variante.indice_pintura is None

def test_normalizar_variante_agente():
    """Testa o identificador externo de um agente."""

    registro = {
        "id": "agent-4613",
        "name": "Bloody Darryl The Strapped | The Professionals",
        "market_hash_name": (
            "Bloody Darryl The Strapped | The Professionals"
        ),
        "image": "https://exemplo.com/agente.png",
    }

    variante = normalizar_variante_item_adicional_csgo_api(
        registro,
        categoria="agentes",
    )

    assert variante.app_id == 730
    assert variante.fonte == "csgo_api"
    assert variante.id_externo == "agent-4613"
    assert variante.nome_mercado == registro["market_hash_name"]
    assert variante.skin_id_externo is None

def test_normalizar_variante_sem_identidade_comercial():
    """Testa a rejeição de um registro sem nome comercial."""

    registro = {
        "id": "sticker-1",
        "name": "Sticker | Shooter",
        "market_hash_name": None,
        "image": "https://exemplo.com/sticker.png",
    }

    with pytest.raises(
        ErroNormalizacaoVarianteAdicionalCSGOAPI,
        match="Registro sem identidade comercial conhecida.",
    ):
        normalizar_variante_item_adicional_csgo_api(
            registro,
            categoria="adesivos",
        )

def test_normalizar_variante_sem_id_externo():
    """Testa a rejeição de um registro sem identificador externo."""

    registro = {
        "id": None,
        "name": "Sticker | Teste",
        "market_hash_name": "Sticker | Teste",
        "image": "https://exemplo.com/sticker.png",
    }

    with pytest.raises(
        ErroNormalizacaoVarianteAdicionalCSGOAPI,
        match="Registro sem ID externo válido.",
    ):
        normalizar_variante_item_adicional_csgo_api(
            registro,
            categoria="adesivos",
        )

def test_normalizar_variante_categoria_invalida():
    """Testa a rejeição de categorias não suportadas."""

    with pytest.raises(
        ErroNormalizacaoVarianteAdicionalCSGOAPI,
        match="Categoria não suportada:",
    ):
        normalizar_variante_item_adicional_csgo_api(
            {},
            categoria="categoria_inexistente",
        )