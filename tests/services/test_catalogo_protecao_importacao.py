from unittest.mock import MagicMock, patch

import pytest

from skinexa.dto.catalogo.importacao import (
    ItemImportacaoCatalogoDTO,
)

from skinexa.dto.catalogo.variante import (
    VarianteImportacaoCatalogoDTO,
)

from skinexa.dto.catalogo.normalizacao_lote import (
    RelatorioNormalizacaoCatalogoDTO,
)

from skinexa.services.catalogo.importacao import (
    importar_lote_catalogo,
    verificar_item_catalogo_importacao,
    verificar_variante_catalogo_importacao,
)

def criar_relatorio_protegido() -> RelatorioNormalizacaoCatalogoDTO:
    """Cria um relatório válido com um item e sua variante."""

    item = ItemImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="Sticker | Teste",
        nome_exibicao="Sticker | Teste",
        tipo_item="adesivo",
    )

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="Sticker | Teste",
        fonte="csgo_api",
        id_externo="sticker-100",
    )

    return RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=1,
        total_normalizados=1,
        total_rejeitados=0,
        total_duplicados=0,
        itens=(item,),
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=1,
        total_variantes_duplicadas=0,
        variantes=(variante,),
    )

def test_verificar_item_catalogo_sem_registro_existente():
    """Permite um item ainda não cadastrado no catálogo."""

    conexao = MagicMock()

    conexao.execute.return_value.mappings.return_value.first.return_value = None

    verificar_item_catalogo_importacao(
        conexao,
        app_id=730,
        nome_mercado="Sticker | Teste",
        tipo_item="adesivo",
    )

    assert conexao.execute.call_count == 1

def test_verificar_item_catalogo_com_tipo_compativel():
    """Permite um item existente com o mesmo tipo."""

    conexao = MagicMock()

    conexao.execute.return_value.mappings.return_value.first.return_value = {
        "id": 25000,
        "tipo_item": "adesivo",
    }

    verificar_item_catalogo_importacao(
        conexao,
        app_id=730,
        nome_mercado="Sticker | Teste",
        tipo_item="adesivo",
    )

def test_verificar_item_catalogo_com_tipo_incompativel():
    """Rejeita a importação quando o tipo comercial é diferente."""

    conexao = MagicMock()

    conexao.execute.return_value.mappings.return_value.first.return_value = {
        "id": 25000,
        "tipo_item": "rifle",
    }

    with pytest.raises(
        RuntimeError,
        match="Conflito de tipo",
    ):
        verificar_item_catalogo_importacao(
            conexao,
            app_id=730,
            nome_mercado="Sticker | Teste",
            tipo_item="adesivo",
        )

def test_verificar_variante_com_vinculo_compativel():
    """Permite uma variante associada ao item esperado."""

    conexao = MagicMock()

    conexao.execute.return_value.mappings.return_value.first.return_value = {
        "id": 32000,
        "item_catalogo_id": 25000,
    }

    verificar_variante_catalogo_importacao(
        conexao,
        fonte="csgo_api",
        id_externo="sticker-100",
        item_catalogo_id=25000,
    )

def test_verificar_variante_com_vinculo_incompativel():
    """Rejeita uma variante associada a outro item comercial."""

    conexao = MagicMock()

    conexao.execute.return_value.mappings.return_value.first.return_value = {
        "id": 32000,
        "item_catalogo_id": 99999,
    }

    with pytest.raises(
        RuntimeError,
        match="Conflito de vínculo",
    ):
        verificar_variante_catalogo_importacao(
            conexao,
            fonte="csgo_api",
            id_externo="sticker-100",
            item_catalogo_id=25000,
        )

def test_importar_lote_com_protecao_habilitada():
    """Confirma que a importação protegida preserva os vínculos."""

    conexao = MagicMock()
    relatorio = criar_relatorio_protegido()

    with patch(
        "skinexa.services.catalogo.importacao."
        "verificar_item_catalogo_importacao"
    ) as mock_verificar_item, patch(
        "skinexa.services.catalogo.importacao."
        "verificar_variante_catalogo_importacao"
    ) as mock_verificar_variante, patch(
        "skinexa.services.catalogo.importacao."
        "inserir_ou_atualizar_item_catalogo_importacao"
    ) as mock_inserir_item, patch(
        "skinexa.services.catalogo.importacao."
        "obter_item_catalogo_por_nome_mercado"
    ) as mock_obter_item, patch(
        "skinexa.services.catalogo.importacao."
        "inserir_ou_atualizar_variante_catalogo_importacao"
    ) as mock_inserir_variante:

        mock_obter_item.return_value = {
            "id": 25000,
        }

        resultado = importar_lote_catalogo(
            conexao,
            relatorio,
            validar_vinculos=True,
        )

    assert resultado == (1, 1)

    assert mock_verificar_item.call_count == 2
    assert mock_verificar_variante.call_count == 2

    mock_inserir_item.assert_called_once_with(
        conexao,
        relatorio.itens[0],
    )

    mock_inserir_variante.assert_called_once_with(
        conexao,
        item_catalogo_id=25000,
        variante=relatorio.variantes[0],
        proteger_vinculo=True,
    )

def test_importar_lote_rejeita_conflito_antes_do_upsert():
    """Impede o upsert quando o item possui tipo incompatível."""

    conexao = MagicMock()
    relatorio = criar_relatorio_protegido()

    with patch(
        "skinexa.services.catalogo.importacao."
        "verificar_item_catalogo_importacao",
        side_effect=RuntimeError(
            "Conflito de tipo para o item comercial."
        ),
    ), patch(
        "skinexa.services.catalogo.importacao."
        "inserir_ou_atualizar_item_catalogo_importacao"
    ) as mock_inserir_item:

        with pytest.raises(
            RuntimeError,
            match="Conflito de tipo",
        ):
            importar_lote_catalogo(
                conexao,
                relatorio,
                validar_vinculos=True,
            )

    mock_inserir_item.assert_not_called()