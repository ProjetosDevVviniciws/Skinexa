from decimal import Decimal

from unittest.mock import Mock, patch

import pytest

from skinexa.dto.catalogo.item import (
    ItemCatalogoDTO,
)

from skinexa.dto.catalogo.autocomplete import (
    SugestaoItemCatalogoDTO,
)

from skinexa.dto.catalogo.paginacao import (
    PaginaItensCatalogoDTO,
)

from skinexa.services.catalogo.pesquisa import (
    autocomplete_itens,
    filtrar_itens,
    listar_itens_paginados,
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
        
@patch(
    "skinexa.services.catalogo.pesquisa."
    "buscar_sugestoes_itens_catalogo",
)

def test_autocomplete_itens(
    mock_buscar_sugestoes,
):
    """Testa sugestões de itens para autocomplete."""

    conexao = Mock()

    mock_buscar_sugestoes.return_value = [
        {
            "id": 1,
            "nome_mercado": (
                "AK-47 | Redline (Field-Tested)"
            ),
            "nome_exibicao": "AK-47 | Redline",
            "tipo_item": "skin",
            "url_icone": "icone-1",
        },
        {
            "id": 2,
            "nome_mercado": (
                "AK-47 | Redline (Minimal Wear)"
            ),
            "nome_exibicao": "AK-47 | Redline",
            "tipo_item": "skin",
            "url_icone": "icone-2",
        },
    ]

    resultado = autocomplete_itens(
        conexao,
        termo="Redline",
        limite=8,
    )

    assert len(resultado) == 2

    assert all(
        isinstance(
            item,
            SugestaoItemCatalogoDTO,
        )
        for item in resultado
    )

    assert resultado[0].id == 1
    assert resultado[0].nome_mercado == (
        "AK-47 | Redline (Field-Tested)"
    )
    assert resultado[0].nome_exibicao == (
        "AK-47 | Redline"
    )
    assert resultado[0].tipo_item == "skin"
    assert resultado[0].url_icone == "icone-1"

    assert resultado[1].id == 2

    mock_buscar_sugestoes.assert_called_once_with(
        conexao,
        termo="Redline",
        limite=8,
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "buscar_sugestoes_itens_catalogo",
)

def test_autocomplete_itens_sem_resultados(
    mock_buscar_sugestoes,
):
    """Testa autocomplete sem sugestões."""

    conexao = Mock()

    mock_buscar_sugestoes.return_value = []

    resultado = autocomplete_itens(
        conexao,
        termo="Inexistente",
    )

    assert resultado == []

    mock_buscar_sugestoes.assert_called_once_with(
        conexao,
        termo="Inexistente",
        limite=10,
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "buscar_sugestoes_itens_catalogo",
)

def test_autocomplete_itens_sem_icone(
    mock_buscar_sugestoes,
):
    """Testa sugestão sem URL de ícone."""

    conexao = Mock()

    mock_buscar_sugestoes.return_value = [
        {
            "id": 1,
            "nome_mercado": (
                "AK-47 | Redline (Field-Tested)"
            ),
            "nome_exibicao": "AK-47 | Redline",
            "tipo_item": "skin",
            "url_icone": None,
        }
    ]

    resultado = autocomplete_itens(
        conexao,
        termo="Redline",
    )

    assert len(resultado) == 1
    assert resultado[0].url_icone is None
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "filtrar_itens_catalogo",
)

