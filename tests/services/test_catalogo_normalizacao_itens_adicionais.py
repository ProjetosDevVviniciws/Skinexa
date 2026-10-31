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

def test_normalizar_lote_gera_variantes():
    """Testa a geração dos vínculos externos dos itens adicionais."""

    registros = [
        {
            "id": "sticker-13",
            "name": "Sticker | Lucky 13",
            "market_hash_name": "Sticker | Lucky 13",
            "image": "https://exemplo.com/sticker.png",
        },
    ]

    relatorio = normalizar_lote_itens_adicionais_csgo_api(
        registros,
        categoria="adesivos",
    )

    assert relatorio.total_normalizados == 1
    assert relatorio.total_variantes_normalizadas == 1
    assert relatorio.total_variantes_duplicadas == 0

    item = relatorio.itens[0]
    variante = relatorio.variantes[0]

    assert variante.app_id == item.app_id
    assert variante.nome_mercado == item.nome_mercado
    assert variante.fonte == "csgo_api"
    assert variante.id_externo == "sticker-13"

def test_normalizar_lote_preserva_multiplas_variantes():
    """Testa múltiplos identificadores externos para o mesmo item."""

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

    assert relatorio.total_variantes_normalizadas == 2
    assert relatorio.total_variantes_duplicadas == 0

    assert len(relatorio.itens) == 1

    assert {
        variante.id_externo
        for variante in relatorio.variantes
    } == {
        "sticker-100",
        "sticker-101",
    }

    assert all(
        variante.nome_mercado == "Sticker | Teste"
        for variante in relatorio.variantes
    )

def test_normalizar_lote_remove_variantes_duplicadas():
    """Testa a deduplicação de identificadores externos repetidos."""

    registro = {
        "id": "crate-1210",
        "name": "Gift Package",
        "market_hash_name": "Gift Package",
        "image": "https://exemplo.com/caixa.png",
    }

    relatorio = normalizar_lote_itens_adicionais_csgo_api(
        [registro, registro.copy()],
        categoria="caixas",
    )

    assert relatorio.total_recebidos == 2
    assert relatorio.total_normalizados == 1
    assert relatorio.total_duplicados == 1

    assert relatorio.total_variantes_normalizadas == 1
    assert relatorio.total_variantes_duplicadas == 1

    assert relatorio.total_rejeitados == 0

def test_normalizar_lote_rejeita_id_externo_com_vinculos_diferentes():
    """Testa a rejeição de um ID externo associado a dois itens."""

    registros = [
        {
            "id": "agent-4613",
            "name": "Agente A",
            "market_hash_name": "Agente A",
            "image": "https://exemplo.com/agente-a.png",
        },
        {
            "id": "agent-4613",
            "name": "Agente B",
            "market_hash_name": "Agente B",
            "image": "https://exemplo.com/agente-b.png",
        },
    ]

    relatorio = normalizar_lote_itens_adicionais_csgo_api(
        registros,
        categoria="agentes",
    )

    assert relatorio.total_recebidos == 2
    assert relatorio.total_normalizados == 1
    assert relatorio.total_variantes_normalizadas == 1
    assert relatorio.total_rejeitados == 1

    assert relatorio.erros[0].motivo == (
        "ID externo associado a itens comerciais diferentes."
    )

    assert relatorio.variantes[0].nome_mercado == "Agente A"
    
def test_normalizacao_classifica_chave_nao_comercializavel():
    """Classifica como não comercializável uma chave restrita pela fonte."""

    registros = [
        {
            "id": "key-1384",
            "name": "Shattered Web Case Key",
            "market_hash_name": None,
            "image": "https://exemplo.com/chave.png",
            "marketable": False,
        }
    ]

    relatorio = normalizar_lote_itens_adicionais_csgo_api(
        registros,
        categoria="chaves",
    )

    assert relatorio.total_recebidos == 1
    assert relatorio.total_normalizados == 0
    assert relatorio.total_sem_identidade_comercial == 1
    assert relatorio.total_rejeitados == 0

    assert len(relatorio.pendentes) == 1

    assert (
        relatorio.pendentes[0].motivo
        == "nao_comercializavel_fonte"
    )

    assert relatorio.variantes == ()