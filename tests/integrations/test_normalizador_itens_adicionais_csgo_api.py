import pytest

from skinexa.integrations.catalogo.normalizador_itens_adicionais_csgo_api import (
    ErroNormalizacaoItemAdicionalCSGOAPI,
    normalizar_item_adicional_csgo_api,
)

def test_normalizar_adesivo_csgo_api():
    """Testa a normalização de um adesivo com identidade comercial."""

    registro = {
        "id": "sticker-100",
        "name": "Sticker | Teste",
        "market_hash_name": "Sticker | Teste",
        "image": "https://exemplo.com/adesivo.png",
        "description": "Adesivo de teste.",
        "def_index": "100",
        "type": "Team",
        "effect": "Holo",
        "rarity": {
            "id": "rarity_rare",
            "name": "High Grade",
            "color": "#4b69ff",
        },
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria="adesivos",
    )

    assert item.app_id == 730
    assert item.nome_mercado == "Sticker | Teste"
    assert item.nome_exibicao == "Sticker | Teste"
    assert item.tipo_item == "adesivo"
    assert item.raridade == "High Grade"
    assert item.url_icone_grande == "https://exemplo.com/adesivo.png"
    assert item.comercializavel is False

    assert item.metadados_origem["id_externo"] == "sticker-100"
    assert item.metadados_origem["effect"] == "Holo"
    assert item.metadados_origem["type"] == "Team"

def test_normalizar_caixa_csgo_api():
    """Testa a normalização de um contêiner da CSGO-API."""

    registro = {
        "id": "crate-1210",
        "name": "Gift Package",
        "market_hash_name": "Gift Package",
        "image": "https://exemplo.com/caixa.png",
        "description": "Pacote de presente.",
        "def_index": "1210",
        "type": None,
        "rarity": {
            "id": "rarity_common",
            "name": "Base Grade",
            "color": "#b0c3d9",
        },
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria="caixas",
    )

    assert item.tipo_item == "caixa"
    assert item.nome_mercado == "Gift Package"
    assert item.raridade == "Base Grade"
    assert item.indice_pintura is None
    assert item.estado_exterior is None

    assert item.metadados_origem["categoria_origem"] == "caixas"
    assert item.metadados_origem["def_index"] == "1210"

def test_normalizar_agente_csgo_api():
    """Testa a normalização de um agente com metadados próprios."""

    registro = {
        "id": "agent-4613",
        "name": "Bloody Darryl The Strapped | The Professionals",
        "market_hash_name": "Bloody Darryl The Strapped | The Professionals",
        "image": "https://exemplo.com/agente.png",
        "team": {
            "id": "terrorists",
            "name": "Terrorists",
        },
        "rarity": {
            "id": "rarity_legendary_character",
            "name": "Superior",
            "color": "#d32ce6",
        },
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria="agentes",
    )

    assert item.tipo_item == "agente"
    assert item.raridade == "Superior"
    assert item.float_minimo is None
    assert item.float_maximo is None

    assert item.metadados_origem["id_externo"] == "agent-4613"
    assert item.metadados_origem["team"]["id"] == "terrorists"

def test_normalizar_item_sem_nome_comercial():
    """Testa a rejeição de um registro sem identidade comercial."""

    registro = {
        "id": "sticker-1",
        "name": "Sticker | Shooter",
        "market_hash_name": None,
        "image": "https://exemplo.com/adesivo.png",
    }

    with pytest.raises(
        ErroNormalizacaoItemAdicionalCSGOAPI,
        match="Registro sem identidade comercial conhecida.",
    ):
        normalizar_item_adicional_csgo_api(
            registro,
            categoria="adesivos",
        )

def test_normalizar_item_sem_id_externo():
    """Testa a rejeição de um registro sem ID externo."""

    registro = {
        "id": None,
        "name": "Sticker | Teste",
        "market_hash_name": "Sticker | Teste",
        "image": "https://exemplo.com/adesivo.png",
    }

    with pytest.raises(
        ErroNormalizacaoItemAdicionalCSGOAPI,
        match="Registro sem ID externo válido.",
    ):
        normalizar_item_adicional_csgo_api(
            registro,
            categoria="adesivos",
        )

def test_normalizar_item_sem_imagem():
    """Testa a rejeição de um registro sem imagem."""

    registro = {
        "id": "sticker-100",
        "name": "Sticker | Teste",
        "market_hash_name": "Sticker | Teste",
        "image": None,
    }

    with pytest.raises(
        ErroNormalizacaoItemAdicionalCSGOAPI,
        match="Registro sem imagem válida.",
    ):
        normalizar_item_adicional_csgo_api(
            registro,
            categoria="adesivos",
        )

def test_normalizar_categoria_nao_suportada():
    """Testa a rejeição de uma categoria não implementada."""

    with pytest.raises(
        ErroNormalizacaoItemAdicionalCSGOAPI,
        match="Categoria não suportada:",
    ):
        normalizar_item_adicional_csgo_api(
            {},
            categoria="categoria_inexistente",
        )

def test_normalizar_item_sem_raridade():
    """Testa um item válido sem informação de raridade."""

    registro = {
        "id": "crate-200",
        "name": "Contêiner de teste",
        "market_hash_name": "Contêiner de teste",
        "image": "https://exemplo.com/conteiner.png",
        "rarity": None,
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria="caixas",
    )

    assert item.raridade is None
    assert item.metadados_origem["raridade_origem"] is None
    
