from copy import deepcopy

import pytest

from skinexa.services.catalogo.normalizacao_lote import (
    normalizar_lote_skins_csgo_api,
)

@pytest.fixture
def registro_skin():
    """Registro válido representativo da CSGO-API."""

    return {
        "id": "skin-teste-0",
        "skin_id": "skin-teste",
        "market_hash_name": "AK-47 | Redline (Field-Tested)",
        "name": "AK-47 | Redline (Field-Tested)",
        "category": {
            "id": "csgo_inventory_weapon_category_rifles",
            "name": "Rifles",
        },
        "weapon": {
            "id": "weapon_ak47",
            "name": "AK-47",
        },
        "pattern": {
            "id": "redline",
            "name": "Redline",
        },
        "wear": {
            "id": "SFUI_InvTooltip_Wear_Amount_2",
            "name": "Field-Tested",
        },
        "rarity": {
            "id": "rarity_classified",
            "name": "Classified",
        },
        "paint_index": "282",
        "min_float": 0.10,
        "max_float": 0.70,
        "stattrak": False,
        "souvenir": False,
        "image": "https://example.com/redline.png",
    }

def test_normalizar_lote_vazio():
    """Verifica o relatório gerado para um lote sem registros."""

    relatorio = normalizar_lote_skins_csgo_api([])

    assert relatorio.total_recebidos == 0
    assert relatorio.total_normalizados == 0
    assert relatorio.total_rejeitados == 0
    assert relatorio.total_duplicados == 0
    assert relatorio.itens == ()
    assert relatorio.erros == ()

def test_normalizar_lote_item_valido(registro_skin):
    """Verifica a normalização de um lote com um item válido."""

    relatorio = normalizar_lote_skins_csgo_api(
        [registro_skin]
    )

    assert relatorio.total_recebidos == 1
    assert relatorio.total_normalizados == 1
    assert relatorio.total_rejeitados == 0
    assert relatorio.total_duplicados == 0

    assert relatorio.itens[0].nome_mercado == (
        "AK-47 | Redline (Field-Tested)"
    )

def test_normalizar_lote_com_item_invalido(
    registro_skin,
):
    """Verifica a rejeição de itens inválidos e o registro do erro."""

    invalido = deepcopy(registro_skin)

    invalido["id"] = "skin-invalida"
    invalido.pop("market_hash_name")

    relatorio = normalizar_lote_skins_csgo_api(
        [registro_skin, invalido]
    )

    assert relatorio.total_recebidos == 2
    assert relatorio.total_normalizados == 1
    assert relatorio.total_rejeitados == 1
    assert relatorio.total_duplicados == 0

    assert relatorio.erros[0].indice == 1
    assert (
        relatorio.erros[0].identificador_externo
        == "skin-invalida"
    )

    assert "market_hash_name" in (
        relatorio.erros[0].motivo
    )

def test_normalizar_lote_remove_duplicados(
    registro_skin,
):
    """Verifica a remoção de itens com a mesma chave comercial."""

    duplicado = deepcopy(registro_skin)

    duplicado["id"] = "skin-outro-id"

    relatorio = normalizar_lote_skins_csgo_api(
        [registro_skin, duplicado]
    )

    assert relatorio.total_recebidos == 2
    assert relatorio.total_normalizados == 1
    assert relatorio.total_rejeitados == 0
    assert relatorio.total_duplicados == 1

    assert len(relatorio.itens) == 1

def test_normalizar_lote_preserva_ordem(
    registro_skin,
):
    """Verifica se a ordem dos itens normalizados é preservada."""

    segunda_skin = deepcopy(registro_skin)

    segunda_skin["id"] = "skin-teste-1"
    segunda_skin["market_hash_name"] = (
        "M4A4 | Asiimov (Field-Tested)"
    )
    segunda_skin["name"] = (
        "M4A4 | Asiimov (Field-Tested)"
    )

    relatorio = normalizar_lote_skins_csgo_api(
        [registro_skin, segunda_skin]
    )

    nomes = [
        item.nome_mercado
        for item in relatorio.itens
    ]

    assert nomes == [
        "AK-47 | Redline (Field-Tested)",
        "M4A4 | Asiimov (Field-Tested)",
    ]

