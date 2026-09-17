from contextlib import nullcontext

from decimal import Decimal

from datetime import datetime

from unittest.mock import Mock, patch

from skinexa.domain.preco import UltimoPrecoMercado

from skinexa.services.precos.consulta import (
    consultar_ultimos_precos,
    consultar_comparacao_precos,
)

from skinexa.domain.comparacao_preco import (
    PrecoComparacao,
)

@patch(
    "skinexa.services.precos.consulta."
    "obter_ultimos_precos",
)
@patch(
    "skinexa.services.precos.consulta."
    "engine.connect",
)

def test_consultar_ultimos_precos_com_sucesso(
    mock_connect,
    mock_obter_precos,
):
    """Testa consulta dos últimos preços."""

    conexao = Mock()

    mock_connect.return_value = nullcontext(
        conexao
    )

    preco = UltimoPrecoMercado(
        item_catalogo_id=1,
        plataforma="skinport",
        moeda="BRL",
        menor_preco=Decimal("75.18"),
        maior_preco=Decimal("7364.27"),
        preco_medio=Decimal("424.00"),
        preco_mediano=Decimal("143.05"),
        maior_ordem_compra=None,
        quantidade_anuncios=134,
        volume_vendas=None,
        coletado_em=Mock(),
        atualizado_na_origem_em=Mock(),
    )

    mock_obter_precos.return_value = {
        1: preco,
    }

    resultado = consultar_ultimos_precos(
        item_catalogo_ids={1},
        plataforma="skinport",
    )

    assert resultado == {
        1: preco,
    }

    mock_connect.assert_called_once_with()

    mock_obter_precos.assert_called_once_with(
        conexao,
        item_catalogo_ids={1},
        plataforma="skinport",
    )

@patch(
    "skinexa.services.precos.consulta."
    "obter_ultimos_precos",
)
@patch(
    "skinexa.services.precos.consulta."
    "engine.connect",
)

def test_consultar_ultimos_precos_sem_itens(
    mock_connect,
    mock_obter_precos,
):
    """Testa consulta sem itens."""

    resultado = consultar_ultimos_precos(
        item_catalogo_ids=set(),
        plataforma="skinport",
    )

    assert resultado == {}

    mock_connect.assert_not_called()
    mock_obter_precos.assert_not_called()
    
@patch(
    "skinexa.services.precos.consulta."
    "obter_comparacao_precos",
)
@patch(
    "skinexa.services.precos.consulta."
    "engine.connect",
)

def test_consultar_comparacao_precos(
    mock_connect,
    mock_obter_comparacao,
):
    """Testa consulta de comparação de preços."""

    conexao = Mock()

    mock_connect.return_value.__enter__.return_value = (
        conexao
    )

    coletado_em = datetime(
        2026,
        9,
        16,
        14,
        0,
    )

    comparacao = (
        PrecoComparacao(
            plataforma="skinport",
            moeda="BRL",
            menor_preco=Decimal("103.16"),
            maior_preco=Decimal("150.00"),
            preco_medio=Decimal("120.00"),
            preco_mediano=Decimal("115.00"),
            maior_ordem_compra=None,
            quantidade_anuncios=134,
            volume_vendas=None,
            coletado_em=coletado_em,
            atualizado_na_origem_em=None,
        ),
    )

    mock_obter_comparacao.return_value = (
        comparacao
    )

    resultado = consultar_comparacao_precos(
        item_catalogo_id=1,
    )

    assert resultado == comparacao

    mock_connect.assert_called_once_with()

    mock_obter_comparacao.assert_called_once_with(
        conexao,
        item_catalogo_id=1,
    )
    
@patch(
    "skinexa.services.precos.consulta."
    "obter_comparacao_precos",
)
@patch(
    "skinexa.services.precos.consulta."
    "engine.connect",
)

def test_consultar_comparacao_precos_sem_historico(
    mock_connect,
    mock_obter_comparacao,
):
    """Testa consulta quando não existem preços."""

    conexao = Mock()

    mock_connect.return_value.__enter__.return_value = (
        conexao
    )

    mock_obter_comparacao.return_value = ()

    resultado = consultar_comparacao_precos(
        item_catalogo_id=999,
    )

    assert resultado == ()

    mock_connect.assert_called_once_with()

    mock_obter_comparacao.assert_called_once_with(
        conexao,
        item_catalogo_id=999,
    )