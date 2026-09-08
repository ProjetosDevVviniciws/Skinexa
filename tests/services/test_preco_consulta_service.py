from contextlib import nullcontext
from decimal import Decimal
from unittest.mock import Mock, patch

from skinexa.domain.preco import UltimoPrecoMercado
from skinexa.services.precos.consulta import (
    consultar_ultimos_precos,
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