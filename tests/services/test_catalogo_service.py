from decimal import Decimal

from unittest.mock import Mock, patch

from skinexa.dto.catalogo.item import ItemCatalogoDTO

from skinexa.services.catalogo.service import (
    obter_item,
    obter_item_por_nome_mercado,    
    listar_itens,
    contar_itens, 
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
    "skinexa.services.catalogo.service."
    "obter_item_catalogo_por_id",
)

def test_obter_item(
    mock_obter_item,
):
    """Testa obtenção de item do catálogo."""

    conexao = Mock()

    mock_obter_item.return_value = (
        _criar_registro_item()
    )

    resultado = obter_item(
        conexao,
        1,
    )

    assert isinstance(
        resultado,
        ItemCatalogoDTO,
    )

    assert resultado.id == 1
    assert resultado.app_id == 730
    assert resultado.nome_mercado == (
        "AK-47 | Redline (Field-Tested)"
    )
    assert resultado.variante_stattrak is False
    assert resultado.comercializavel is True

    mock_obter_item.assert_called_once_with(
        conexao,
        1,
    )
    
@patch(
    "skinexa.services.catalogo.service."
    "obter_item_catalogo_por_id",
)

def test_obter_item_inexistente(
    mock_obter_item,
):
    """Testa obtenção de item inexistente."""

    conexao = Mock()

    mock_obter_item.return_value = None

    resultado = obter_item(
        conexao,
        999,
    )

    assert resultado is None

    mock_obter_item.assert_called_once_with(
        conexao,
        999,
    )
    
@patch(
    "skinexa.services.catalogo.service."
    "obter_item_catalogo_por_nome_mercado",
)

def test_obter_item_por_nome_mercado(
    mock_obter_item,
):
    """Testa obtenção pelo nome de mercado."""

    conexao = Mock()

    mock_obter_item.return_value = (
        _criar_registro_item()
    )

    resultado = obter_item_por_nome_mercado(
        conexao,
        app_id=730,
        nome_mercado=(
            "AK-47 | Redline (Field-Tested)"
        ),
    )

    assert isinstance(
        resultado,
        ItemCatalogoDTO,
    )

    assert resultado.id == 1

    mock_obter_item.assert_called_once_with(
        conexao,
        app_id=730,
        nome_mercado=(
            "AK-47 | Redline (Field-Tested)"
        ),
    )
    
@patch(
    "skinexa.services.catalogo.service."
    "obter_item_catalogo_por_nome_mercado",
)

def test_obter_item_por_nome_mercado_inexistente(
    mock_obter_item,
):
    """Testa busca por nome de mercado inexistente."""

    conexao = Mock()

    mock_obter_item.return_value = None

    resultado = obter_item_por_nome_mercado(
        conexao,
        app_id=730,
        nome_mercado="Item inexistente",
    )

    assert resultado is None
    
@patch(
    "skinexa.services.catalogo.service."
    "listar_itens_catalogo",
)

def test_listar_itens(
    mock_listar_itens,
):
    """Testa listagem de itens do catálogo."""

    conexao = Mock()

    mock_listar_itens.return_value = [
        _criar_registro_item(
            item_id=1,
        ),
        _criar_registro_item(
            item_id=2,
            nome_mercado=(
                "AWP | Asiimov (Field-Tested)"
            ),
            nome_exibicao="AWP | Asiimov",
        ),
    ]

    resultado = listar_itens(
        conexao,
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

    mock_listar_itens.assert_called_once_with(
        conexao,
        limite=20,
        deslocamento=0,
    )
    
@patch(
    "skinexa.services.catalogo.service."
    "listar_itens_catalogo",
)

def test_listar_itens_sem_resultados(
    mock_listar_itens,
):
    """Testa listagem sem itens no catálogo."""

    conexao = Mock()

    mock_listar_itens.return_value = []

    resultado = listar_itens(
        conexao,
        limite=20,
        deslocamento=0,
    )

    assert resultado == []
    
@patch(
    "skinexa.services.catalogo.service."
    "contar_itens_catalogo",
)

def test_contar_itens(
    mock_contar_itens,
):
    """Testa contagem dos itens do catálogo."""

    conexao = Mock()

    mock_contar_itens.return_value = 150

    resultado = contar_itens(
        conexao
    )

    assert resultado == 150

    mock_contar_itens.assert_called_once_with(
        conexao
    )