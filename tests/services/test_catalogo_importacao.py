import pytest

from unittest.mock import Mock, patch

from skinexa.services.catalogo.importacao import (
    importar_lote_catalogo,
)

from skinexa.dto.catalogo.importacao import (
    ItemImportacaoCatalogoDTO,
)

from skinexa.dto.catalogo.variante import (
    VarianteImportacaoCatalogoDTO,
)

from skinexa.dto.catalogo.normalizacao_lote import (
    RelatorioNormalizacaoCatalogoDTO,
)

def test_importar_lote_catalogo():
    """Testa a importação de itens comerciais e variantes."""

    conexao = Mock()

    item = ItemImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        nome_exibicao="AK-47 | Redline (Field-Tested)",
        tipo_item="Rifle",
    )

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    relatorio = RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=1,
        total_normalizados=1,
        total_rejeitados=0,
        total_duplicados=0,
        itens=(item,),
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=1,
        variantes=(variante,),
    )

    with (
        patch(
            "skinexa.services.catalogo.importacao."
            "inserir_ou_atualizar_item_catalogo_importacao"
        ) as mock_inserir_item,
        patch(
            "skinexa.services.catalogo.importacao."
            "obter_item_catalogo_por_nome_mercado"
        ) as mock_obter_item,
        patch(
            "skinexa.services.catalogo.importacao."
            "inserir_ou_atualizar_variante_catalogo_importacao"
        ) as mock_inserir_variante,
    ):
        mock_inserir_item.return_value = 35

        mock_obter_item.return_value = {
            "id": 35,
            "app_id": 730,
            "nome_mercado": "AK-47 | Redline (Field-Tested)",
        }

        mock_inserir_variante.return_value = 50

        resultado = importar_lote_catalogo(
            conexao,
            relatorio,
        )

    assert resultado == (1, 1)

    mock_inserir_item.assert_called_once_with(
        conexao,
        item,
    )

    mock_obter_item.assert_called_once_with(
        conexao,
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
    )

    mock_inserir_variante.assert_called_once_with(
        conexao,
        item_catalogo_id=35,
        variante=variante,
    )

def test_importar_lote_catalogo_vazio():
    """Testa a importação de um lote sem itens e variantes."""

    conexao = Mock()

    relatorio = RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=0,
        total_normalizados=0,
        total_rejeitados=0,
        total_duplicados=0,
        itens=(),
        erros=(),
        motivos_rejeicao={},
    )

    with (
        patch(
            "skinexa.services.catalogo.importacao."
            "inserir_ou_atualizar_item_catalogo_importacao"
        ) as mock_inserir_item,
        patch(
            "skinexa.services.catalogo.importacao."
            "obter_item_catalogo_por_nome_mercado"
        ) as mock_obter_item,
        patch(
            "skinexa.services.catalogo.importacao."
            "inserir_ou_atualizar_variante_catalogo_importacao"
        ) as mock_inserir_variante,
    ):
        resultado = importar_lote_catalogo(
            conexao,
            relatorio,
        )

    assert resultado == (0, 0)

    mock_inserir_item.assert_not_called()
    mock_obter_item.assert_not_called()
    mock_inserir_variante.assert_not_called()

def test_importar_lote_catalogo_item_comercial_inexistente():
    """Testa erro quando a variante não encontra seu item comercial."""

    conexao = Mock()

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    relatorio = RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=1,
        total_normalizados=0,
        total_rejeitados=0,
        total_duplicados=0,
        itens=(),
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=1,
        variantes=(variante,),
    )

    with (
        patch(
            "skinexa.services.catalogo.importacao."
            "obter_item_catalogo_por_nome_mercado"
        ) as mock_obter_item,
        patch(
            "skinexa.services.catalogo.importacao."
            "inserir_ou_atualizar_variante_catalogo_importacao"
        ) as mock_inserir_variante,
    ):
        mock_obter_item.return_value = None

        with pytest.raises(
            RuntimeError,
            match="Item comercial não encontrado",
        ):
            importar_lote_catalogo(
                conexao,
                relatorio,
            )

    mock_obter_item.assert_called_once()
    mock_inserir_variante.assert_not_called()

