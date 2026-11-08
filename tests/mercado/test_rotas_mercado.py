from datetime import datetime

from decimal import Decimal

from unittest.mock import Mock, patch

from types import SimpleNamespace

from skinexa.domain.comparacao_preco import (
    PrecoComparacao,
)

from skinexa.dto.catalogo.paginacao import (
    PaginaItensCatalogoDTO,
)

@patch(
    "skinexa.blueprints.mercado.routes."
    "consultar_comparacao_precos",
)

def test_precos_item_retorna_comparacao(
    mock_consultar_comparacao_precos,
    client,
):
    """Testa o retorno dos preços de diferentes marketplaces."""

    mock_consultar_comparacao_precos.return_value = (
        PrecoComparacao(
            plataforma="skinport",
            moeda="BRL",
            menor_preco=Decimal("103.16"),
            maior_preco=Decimal("150.00"),
            preco_medio=Decimal("120.50"),
            preco_mediano=Decimal("118.00"),
            maior_ordem_compra=None,
            quantidade_anuncios=134,
            volume_vendas=None,
            coletado_em=datetime(
                2026,
                9,
                17,
                14,
                30,
            ),
            atualizado_na_origem_em=datetime(
                2026,
                9,
                17,
                14,
                25,
            ),
        ),
        PrecoComparacao(
            plataforma="csfloat",
            moeda="BRL",
            menor_preco=Decimal("98.40"),
            maior_preco=Decimal("145.00"),
            preco_medio=Decimal("115.00"),
            preco_mediano=Decimal("110.00"),
            maior_ordem_compra=None,
            quantidade_anuncios=42,
            volume_vendas=None,
            coletado_em=datetime(
                2026,
                9,
                17,
                14,
                31,
            ),
            atualizado_na_origem_em=None,
        ),
    )

    resposta = client.get(
        "/mercado/item/153/precos",
    )

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados == {
        "item_catalogo_id": 153,
        "mercados": [
            {
                "plataforma": "skinport",
                "moeda": "BRL",
                "menor_preco": "103.16",
                "maior_preco": "150.00",
                "preco_medio": "120.50",
                "preco_mediano": "118.00",
                "maior_ordem_compra": None,
                "quantidade_anuncios": 134,
                "volume_vendas": None,
                "coletado_em": (
                    "2026-09-17T14:30:00"
                ),
                "atualizado_na_origem_em": (
                    "2026-09-17T14:25:00"
                ),
            },
            {
                "plataforma": "csfloat",
                "moeda": "BRL",
                "menor_preco": "98.40",
                "maior_preco": "145.00",
                "preco_medio": "115.00",
                "preco_mediano": "110.00",
                "maior_ordem_compra": None,
                "quantidade_anuncios": 42,
                "volume_vendas": None,
                "coletado_em": (
                    "2026-09-17T14:31:00"
                ),
                "atualizado_na_origem_em": None,
            },
        ],
    }

    mock_consultar_comparacao_precos.assert_called_once_with(
        item_catalogo_id=153,
    )
    
@patch(
    "skinexa.blueprints.mercado.routes."
    "consultar_comparacao_precos",
)

def test_precos_item_sem_precos_retorna_lista_vazia(
    mock_consultar_comparacao_precos,
    client,
):
    """Testa item sem preços coletados."""

    mock_consultar_comparacao_precos.return_value = ()

    resposta = client.get(
        "/mercado/item/153/precos",
    )

    assert resposta.status_code == 200

    assert resposta.get_json() == {
        "item_catalogo_id": 153,
        "mercados": [],
    }

    mock_consultar_comparacao_precos.assert_called_once_with(
        item_catalogo_id=153,
    )
    
@patch(
    "skinexa.blueprints.mercado.routes."
    "listar_itens_paginados",
)
@patch(
    "skinexa.blueprints.mercado.routes.engine",
)

def test_mercado_index_renderiza_resultados(
    mock_engine,
    mock_listar_itens,
    client,
):
    """Testa a renderização da página de resultados."""

    conexao = Mock()

    mock_engine.connect.return_value.__enter__ = Mock(
        return_value=conexao,
    )

    mock_engine.connect.return_value.__exit__ = Mock(
        return_value=False,
    )

    mock_listar_itens.return_value = PaginaItensCatalogoDTO(
        itens=[],
        pagina=1,
        por_pagina=20,
        total_itens=35,
        total_paginas=2,
        tem_anterior=False,
        tem_proxima=True,
    )

    resposta = client.get("/mercado/")

    assert resposta.status_code == 200

    html = resposta.get_data(as_text=True)

    assert "Mercado" in html
    assert "35" in html
    assert "Página" in html

    mock_listar_itens.assert_called_once_with(
        conexao,
        pagina=1,
        por_pagina=20,
        ordenacao="nome_asc",
    )
    
