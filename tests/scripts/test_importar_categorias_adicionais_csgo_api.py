from unittest.mock import patch

import pytest

from skinexa.dto.catalogo.importacao import (
    ItemImportacaoCatalogoDTO,
)

from skinexa.dto.catalogo.variante import (
    VarianteImportacaoCatalogoDTO,
)

from skinexa.dto.catalogo.normalizacao_itens_adicionais import (
    RelatorioItensAdicionaisDTO,
)

from scripts.importar_categorias_adicionais_csgo_api import (
    adaptar_relatorio_importacao,
    executar_validacao_categorias_adicionais,
)

def criar_relatorio_teste(
    *,
    categoria: str = "adesivos",
    nome: str = "Sticker | Teste",
    id_externo: str = "sticker-100",
) -> RelatorioItensAdicionaisDTO:
    """Cria um relatório válido com um item e sua variante."""

    item = ItemImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado=nome,
        nome_exibicao=nome,
        tipo_item="adesivo",
    )

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado=nome,
        fonte="csgo_api",
        id_externo=id_externo,
    )

    return RelatorioItensAdicionaisDTO(
        categoria=categoria,
        total_recebidos=1,
        total_normalizados=1,
        total_sem_identidade_comercial=0,
        total_rejeitados=0,
        total_duplicados=0,
        itens=(item,),
        pendentes=(),
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=1,
        total_variantes_duplicadas=0,
        variantes=(variante,),
    )

def test_adaptar_relatorio_preserva_item_e_variante():
    """Verifica se a adaptação preserva a identidade comercial."""

    relatorio = criar_relatorio_teste()

    resultado = adaptar_relatorio_importacao(
        [relatorio]
    )

    assert resultado.total_normalizados == 1
    assert resultado.total_variantes_normalizadas == 1

    assert resultado.itens[0].nome_mercado == (
        resultado.variantes[0].nome_mercado
    )

    assert resultado.variantes[0].id_externo == "sticker-100"

def test_adaptar_relatorio_rejeita_item_duplicado():
    """Impede itens comerciais duplicados entre relatórios."""

    primeiro = criar_relatorio_teste(
        categoria="adesivos",
        id_externo="sticker-100",
    )

    segundo = criar_relatorio_teste(
        categoria="caixas",
        id_externo="crate-200",
    )

    with pytest.raises(
        ValueError,
        match="Item comercial duplicado",
    ):
        adaptar_relatorio_importacao(
            [primeiro, segundo]
        )

def test_adaptar_relatorio_rejeita_variante_sem_item():
    """Impede a importação de uma variante sem item correspondente."""

    relatorio = criar_relatorio_teste()

    variante_orfa = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="Item Inexistente",
        fonte="csgo_api",
        id_externo="sticker-999",
    )

    relatorio_invalido = RelatorioItensAdicionaisDTO(
        categoria="adesivos",
        total_recebidos=2,
        total_normalizados=1,
        total_sem_identidade_comercial=0,
        total_rejeitados=0,
        total_duplicados=0,
        itens=relatorio.itens,
        pendentes=(),
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=2,
        total_variantes_duplicadas=0,
        variantes=(
            relatorio.variantes[0],
            variante_orfa,
        ),
    )

    with pytest.raises(
        ValueError,
        match="Variante sem item comercial correspondente",
    ):
        adaptar_relatorio_importacao(
            [relatorio_invalido]
        )

def test_validacao_busca_todas_as_categorias():
    """Valida a consulta das categorias sem realizar persistência."""

    registros = [
        {
            "id": "sticker-100",
            "name": "Sticker | Teste",
            "market_hash_name": "Sticker | Teste",
            "image": "https://exemplo.com/sticker.png",
        }
    ]

    with patch(
        "scripts.importar_categorias_adicionais_csgo_api."
        "buscar_itens_csgo_api"
    ) as mock_buscar, patch(
        "scripts.importar_categorias_adicionais_csgo_api."
        "normalizar_lote_itens_adicionais_csgo_api"
    ) as mock_normalizar:

        mock_buscar.return_value = registros

        mock_normalizar.side_effect = [
            criar_relatorio_teste(
                categoria="adesivos",
                nome="Sticker | Teste",
                id_externo="sticker-100",
            ),
            criar_relatorio_teste(
                categoria="caixas",
                nome="Case Teste",
                id_externo="crate-200",
            ),
            criar_relatorio_teste(
                categoria="agentes",
                nome="Agente Teste",
                id_externo="agent-300",
            ),
        ]

        resultado = executar_validacao_categorias_adicionais()

    assert mock_buscar.call_count == 3
    assert mock_normalizar.call_count == 3

    assert resultado.total_normalizados == 3
    assert resultado.total_variantes_normalizadas == 3
    