def test_importar_lote_catalogo_falha_persistencia_comercial():
    """Testa a propagação de falhas ao persistir um item comercial."""

    conexao = Mock()

    item = ItemImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        nome_exibicao="AK-47 | Redline (Field-Tested)",
        tipo_item="Rifle",
    )

    relatorio = RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=1,
        total_normalizados=1,
        total_rejeitados=0,
        total_duplicados=0,
        itens=(item,),
        erros=(),
        motivos_rejeicao={},
    )

    with patch(
        "skinexa.services.catalogo.importacao."
        "inserir_ou_atualizar_item_catalogo_importacao"
    ) as mock_inserir_item:
        mock_inserir_item.side_effect = RuntimeError(
            "Falha na persistência comercial."
        )

        with pytest.raises(
            RuntimeError,
            match="Falha na persistência comercial",
        ):
            importar_lote_catalogo(
                conexao,
                relatorio,
            )

    mock_inserir_item.assert_called_once_with(
        conexao,
        item,
    )

def test_importar_lote_catalogo_falha_persistencia_variante():
    """Testa a propagação de falhas ao persistir uma variante."""

    conexao = Mock()

    item = ItemImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        nome_exibicao="AK-47 | Redline (Field-Tested)",
        tipo_item="Rifle",
    )

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    relatorio = RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=1,
        total_normalizados=1,
        total_rejeitados=0,
        total_duplicados=0,
        itens=(item,),
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=1,
        variantes=(variante,),
    )

    with (
        patch(
            "skinexa.services.catalogo.importacao."
            "inserir_ou_atualizar_item_catalogo_importacao"
        ) as mock_inserir_item,
        patch(
            "skinexa.services.catalogo.importacao."
            "obter_item_catalogo_por_nome_mercado"
        ) as mock_obter_item,
        patch(
            "skinexa.services.catalogo.importacao."
            "inserir_ou_atualizar_variante_catalogo_importacao"
        ) as mock_inserir_variante,
    ):
        mock_inserir_item.return_value = 35
        mock_obter_item.return_value = {"id": 35}

        mock_inserir_variante.side_effect = RuntimeError(
            "Falha na persistência da variante."
        )

        with pytest.raises(
            RuntimeError,
            match="Falha na persistência da variante",
        ):
            importar_lote_catalogo(
                conexao,
                relatorio,
            )

    mock_inserir_item.assert_called_once()
    mock_inserir_variante.assert_called_once()

def test_importar_lote_catalogo_multiplas_variantes():
    """Testa variantes diferentes vinculadas ao mesmo item comercial."""

    conexao = Mock()

    item = ItemImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        nome_exibicao="AK-47 | Redline (Field-Tested)",
        tipo_item="Rifle",
    )

    variante_1 = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    variante_2 = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        fonte="csgo_api",
        id_externo="skin-abc_1",
    )

    relatorio = RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=2,
        total_normalizados=1,
        total_rejeitados=0,
        total_duplicados=1,
        itens=(item,),
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=2,
        variantes=(
            variante_1,
            variante_2,
        ),
    )

    with (
        patch(
            "skinexa.services.catalogo.importacao."
            "inserir_ou_atualizar_item_catalogo_importacao"
        ) as mock_inserir_item,
        patch(
            "skinexa.services.catalogo.importacao."
            "obter_item_catalogo_por_nome_mercado"
        ) as mock_obter_item,
        patch(
            "skinexa.services.catalogo.importacao."
            "inserir_ou_atualizar_variante_catalogo_importacao"
        ) as mock_inserir_variante,
    ):
        mock_inserir_item.return_value = 35
        mock_obter_item.return_value = {"id": 35}

        resultado = importar_lote_catalogo(
            conexao,
            relatorio,
        )

    assert resultado == (1, 2)

    mock_inserir_item.assert_called_once()
    assert mock_obter_item.call_count == 2
    assert mock_inserir_variante.call_count == 2

    assert (
        mock_inserir_variante.call_args_list[0].kwargs[
            "item_catalogo_id"
        ]
        == 35
    )

    assert (
        mock_inserir_variante.call_args_list[1].kwargs[
            "item_catalogo_id"
        ]
        == 35
    )