@patch(
    "skinexa.blueprints.mercado.routes."
    "listar_itens_paginados",
)
@patch(
    "skinexa.blueprints.mercado.routes.engine",
)

def test_mercado_index_com_parametros(
    mock_engine,
    mock_listar_itens,
    client,
):
    """Testa paginação e ordenação recebidas pela rota."""

    conexao = Mock()

    mock_engine.connect.return_value.__enter__ = Mock(
        return_value=conexao,
    )

    mock_engine.connect.return_value.__exit__ = Mock(
        return_value=False,
    )

    mock_listar_itens.return_value = PaginaItensCatalogoDTO(
        itens=[],
        pagina=2,
        por_pagina=10,
        total_itens=35,
        total_paginas=4,
        tem_anterior=True,
        tem_proxima=True,
    )

    resposta = client.get(
        "/mercado/?pagina=2"
        "&por_pagina=10"
        "&ordenacao=mais_recentes"
    )

    assert resposta.status_code == 200

    mock_listar_itens.assert_called_once_with(
        conexao,
        pagina=2,
        por_pagina=10,
        ordenacao="mais_recentes",
    )
    
@patch(
    "skinexa.blueprints.mercado.routes."
    "listar_itens_paginados",
)
@patch(
    "skinexa.blueprints.mercado.routes.engine",
)

def test_mercado_index_parametros_nao_numericos(
    mock_engine,
    mock_listar_itens,
    client,
):
    """Testa os valores padrão para parâmetros não numéricos."""

    conexao = Mock()

    mock_engine.connect.return_value.__enter__ = Mock(
        return_value=conexao,
    )

    mock_engine.connect.return_value.__exit__ = Mock(
        return_value=False,
    )

    mock_listar_itens.return_value = PaginaItensCatalogoDTO(
        itens=[],
        pagina=1,
        por_pagina=20,
        total_itens=0,
        total_paginas=0,
        tem_anterior=False,
        tem_proxima=False,
    )

    resposta = client.get(
        "/mercado/?pagina=abc&por_pagina=xyz"
    )

    assert resposta.status_code == 200

    mock_listar_itens.assert_called_once_with(
        conexao,
        pagina=1,
        por_pagina=20,
        ordenacao="nome_asc",
    )    

@patch(
    "skinexa.blueprints.mercado.routes."
    "listar_itens_paginados",
)
@patch(
    "skinexa.blueprints.mercado.routes.engine",
)

def test_mercado_api_retorna_itens_paginados(
    mock_engine,
    mock_listar_itens,
    client,
):
    """Retorna itens reais do serviço no contrato JSON do Mercado."""

    conexao = Mock()

    mock_engine.connect.return_value.__enter__ = Mock(
        return_value=conexao,
    )
    mock_engine.connect.return_value.__exit__ = Mock(
        return_value=False,
    )

    item = SimpleNamespace(
        id=153,
        nome_exibicao="AK-47 | Teste",
        tipo_item="skin",
        nome_arma="AK-47",
        nome_acabamento="Teste",
        estado_exterior="Factory New",
        raridade="Covert",
        url_icone=None,
        url_icone_grande="https://exemplo.com/item.png",
        variante_stattrak=True,
        variante_souvenir=False,
    )

    mock_listar_itens.return_value = PaginaItensCatalogoDTO(
        itens=[item],
        pagina=2,
        por_pagina=20,
        total_itens=45,
        total_paginas=3,
        tem_anterior=True,
        tem_proxima=True,
    )

    resposta = client.get(
        "/mercado/itens"
        "?pagina=2&ordenacao=mais_recentes"
    )

    assert resposta.status_code == 200
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["ordenacao"] == "mais_recentes"
    assert dados["paginacao"] == {
        "pagina": 2,
        "por_pagina": 20,
        "total_itens": 45,
        "total_paginas": 3,
        "tem_anterior": True,
        "tem_proxima": True,
    }

    assert dados["itens"] == [
        {
            "id": 153,
            "nome_exibicao": "AK-47 | Teste",
            "tipo_item": "skin",
            "nome_arma": "AK-47",
            "nome_acabamento": "Teste",
            "estado_exterior": "Factory New",
            "raridade": "Covert",
            "cor_raridade": "#EB4B4B",
            "url_icone": None,
            "url_icone_grande": (
                "https://exemplo.com/item.png"
            ),
            "variante_stattrak": True,
            "variante_souvenir": False,
            "url_detalhes": "/mercado/item/153",
        }
    ]

    mock_listar_itens.assert_called_once_with(
        conexao,
        pagina=2,
        por_pagina=20,
        ordenacao="mais_recentes",
    )

