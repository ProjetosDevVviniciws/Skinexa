from decimal import Decimal

from unittest.mock import Mock, patch

import pytest

from skinexa.dto.catalogo.item import ItemCatalogoDTO

from skinexa.services.catalogo.pesquisa import (
    pesquisar_item_por_identificador,
    pesquisar_itens_globalmente,
    pesquisar_itens_por_nome,  
)

def _criar_registro_item(
    *,
    item_id: int = 1,
    nome_mercado: str = "AK-47 | Redline (Field-Tested)",
    nome_exibicao: str = "AK-47 | Redline",
) -> dict:
    """Cria um registro de catálogo para uso nos testes."""

    return {
        "id": item_id,
        "app_id": 730,
        "nome_mercado": nome_mercado,
        "nome_exibicao": nome_exibicao,
        "tipo_item": "skin",
        "nome_arma": "AK-47",
        "nome_acabamento": "Redline",
        "estado_exterior": "Field-Tested",
        "raridade": "Classified",
        "qualidade": None,
        "colecao": "The Phoenix Collection",
        "descricao": None,
        "indice_pintura": 282,
        "float_minimo": Decimal("0.10"),
        "float_maximo": Decimal("0.70"),
        "variante_stattrak": 0,
        "variante_souvenir": 0,
        "comercializavel": 1,
        "mercadoria_generica": 0,
        "steam_class_id": None,
        "steam_instance_id": None,
        "url_icone": None,
        "url_icone_grande": None,
        "tags": None,
        "metadados_origem": None,
    }
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_itens_catalogo_por_nome",
)

def test_pesquisar_itens_por_nome(
    mock_pesquisar_itens,
):
    """Testa pesquisa de itens do catálogo."""

    conexao = Mock()

    mock_pesquisar_itens.return_value = [
        _criar_registro_item(
            item_id=1,
        ),
        _criar_registro_item(
            item_id=2,
            nome_mercado=(
                "AK-47 | Redline (Minimal Wear)"
            ),
        ),
    ]

    resultado = pesquisar_itens_por_nome(
        conexao,
        termo="Redline",
        limite=20,
        deslocamento=0,
    )

    assert len(resultado) == 2

    assert all(
        isinstance(item, ItemCatalogoDTO)
        for item in resultado
    )

    assert resultado[0].id == 1
    assert resultado[1].id == 2

    mock_pesquisar_itens.assert_called_once_with(
        conexao,
        termo="Redline",
        limite=20,
        deslocamento=0,
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_itens_catalogo_por_nome",
)

def test_pesquisar_itens_por_nome_sem_resultados(
    mock_pesquisar_itens,
):
    """Testa pesquisa sem resultados."""

    conexao = Mock()

    mock_pesquisar_itens.return_value = []

    resultado = pesquisar_itens_por_nome(
        conexao,
        termo="Item inexistente",
        limite=20,
        deslocamento=0,
    )

    assert resultado == []

    mock_pesquisar_itens.assert_called_once_with(
        conexao,
        termo="Item inexistente",
        limite=20,
        deslocamento=0,
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_itens_catalogo_por_nome",
)

def test_pesquisar_itens_por_nome_utiliza_paginacao_padrao(
    mock_pesquisar_itens,
):
    """Testa os valores padrão da pesquisa por nome."""

    conexao = Mock()

    mock_pesquisar_itens.return_value = []

    resultado = pesquisar_itens_por_nome(
        conexao,
        termo="Redline",
    )

    assert resultado == []

    mock_pesquisar_itens.assert_called_once_with(
        conexao,
        termo="Redline",
        limite=20,
        deslocamento=0,
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "obter_item",
)

def test_pesquisar_item_por_identificador(
    mock_obter_item,
):
    """Testa pesquisa de item pelo identificador."""

    conexao = Mock()

    item = ItemCatalogoDTO(
        **_criar_registro_item(
            item_id=15,
        )
    )

    mock_obter_item.return_value = item

    resultado = pesquisar_item_por_identificador(
        conexao,
        15,
    )

    assert resultado == item

    mock_obter_item.assert_called_once_with(
        conexao,
        15,
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "obter_item",
)

