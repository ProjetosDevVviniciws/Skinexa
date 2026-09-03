from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from contextlib import nullcontext

from skinexa.domain.preco import PrecoMercado
from skinexa.dto.skinport.preco import PrecoSkinportDTO
from skinexa.integrations.skinport.client import (
    ConsultaPrecosSkinport,
    SkinportIndisponivel
)

from skinexa.services.precos.service import (
    ResultadoRegistroPrecos,
)

from skinexa.services.precos.skinport import (
    coletar_precos_skinport,
    sincronizar_precos_skinport,
)

def _criar_preco_skinport() -> PrecoSkinportDTO:
    """Cria um preço Skinport para os testes."""

    return PrecoSkinportDTO(
        market_hash_name=(
            "AK-47 | Redline (Field-Tested)"
        ),
        currency="BRL",
        min_price=Decimal("145.50"),
        max_price=Decimal("230.00"),
        mean_price=Decimal("167.30"),
        median_price=Decimal("160.00"),
        quantity=42,
        updated_at=datetime(
            2026,
            9,
            1,
            12,
            30,
        ),
    )

def _criar_preco_normalizado() -> PrecoMercado:
    """Cria um preço interno para os testes."""

    return PrecoMercado(
        nome_mercado=(
            "AK-47 | Redline (Field-Tested)"
        ),
        plataforma="skinport",
        moeda="BRL",
        menor_preco=Decimal("145.50"),
        maior_preco=Decimal("230.00"),
        preco_medio=Decimal("167.30"),
        preco_mediano=Decimal("160.00"),
        maior_ordem_compra=None,
        quantidade_anuncios=42,
        volume_vendas=None,
        atualizado_na_origem_em=datetime(
            2026,
            9,
            1,
            12,
            30,
        ),
    )
    
@patch(
    "skinexa.services.precos.skinport."
    "registrar_precos",
)
@patch(
    "skinexa.services.precos.skinport."
    "normalizar_preco_skinport",
)
@patch(
    "skinexa.services.precos.skinport."
    "buscar_precos_skinport",
)

def test_coletar_precos_skinport_com_sucesso(
    mock_buscar_precos,
    mock_normalizar,
    mock_registrar_precos,
):
    """Testa a orquestração da coleta Skinport."""

    conexao = Mock()

    preco_dto = _criar_preco_skinport()
    preco_normalizado = _criar_preco_normalizado()

    mock_buscar_precos.return_value = (
        ConsultaPrecosSkinport(
            moeda="BRL",
            itens=(preco_dto,),
        )
    )

    mock_normalizar.return_value = (
        preco_normalizado
    )

    resultado_esperado = ResultadoRegistroPrecos(
        total_recebido=1,
        total_registrado=1,
        total_ignorado=0,
    )

    mock_registrar_precos.return_value = (
        resultado_esperado
    )

    resultado = coletar_precos_skinport(
        conexao,
        moeda="BRL",
    )

    assert resultado == resultado_esperado

    mock_buscar_precos.assert_called_once_with(
        moeda="BRL",
    )
    
@patch(
    "skinexa.services.precos.skinport."
    "registrar_precos",
)
@patch(
    "skinexa.services.precos.skinport."
    "normalizar_preco_skinport",
)
@patch(
    "skinexa.services.precos.skinport."
    "buscar_precos_skinport",
)
def test_coletar_precos_skinport_normaliza_itens(
    mock_buscar_precos,
    mock_normalizar,
    mock_registrar_precos,
):
    """Testa a normalização dos itens retornados."""

    conexao = Mock()

    preco_dto = _criar_preco_skinport()
    preco_normalizado = _criar_preco_normalizado()

    mock_buscar_precos.return_value = (
        ConsultaPrecosSkinport(
            moeda="BRL",
            itens=(preco_dto,),
        )
    )

    mock_normalizar.return_value = (
        preco_normalizado
    )

    resultado_esperado = ResultadoRegistroPrecos(
        total_recebido=1,
        total_registrado=1,
        total_ignorado=0,
    )

    def consumir_precos(
        conexao_recebida,
        precos,
    ):
        assert conexao_recebida is conexao

        lista_precos = list(precos)

        assert lista_precos == [
            preco_normalizado
        ]

        return resultado_esperado

    mock_registrar_precos.side_effect = (
        consumir_precos
    )

    resultado = coletar_precos_skinport(
        conexao,
    )

    assert resultado == resultado_esperado

    mock_normalizar.assert_called_once_with(
        preco_dto,
    )
    