@pytest.mark.parametrize(
    "categoria,tipo_item,id_externo,nome_mercado",
    [
        (
            "patches",
            "patch",
            "patch-4550",
            "Patch | Crazy Banana",
        ),
        (
            "chaveiros",
            "chaveiro",
            "keychain-1",
            "Charm | Teste",
        ),
        (
            "grafites",
            "grafite",
            "graffiti-1653",
            "Sealed Graffiti | Blood Boiler",
        ),
        (
            "musicas",
            "musica",
            "music_kit-3",
            "Music Kit | Teste",
        ),
        (
            "colecionaveis",
            "colecionavel",
            "collectible-100",
            "Collectible | Teste",
        ),
        (
            "adesivos_encapsulados",
            "adesivo_encapsulado",
            "sticker_slab-100",
            "Sticker Slab | Teste",
        ),
        (
            "chaves",
            "chave",
            "key-1203",
            "CS:GO Case Key",
        ),
        (
            "destaques",
            "destaque",
            "highlight-1",
            "Souvenir Charm | Teste",
        ),
    ],
)

def test_normalizar_novas_categorias_csgo_api(
    categoria,
    tipo_item,
    id_externo,
    nome_mercado,
):
    """Testa a normalização das oito novas categorias."""

    registro = {
        "id": id_externo,
        "name": nome_mercado,
        "market_hash_name": nome_mercado,
        "image": "https://exemplo.com/imagem.png",
        "rarity": {
            "name": "High Grade",
        },
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria=categoria,
    )

    assert item.app_id == 730
    assert item.nome_mercado == nome_mercado
    assert item.tipo_item == tipo_item
    assert item.raridade == "High Grade"
    assert item.comercializavel is False

    assert item.metadados_origem["id_externo"] == id_externo
    assert item.metadados_origem["categoria_origem"] == categoria

def test_normalizar_chave_preserva_atributo_marketable():
    """Preserva a informação de mercado da chave sem inferir comercialização."""

    registro = {
        "id": "key-1203",
        "name": "CS:GO Case Key",
        "market_hash_name": "CS:GO Case Key",
        "image": "https://exemplo.com/chave.png",
        "marketable": False,
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria="chaves",
    )

    assert item.tipo_item == "chave"
    assert item.comercializavel is False
    assert item.metadados_origem["marketable"] is False

def test_normalizar_destaque_preserva_metadados_especificos():
    """Preserva os atributos próprios dos destaques da CSGO-API."""

    registro = {
        "id": "highlight-1",
        "name": "Souvenir Charm | Teste",
        "market_hash_name": "Souvenir Charm | Teste",
        "image": "https://exemplo.com/destaque.png",
        "type": "player",
        "map": {"name": "Mirage"},
        "video": "https://exemplo.com/video",
        "tournament_player": {"name": "Jogador Teste"},
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria="destaques",
    )

    assert item.tipo_item == "destaque"
    assert item.metadados_origem["type"] == "player"
    assert item.metadados_origem["map"] == {"name": "Mirage"}
    assert item.metadados_origem["video"] == (
        "https://exemplo.com/video"
    )
    assert item.metadados_origem["tournament_player"] == {
        "name": "Jogador Teste"
    }
    
def test_normalizar_musica_preserva_atributo_exclusive():
    """Preserva a exclusividade informada pela CSGO-API."""

    registro = {
        "id": "music_kit-40",
        "name": "Music Kit | Teste Exclusivo",
        "market_hash_name": "Music Kit | Teste Exclusivo",
        "image": "https://exemplo.com/musica.png",
        "exclusive": True,
        "rarity": {
            "name": "High Grade",
        },
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria="musicas",
    )

    assert item.tipo_item == "musica"
    assert item.raridade == "High Grade"
    assert item.metadados_origem["exclusive"] is True
    
def test_normalizar_colecionavel_preserva_atributo_genuine():
    """Preserva a classificação Genuine de um colecionável."""

    registro = {
        "id": "collectible-6001",
        "name": "Genuine Pin | Teste",
        "market_hash_name": "Genuine Pin | Teste",
        "image": "https://exemplo.com/pin.png",
        "type": "Pin",
        "genuine": True,
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria="colecionaveis",
    )

    assert item.tipo_item == "colecionavel"
    assert item.metadados_origem["type"] == "Pin"
    assert item.metadados_origem["genuine"] is True
    
def test_normalizar_grafite_preserva_atributo_tint():
    """Preserva o identificador de cor dos grafites."""

    registro = {
        "id": "graffiti-100",
        "name": "Sealed Graffiti | Teste",
        "market_hash_name": "Sealed Graffiti | Teste",
        "image": "https://exemplo.com/grafite.png",
        "tint": {
            "id": "teste",
            "name": "Cor de Teste",
        },
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria="grafites",
    )

    assert item.tipo_item == "grafite"
    assert item.metadados_origem["tint"] == {
        "id": "teste",
        "name": "Cor de Teste",
    }
    
def test_normalizar_caixa_preserva_atributos_especificos():
    """Preserva atributos próprios de contêineres da CSGO-API."""

    registro = {
        "id": "crate-100",
        "name": "Caixa de Teste",
        "market_hash_name": "Caixa de Teste",
        "image": "https://exemplo.com/caixa.png",
        "first_sale_date": "2026-01-01",
        "rental": False,
        "model_player": None,
    }

    item = normalizar_item_adicional_csgo_api(
        registro,
        categoria="caixas",
    )

    assert item.tipo_item == "caixa"
    assert item.metadados_origem["first_sale_date"] == (
        "2026-01-01"
    )
    assert item.metadados_origem["rental"] is False
    assert item.metadados_origem["model_player"] is None