def test_normalizar_lote_contabiliza_motivos(
    registro_skin,
):
    """Verifica a contabilização dos motivos de rejeição."""

    sem_nome = deepcopy(registro_skin)
    sem_nome.pop("market_hash_name")

    float_invalido = deepcopy(registro_skin)
    float_invalido["min_float"] = 2

    relatorio = normalizar_lote_skins_csgo_api(
        [sem_nome, float_invalido]
    )

    assert relatorio.total_recebidos == 2
    assert relatorio.total_normalizados == 0
    assert relatorio.total_rejeitados == 2

    assert relatorio.motivos_rejeicao == {
        "Item sem market_hash_name válido.": 1,
        "O float deve estar entre 0 e 1.": 1,
    }

def test_normalizar_lote_preserva_entrada(
    registro_skin,
):
    """Verifica se a normalização não modifica os registros recebidos."""

    registros = [registro_skin]

    original = deepcopy(registros)

    normalizar_lote_skins_csgo_api(registros)

    assert registros == original
    
def test_normalizar_lote_preserva_variantes_com_mesmo_nome(
    registro_skin,
):
    """Verifica a preservação de variantes com a mesma chave comercial."""

    segunda_variante = deepcopy(registro_skin)

    segunda_variante["id"] = "skin-teste-1"
    segunda_variante["paint_index"] = "283"

    relatorio = normalizar_lote_skins_csgo_api(
        [registro_skin, segunda_variante]
    )

    assert relatorio.total_recebidos == 2
    assert relatorio.total_normalizados == 1
    assert relatorio.total_duplicados == 1

    assert relatorio.total_variantes_normalizadas == 2
    assert relatorio.total_variantes_duplicadas == 0

    assert len(relatorio.itens) == 1
    assert len(relatorio.variantes) == 2

    assert [
        variante.indice_pintura
        for variante in relatorio.variantes
    ] == [282, 283]

def test_normalizar_lote_remove_variantes_duplicadas(
    registro_skin,
):
    """Verifica a remoção de variantes com o mesmo identificador externo."""

    duplicado = deepcopy(registro_skin)

    relatorio = normalizar_lote_skins_csgo_api(
        [registro_skin, duplicado]
    )

    assert relatorio.total_recebidos == 2
    assert relatorio.total_normalizados == 1
    assert relatorio.total_duplicados == 1

    assert relatorio.total_variantes_normalizadas == 1
    assert relatorio.total_variantes_duplicadas == 1

    assert len(relatorio.variantes) == 1

def test_normalizar_lote_preserva_ordem_variantes(
    registro_skin,
):
    """Verifica a preservação da ordem das variantes normalizadas."""

    segunda_variante = deepcopy(registro_skin)
    segunda_variante["id"] = "skin-teste-1"

    terceira_variante = deepcopy(registro_skin)
    terceira_variante["id"] = "skin-teste-2"

    relatorio = normalizar_lote_skins_csgo_api(
        [
            registro_skin,
            segunda_variante,
            terceira_variante,
        ]
    )

    ids_externos = [
        variante.id_externo
        for variante in relatorio.variantes
    ]

    assert ids_externos == [
        "skin-teste-0",
        "skin-teste-1",
        "skin-teste-2",
    ]

def test_normalizar_lote_rejeita_variante_sem_id(
    registro_skin,
):
    """Verifica a rejeição de registros sem identificador externo."""

    sem_id = deepcopy(registro_skin)
    sem_id.pop("id")

    relatorio = normalizar_lote_skins_csgo_api(
        [sem_id]
    )

    assert relatorio.total_recebidos == 1
    assert relatorio.total_normalizados == 0
    assert relatorio.total_variantes_normalizadas == 0
    assert relatorio.total_rejeitados == 1

    assert "identificador externo" in (
        relatorio.erros[0].motivo
    )

def test_normalizar_lote_preserva_associacao_comercial(
    registro_skin,
):
    """Verifica a associação lógica entre a variante e o item comercial."""

    relatorio = normalizar_lote_skins_csgo_api(
        [registro_skin]
    )

    item = relatorio.itens[0]
    variante = relatorio.variantes[0]

    assert variante.app_id == item.app_id
    assert variante.nome_mercado == item.nome_mercado

def test_normalizar_lote_vazio_sem_variantes():
    """Verifica a ausência de variantes em um lote vazio."""

    relatorio = normalizar_lote_skins_csgo_api([])

    assert relatorio.total_variantes_normalizadas == 0
    assert relatorio.total_variantes_duplicadas == 0
    assert relatorio.variantes == ()