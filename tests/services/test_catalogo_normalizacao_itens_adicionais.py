import pytest

from skinexa.services.catalogo.normalizacao_itens_adicionais import (
    normalizar_lote_itens_adicionais_csgo_api,
)

def test_normalizar_lote_adesivos():
    """Testa a normalização de adesivos comercialmente identificados."""

    registros = [
        {
            "id": "sticker-100",
            "name": "Sticker | Teste",
            "market_hash_name": "Sticker | Teste",
            "image": "https://exemplo.com/sticker.png",
            "rarity": {
                "name": "High Grade",
            },
        },
    ]

    relatorio = normalizar_lote_itens_adicionais_csgo_api(
        registros,
        categoria="adesivos",
    )

    assert relatorio.total_recebidos == 1
    assert relatorio.total_normalizados == 1
    assert relatorio.total_sem_identidade_comercial == 0
    assert relatorio.total_rejeitados == 0
    assert relatorio.total_duplicados == 0

    assert relatorio.itens[0].tipo_item == "adesivo"
    assert relatorio.itens[0].raridade == "High Grade"

def test_normalizar_lote_com_item_sem_nome_comercial():
    """Testa a separação de registros sem identidade comercial."""

    registros = [
        {
            "id": "sticker-1",
            "name": "Sticker | Shooter",
            "market_hash_name": None,
            "image": "https://exemplo.com/sticker.png",
        },
    ]

    relatorio = normalizar_lote_itens_adicionais_csgo_api(
        registros,
        categoria="adesivos",
    )

    assert relatorio.total_recebidos == 1
    assert relatorio.total_normalizados == 0
    assert relatorio.total_sem_identidade_comercial == 1
    assert relatorio.total_rejeitados == 0

    assert relatorio.pendentes[0].id_externo == "sticker-1"
    assert relatorio.pendentes[0].indice == 0

def test_normalizar_lote_com_registro_invalido():
    """Testa a contabilização de registros inválidos."""

    registros = [
        {
            "id": None,
            "name": "Sticker | Teste",
            "market_hash_name": "Sticker | Teste",
            "image": "https://exemplo.com/sticker.png",
        },
    ]

    relatorio = normalizar_lote_itens_adicionais_csgo_api(
        registros,
        categoria="adesivos",
    )

    assert relatorio.total_recebidos == 1
    assert relatorio.total_normalizados == 0
    assert relatorio.total_sem_identidade_comercial == 0
    assert relatorio.total_rejeitados == 1

    assert (
        relatorio.motivos_rejeicao[
            "Registro sem ID externo válido."
        ] == 1
    )

def test_normalizar_lote_remove_duplicacoes_comerciais():
    """Testa a deduplicação por app_id e nome de mercado."""

    registros = [
        {
            "id": "sticker-100",
            "name": "Sticker | Teste",
            "market_hash_name": "Sticker | Teste",
            "image": "https://exemplo.com/sticker-1.png",
        },
        {
            "id": "sticker-101",
            "name": "Sticker | Teste",
            "market_hash_name": "Sticker | Teste",
            "image": "https://exemplo.com/sticker-2.png",
        },
    ]

    relatorio = normalizar_lote_itens_adicionais_csgo_api(
        registros,
        categoria="adesivos",
    )

    assert relatorio.total_recebidos == 2
    assert relatorio.total_normalizados == 1
    assert relatorio.total_duplicados == 1
    assert relatorio.total_rejeitados == 0

    assert len(relatorio.itens) == 1

def test_normalizar_lote_com_categoria_invalida():
    """Testa a rejeição de uma categoria não suportada."""

    with pytest.raises(
        ValueError,
        match="Categoria não suportada:",
    ):
        normalizar_lote_itens_adicionais_csgo_api(
            [],
            categoria="categoria_inexistente",
        )

def test_normalizar_lote_com_registro_sem_imagem():
    """Testa que a ausência de imagem não é confundida com pendência."""

    registros = [
        {
            "id": "sticker-200",
            "name": "Sticker | Sem Imagem",
            "market_hash_name": None,
            "image": None,
        },
    ]

    relatorio = normalizar_lote_itens_adicionais_csgo_api(
        registros,
        categoria="adesivos",
    )

    assert relatorio.total_recebidos == 1
    assert relatorio.total_sem_identidade_comercial == 0
    assert relatorio.total_rejeitados == 1

    assert relatorio.erros[0].motivo == (
        "Registro sem identidade comercial conhecida."
    )