@pytest.mark.parametrize(
    "categorias,mensagem",
    [
        (
            (),
            "pelo menos uma categoria",
        ),
        (
            ("patches", "patches"),
            "categorias repetidas",
        ),
        (
            ("categoria_inexistente",),
            "Categorias não suportadas",
        ),
    ],
)

def test_validacao_rejeita_categorias_invalidas(
    categorias,
    mensagem,
):
    """Rejeita seleções vazias, repetidas ou não suportadas."""

    with patch(
        "scripts.importar_categorias_adicionais_csgo_api."
        "buscar_itens_csgo_api"
    ) as mock_buscar:
        with pytest.raises(
            ValueError,
            match=mensagem,
        ):
            executar_validacao_categorias_adicionais(
                categorias=categorias,
            )

    mock_buscar.assert_not_called()

def test_validacao_processa_somente_categorias_selecionadas():
    """Consulta e normaliza somente as categorias informadas."""

    registros = [
        {
            "id": "patch-4550",
            "name": "Patch | Crazy Banana",
            "market_hash_name": "Patch | Crazy Banana",
            "image": "https://exemplo.com/patch.png",
        }
    ]

    with patch(
        "scripts.importar_categorias_adicionais_csgo_api."
        "buscar_itens_csgo_api",
        return_value=registros,
    ) as mock_buscar, patch(
        "scripts.importar_categorias_adicionais_csgo_api."
        "normalizar_lote_itens_adicionais_csgo_api"
    ) as mock_normalizar:

        mock_normalizar.return_value = criar_relatorio_teste(
            categoria="patches",
            nome="Patch | Crazy Banana",
            id_externo="patch-4550",
        )

        resultado = executar_validacao_categorias_adicionais(
            categorias=("patches",),
        )

    mock_buscar.assert_called_once_with(
        "patches"
    )

    mock_normalizar.assert_called_once_with(
        registros,
        categoria="patches",
    )

    assert resultado.total_normalizados == 1
    assert resultado.total_variantes_normalizadas == 1

def test_validacao_filtra_identidade_antes_do_limite():
    """Seleciona registros com identidade antes de aplicar o limite."""

    registros = [
        {
            "id": "collectible-1",
            "name": "Item sem identidade",
            "market_hash_name": None,
            "image": "https://exemplo.com/1.png",
        },
        {
            "id": "collectible-2",
            "name": "Operation Test Pass",
            "market_hash_name": "Operation Test Pass",
            "image": "https://exemplo.com/2.png",
        },
        {
            "id": "collectible-3",
            "name": "Operation Other Pass",
            "market_hash_name": "Operation Other Pass",
            "image": "https://exemplo.com/3.png",
        },
    ]

    with patch(
        "scripts.importar_categorias_adicionais_csgo_api."
        "buscar_itens_csgo_api",
        return_value=registros,
    ), patch(
        "scripts.importar_categorias_adicionais_csgo_api."
        "normalizar_lote_itens_adicionais_csgo_api"
    ) as mock_normalizar:

        mock_normalizar.return_value = criar_relatorio_teste(
            categoria="colecionaveis",
            nome="Operation Test Pass",
            id_externo="collectible-2",
        )

        executar_validacao_categorias_adicionais(
            categorias=("colecionaveis",),
            limite=1,
            somente_com_identidade=True,
        )

    registros_recebidos = mock_normalizar.call_args.args[0]

    assert len(registros_recebidos) == 1
    assert registros_recebidos[0]["id"] == "collectible-2"

def test_validacao_sem_filtro_preserva_comportamento():
    """Mantém a seleção original quando o filtro não está habilitado."""

    registros = [
        {
            "id": "collectible-1",
            "name": "Item sem identidade",
            "market_hash_name": None,
            "image": "https://exemplo.com/1.png",
        },
        {
            "id": "collectible-2",
            "name": "Operation Test Pass",
            "market_hash_name": "Operation Test Pass",
            "image": "https://exemplo.com/2.png",
        },
    ]

    with patch(
        "scripts.importar_categorias_adicionais_csgo_api."
        "buscar_itens_csgo_api",
        return_value=registros,
    ), patch(
        "scripts.importar_categorias_adicionais_csgo_api."
        "normalizar_lote_itens_adicionais_csgo_api"
    ) as mock_normalizar:

        mock_normalizar.return_value = criar_relatorio_teste(
            categoria="colecionaveis",
            nome="Operation Test Pass",
            id_externo="collectible-2",
        )

        executar_validacao_categorias_adicionais(
            categorias=("colecionaveis",),
            limite=1,
        )

    registros_recebidos = mock_normalizar.call_args.args[0]

    assert len(registros_recebidos) == 1
    assert registros_recebidos[0]["id"] == "collectible-1"