@patch(
    "skinexa.blueprints.mercado.routes."
    "listar_itens_paginados",
)
@patch(
    "skinexa.blueprints.mercado.routes.engine",
)

def test_mercado_api_retorna_lista_vazia(
    mock_engine,
    mock_listar_itens,
    client,
):
    """Retorna uma resposta válida quando não existem itens."""

    conexao = Mock()

    mock_engine.connect.return_value.__enter__ = Mock(
        return_value=conexao,
    )
    mock_engine.connect.return_value.__exit__ = Mock(
        return_value=False,
    )

    mock_listar_itens.return_value = PaginaItensCatalogoDTO(
        itens=[],
        pagina=1,
        por_pagina=20,
        total_itens=0,
        total_paginas=0,
        tem_anterior=False,
        tem_proxima=False,
    )

    resposta = client.get("/mercado/itens")

    assert resposta.status_code == 200

    dados = resposta.get_json()

    assert dados["itens"] == []
    assert dados["paginacao"]["total_itens"] == 0
    assert dados["paginacao"]["total_paginas"] == 0

@patch(
    "skinexa.blueprints.mercado.routes."
    "listar_itens_paginados",
)

def test_mercado_api_rejeita_ordenacao_invalida(
    mock_listar_itens,
    client,
):
    """Rejeita ordenações desconhecidas antes de consultar o banco."""

    resposta = client.get(
        "/mercado/itens?ordenacao=invalida"
    )

    assert resposta.status_code == 400
    assert resposta.is_json

    dados = resposta.get_json()

    assert dados["sucesso"] is False
    assert "inválidos" in dados["mensagem"]

    mock_listar_itens.assert_not_called()  

@patch(
    "skinexa.blueprints.mercado.routes."
    "listar_itens_paginados",
)
@patch(
    "skinexa.blueprints.mercado.routes.engine",
)

def test_mercado_index_catalogo_vazio(
    mock_engine,
    mock_listar_itens,
    client,
):
    """Exibe o Empty State quando o catálogo não possui itens."""

    conexao = Mock()

    mock_engine.connect.return_value.__enter__ = Mock(
        return_value=conexao,
    )
    mock_engine.connect.return_value.__exit__ = Mock(
        return_value=False,
    )

    mock_listar_itens.return_value = PaginaItensCatalogoDTO(
        itens=[],
        pagina=1,
        por_pagina=20,
        total_itens=0,
        total_paginas=0,
        tem_anterior=False,
        tem_proxima=False,
    )

    resposta = client.get("/mercado/")

    assert resposta.status_code == 200

    html = resposta.get_data(as_text=True)

    assert "Nenhum item disponível" in html
    assert "market-empty" in html
    assert "Voltar à primeira página" not in html

@patch(
    "skinexa.blueprints.mercado.routes."
    "listar_itens_paginados",
)
@patch(
    "skinexa.blueprints.mercado.routes.engine",
)

def test_mercado_index_pagina_fora_do_intervalo(
    mock_engine,
    mock_listar_itens,
    client,
):
    """Exibe o Empty State para páginas sem itens."""

    conexao = Mock()

    mock_engine.connect.return_value.__enter__ = Mock(
        return_value=conexao,
    )
    mock_engine.connect.return_value.__exit__ = Mock(
        return_value=False,
    )

    mock_listar_itens.return_value = PaginaItensCatalogoDTO(
        itens=[],
        pagina=99999,
        por_pagina=20,
        total_itens=45388,
        total_paginas=2270,
        tem_anterior=True,
        tem_proxima=False,
    )

    resposta = client.get(
        "/mercado/?pagina=99999"
    )

    assert resposta.status_code == 200

    html = resposta.get_data(as_text=True)

    assert "Página não encontrada no catálogo" in html
    assert "Voltar à primeira página" in html
    assert "market-empty-action" in html
    assert "market-grid" not in html

    mock_listar_itens.assert_called_once_with(
        conexao,
        pagina=99999,
        por_pagina=20,
        ordenacao="nome_asc",
    )