def test_pesquisar_item_por_identificador_inexistente(
    mock_obter_item,
):
    """Testa pesquisa por identificador inexistente."""

    conexao = Mock()

    mock_obter_item.return_value = None

    resultado = pesquisar_item_por_identificador(
        conexao,
        999,
    )

    assert resultado is None

    mock_obter_item.assert_called_once_with(
        conexao,
        999,
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_itens_por_nome",
)

def test_pesquisar_itens_globalmente_por_nome(
    mock_pesquisar_por_nome,
):
    """Testa busca global com termo textual."""

    conexao = Mock()

    item = ItemCatalogoDTO(
        **_criar_registro_item()
    )

    mock_pesquisar_por_nome.return_value = [
        item,
    ]

    resultado = pesquisar_itens_globalmente(
        conexao,
        termo="Redline",
        limite=20,
    )

    assert resultado == [item]

    mock_pesquisar_por_nome.assert_called_once_with(
        conexao,
        termo="Redline",
        limite=20,
        deslocamento=0,
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_itens_por_nome",
)
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_item_por_identificador",
)

def test_pesquisar_itens_globalmente_por_identificador(
    mock_pesquisar_por_identificador,
    mock_pesquisar_por_nome,
):
    """Testa busca global com identificador."""

    conexao = Mock()

    item = ItemCatalogoDTO(
        **_criar_registro_item(
            item_id=15,
        )
    )

    mock_pesquisar_por_identificador.return_value = item
    mock_pesquisar_por_nome.return_value = []

    resultado = pesquisar_itens_globalmente(
        conexao,
        termo="15",
        limite=20,
    )

    assert resultado == [item]

    mock_pesquisar_por_identificador.assert_called_once_with(
        conexao,
        15,
    )

    mock_pesquisar_por_nome.assert_called_once_with(
        conexao,
        termo="15",
        limite=20,
        deslocamento=0,
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_itens_por_nome",
)
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_item_por_identificador",
)

def test_pesquisar_itens_globalmente_com_identificador_inexistente(
    mock_pesquisar_por_identificador,
    mock_pesquisar_por_nome,
):
    """Continua a pesquisa quando o identificador não existe."""

    conexao = Mock()

    item = ItemCatalogoDTO(
        **_criar_registro_item()
    )

    mock_pesquisar_por_identificador.return_value = None
    mock_pesquisar_por_nome.return_value = [item]

    resultado = pesquisar_itens_globalmente(
        conexao,
        termo="999",
        limite=20,
    )

    assert resultado == [item]

    mock_pesquisar_por_identificador.assert_called_once_with(
        conexao,
        999,
    )

    mock_pesquisar_por_nome.assert_called_once_with(
        conexao,
        termo="999",
        limite=20,
        deslocamento=0,
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_itens_por_nome",
)
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_item_por_identificador",
)

def test_pesquisar_itens_globalmente_remove_duplicidade(
    mock_pesquisar_por_identificador,
    mock_pesquisar_por_nome,
):
    """Remove itens duplicados da busca global."""

    conexao = Mock()

    item = ItemCatalogoDTO(
        **_criar_registro_item(
            item_id=15,
        )
    )

    mock_pesquisar_por_identificador.return_value = item
    mock_pesquisar_por_nome.return_value = [item]

    resultado = pesquisar_itens_globalmente(
        conexao,
        termo="15",
        limite=20,
    )

    assert resultado == [item]
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_itens_por_nome",
)
@patch(
    "skinexa.services.catalogo.pesquisa."
    "pesquisar_item_por_identificador",
)

def test_pesquisar_itens_globalmente_com_termo_vazio(
    mock_pesquisar_por_identificador,
    mock_pesquisar_por_nome,
):
    """Não pesquisa quando o termo está vazio."""

    conexao = Mock()

    resultado = pesquisar_itens_globalmente(
        conexao,
        termo="   ",
    )

    assert resultado == []

    mock_pesquisar_por_identificador.assert_not_called()
    mock_pesquisar_por_nome.assert_not_called()
    
def test_pesquisar_itens_globalmente_com_limite_invalido():
    """Testa busca global com limite inválido."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="O limite deve ser maior que zero.",
    ):
        pesquisar_itens_globalmente(
            conexao,
            termo="Redline",
            limite=0,
        )