def test_filtrar_itens(
    mock_filtrar_itens,
):
    """Testa filtragem de itens do catálogo."""

    conexao = Mock()

    mock_filtrar_itens.return_value = [
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

    resultado = filtrar_itens(
        conexao,
        tipo_item="skin",
        nome_arma="AK-47",
        nome_acabamento="Redline",
        raridade="Classified",
        colecao="The Phoenix Collection",
        variante_stattrak=False,
        limite=25,
        deslocamento=50,
        ordenacao="nome_asc",
    )

    assert len(resultado) == 2

    assert all(
        isinstance(item, ItemCatalogoDTO)
        for item in resultado
    )

    assert resultado[0].id == 1
    assert resultado[1].id == 2

    mock_filtrar_itens.assert_called_once_with(
        conexao,
        tipo_item="skin",
        nome_arma="AK-47",
        nome_acabamento="Redline",
        estado_exterior=None,
        raridade="Classified",
        colecao="The Phoenix Collection",
        variante_stattrak=False,
        variante_souvenir=None,
        limite=25,
        deslocamento=50,
        ordenacao="nome_asc",
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "filtrar_itens_catalogo",
)

def test_filtrar_itens_sem_resultados(
    mock_filtrar_itens,
):
    """Testa filtragem sem itens encontrados."""

    conexao = Mock()

    mock_filtrar_itens.return_value = []

    resultado = filtrar_itens(
        conexao,
        tipo_item="luva",
    )

    assert resultado == []

    mock_filtrar_itens.assert_called_once_with(
        conexao,
        tipo_item="luva",
        nome_arma=None,
        nome_acabamento=None,
        estado_exterior=None,
        raridade=None,
        colecao=None,
        variante_stattrak=None,
        variante_souvenir=None,
        limite=20,
        deslocamento=0,
        ordenacao="nome_asc",
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "filtrar_itens_catalogo",
)

def test_filtrar_itens_sem_filtros(
    mock_filtrar_itens,
):
    """Testa filtragem sem filtros específicos."""

    conexao = Mock()

    mock_filtrar_itens.return_value = []

    resultado = filtrar_itens(
        conexao,
    )

    assert resultado == []

    mock_filtrar_itens.assert_called_once_with(
        conexao,
        tipo_item=None,
        nome_arma=None,
        nome_acabamento=None,
        estado_exterior=None,
        raridade=None,
        colecao=None,
        variante_stattrak=None,
        variante_souvenir=None,
        limite=20,
        deslocamento=0,
        ordenacao="nome_asc",
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "listar_itens_catalogo",
)
@patch(
    "skinexa.services.catalogo.pesquisa."
    "contar_itens_catalogo",
)

def test_listar_itens_paginados(
    mock_contar_itens,
    mock_listar_itens,
):
    """Testa listagem paginada do catálogo."""

    conexao = Mock()

    mock_contar_itens.return_value = 45

    mock_listar_itens.return_value = [
        _criar_registro_item(
            item_id=1,
        ),
        _criar_registro_item(
            item_id=2,
        ),
    ]

    resultado = listar_itens_paginados(
        conexao,
        pagina=1,
        por_pagina=20,
        ordenacao="nome_asc",
    )

    assert isinstance(
        resultado,
        PaginaItensCatalogoDTO,
    )

    assert len(resultado.itens) == 2
    assert resultado.pagina == 1
    assert resultado.por_pagina == 20
    assert resultado.total_itens == 45
    assert resultado.total_paginas == 3
    assert resultado.tem_anterior is False
    assert resultado.tem_proxima is True

    mock_contar_itens.assert_called_once_with(
        conexao,
    )

    mock_listar_itens.assert_called_once_with(
        conexao,
        limite=20,
        deslocamento=0,
        ordenacao="nome_asc",
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "listar_itens_catalogo",
)
@patch(
    "skinexa.services.catalogo.pesquisa."
    "contar_itens_catalogo",
)

def test_listar_itens_paginados_pagina_intermediaria(
    mock_contar_itens,
    mock_listar_itens,
):
    """Testa cálculo do deslocamento da paginação."""

    conexao = Mock()

    mock_contar_itens.return_value = 100
    mock_listar_itens.return_value = []

    resultado = listar_itens_paginados(
        conexao,
        pagina=3,
        por_pagina=20,
        ordenacao="mais_recentes",
    )

    assert resultado.pagina == 3
    assert resultado.total_paginas == 5
    assert resultado.tem_anterior is True
    assert resultado.tem_proxima is True

    mock_listar_itens.assert_called_once_with(
        conexao,
        limite=20,
        deslocamento=40,
        ordenacao="mais_recentes",
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "listar_itens_catalogo",
)
@patch(
    "skinexa.services.catalogo.pesquisa."
    "contar_itens_catalogo",
)

def test_listar_itens_paginados_ultima_pagina(
    mock_contar_itens,
    mock_listar_itens,
):
    """Testa última página da listagem."""

    conexao = Mock()

    mock_contar_itens.return_value = 41
    mock_listar_itens.return_value = []

    resultado = listar_itens_paginados(
        conexao,
        pagina=3,
        por_pagina=20,
    )

    assert resultado.total_paginas == 3
    assert resultado.tem_anterior is True
    assert resultado.tem_proxima is False

    mock_listar_itens.assert_called_once_with(
        conexao,
        limite=20,
        deslocamento=40,
        ordenacao="nome_asc",
    )
    
@patch(
    "skinexa.services.catalogo.pesquisa."
    "listar_itens_catalogo",
)
@patch(
    "skinexa.services.catalogo.pesquisa."
    "contar_itens_catalogo",
)

def test_listar_itens_paginados_catalogo_vazio(
    mock_contar_itens,
    mock_listar_itens,
):
    """Testa paginação quando o catálogo está vazio."""

    conexao = Mock()

    mock_contar_itens.return_value = 0
    mock_listar_itens.return_value = []

    resultado = listar_itens_paginados(
        conexao,
    )

    assert resultado.itens == []
    assert resultado.pagina == 1
    assert resultado.total_itens == 0
    assert resultado.total_paginas == 0
    assert resultado.tem_anterior is False
    assert resultado.tem_proxima is False
    
def test_listar_itens_paginados_com_pagina_invalida():
    """Rejeita número de página inválido."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="A página deve ser maior que zero.",
    ):
        listar_itens_paginados(
            conexao,
            pagina=0,
        )
        
def test_listar_itens_paginados_com_por_pagina_invalido():
    """Rejeita quantidade por página inválida."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match=(
            "A quantidade por página "
            "deve ser maior que zero."
        ),
    ):
        listar_itens_paginados(
            conexao,
            por_pagina=0,
        )
        
def test_listar_itens_paginados_com_por_pagina_acima_do_limite():
    """Rejeita quantidade por página acima do limite máximo."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match=(
            "A quantidade por página "
            "não pode ser maior que 100."
        ),
    ):
        listar_itens_paginados(
            conexao,
            por_pagina=101,
        )
        
@patch(
    "skinexa.services.catalogo.pesquisa."
    "listar_itens_catalogo",
)
@patch(
    "skinexa.services.catalogo.pesquisa."
    "contar_itens_catalogo",
)

def test_listar_itens_paginados_aceita_limite_maximo(
    mock_contar_itens,
    mock_listar_itens,
):
    """Aceita a quantidade máxima permitida por página."""

    conexao = Mock()

    mock_contar_itens.return_value = 250
    mock_listar_itens.return_value = []

    resultado = listar_itens_paginados(
        conexao,
        pagina=2,
        por_pagina=100,
    )

    assert resultado.por_pagina == 100
    assert resultado.total_itens == 250
    assert resultado.total_paginas == 3

    mock_listar_itens.assert_called_once_with(
        conexao,
        limite=100,
        deslocamento=100,
        ordenacao="nome_asc",
    )