@patch(
    "skinexa.services.precos.skinport."
    "registrar_precos",
)
@patch(
    "skinexa.services.precos.skinport."
    "normalizar_preco_skinport",
)
@patch(
    "skinexa.services.precos.skinport."
    "buscar_precos_skinport",
)
def test_coletar_precos_skinport_sem_itens(
    mock_buscar_precos,
    mock_normalizar,
    mock_registrar_precos,
):
    """Testa uma consulta Skinport sem itens."""

    conexao = Mock()

    mock_buscar_precos.return_value = (
        ConsultaPrecosSkinport(
            moeda="BRL",
            itens=(),
        )
    )

    resultado_esperado = ResultadoRegistroPrecos(
        total_recebido=0,
        total_registrado=0,
        total_ignorado=0,
    )

    def consumir_precos(
        conexao_recebida,
        precos,
    ):
        assert conexao_recebida is conexao
        assert list(precos) == []

        return resultado_esperado

    mock_registrar_precos.side_effect = (
        consumir_precos
    )

    resultado = coletar_precos_skinport(
        conexao,
    )

    assert resultado == resultado_esperado

    mock_normalizar.assert_not_called()
    
@patch(
    "skinexa.services.precos.skinport."
    "registrar_precos",
)
@patch(
    "skinexa.services.precos.skinport."
    "normalizar_preco_skinport",
)
@patch(
    "skinexa.services.precos.skinport."
    "buscar_precos_skinport",
)
@patch(
    "skinexa.services.precos.skinport."
    "engine.begin",
)

def test_sincronizar_precos_skinport_com_sucesso(
    mock_begin,
    mock_buscar_precos,
    mock_normalizar,
    mock_registrar_precos,
):
    """Testa a sincronização transacional da Skinport."""

    conexao = Mock()

    mock_begin.return_value = nullcontext(
        conexao
    )

    preco_dto = _criar_preco_skinport()
    preco_normalizado = _criar_preco_normalizado()

    mock_buscar_precos.return_value = (
        ConsultaPrecosSkinport(
            moeda="BRL",
            itens=(preco_dto,),
        )
    )

    mock_normalizar.return_value = (
        preco_normalizado
    )

    resultado_esperado = ResultadoRegistroPrecos(
        total_recebido=1,
        total_registrado=1,
        total_ignorado=0,
    )

    mock_registrar_precos.return_value = (
        resultado_esperado
    )

    resultado = sincronizar_precos_skinport(
        moeda="BRL",
    )

    assert resultado == resultado_esperado

    mock_buscar_precos.assert_called_once_with(
        moeda="BRL",
    )

    mock_normalizar.assert_called_once_with(
        preco_dto,
    )

    mock_begin.assert_called_once_with()

    mock_registrar_precos.assert_called_once_with(
        conexao,
        (preco_normalizado,),
    )
    
@patch(
    "skinexa.services.precos.skinport."
    "buscar_precos_skinport",
)
@patch(
    "skinexa.services.precos.skinport."
    "engine.begin",
)

def test_sincronizar_precos_skinport_nao_abre_transacao_se_api_falhar(
    mock_begin,
    mock_buscar_precos,
):
    """
    Testa que nenhuma transação é aberta
    quando a Skinport está indisponível.
    """

    mock_buscar_precos.side_effect = (
        SkinportIndisponivel(
            "Skinport indisponível."
        )
    )

    with pytest.raises(
        SkinportIndisponivel,
    ):
        sincronizar_precos_skinport()

    mock_begin.assert_not_called()