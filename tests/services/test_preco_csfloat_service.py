from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from skinexa.domain.preco import PrecoMercado

from skinexa.dto.cambio.cotacao import (
    CotacaoCambioDTO,
)

from skinexa.dto.csfloat.preco import (
    PrecoCSFloatDTO,
)

from skinexa.integrations.csfloat.client import (
    ConsultaPrecosCSFloat,
)

from skinexa.services.precos.csfloat import (
    coletar_preco_csfloat,
    sincronizar_preco_csfloat,
)

from skinexa.services.precos.service import (
    ResultadoRegistroPrecos,
)

def _criar_consulta_csfloat() -> ConsultaPrecosCSFloat:
    """Cria uma consulta CSFloat para uso nos testes."""

    return ConsultaPrecosCSFloat(
        nome_mercado=(
            "M4A1-S | Nitro (Factory New)"
        ),
        itens=(
            PrecoCSFloatDTO(
                market_hash_name=(
                    "M4A1-S | Nitro "
                    "(Factory New)"
                ),
                preco=Decimal("15.00"),
                criado_em=None,
            ),
            PrecoCSFloatDTO(
                market_hash_name=(
                    "M4A1-S | Nitro "
                    "(Factory New)"
                ),
                preco=Decimal("20.00"),
                criado_em=None,
            ),
        ),
    )

def _criar_cotacao() -> CotacaoCambioDTO:
    """Cria uma cotação USD/BRL para uso nos testes."""

    return CotacaoCambioDTO(
        moeda_origem="USD",
        moeda_destino="BRL",
        taxa=Decimal("5.00"),
        cotado_em=None,
    )

def _criar_preco_mercado() -> PrecoMercado:
    """Cria um preço de mercado para uso nos testes."""

    return PrecoMercado(
        nome_mercado=(
            "M4A1-S | Nitro (Factory New)"
        ),
        plataforma="csfloat",
        moeda="BRL",
        menor_preco=Decimal("75.00"),
        maior_preco=Decimal("100.00"),
        preco_medio=Decimal("87.50"),
        preco_mediano=Decimal("87.50"),
        maior_ordem_compra=None,
        quantidade_anuncios=2,
        volume_vendas=None,
        atualizado_na_origem_em=None,
    )

@patch(
    "skinexa.services.precos.csfloat."
    "normalizar_precos_csfloat",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_cotacao_usd_brl",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_precos_csfloat",
)

def test_coletar_preco_csfloat_com_sucesso(
    mock_buscar_precos,
    mock_buscar_cotacao,
    mock_normalizar,
):
    """Testa a coleta e normalização de preço da CSFloat."""

    consulta = _criar_consulta_csfloat()
    cotacao = _criar_cotacao()
    preco = _criar_preco_mercado()

    mock_buscar_precos.return_value = consulta
    mock_buscar_cotacao.return_value = cotacao
    mock_normalizar.return_value = preco

    resultado = coletar_preco_csfloat(
        nome_mercado=(
            "M4A1-S | Nitro (Factory New)"
        ),
    )

    assert resultado == preco

    mock_buscar_precos.assert_called_once_with(
        nome_mercado=(
            "M4A1-S | Nitro (Factory New)"
        ),
    )

    mock_buscar_cotacao.assert_called_once_with()

    mock_normalizar.assert_called_once_with(
        consulta.itens,
        taxa_usd_brl=Decimal("5.00"),
    )

@patch(
    "skinexa.services.precos.csfloat."
    "normalizar_precos_csfloat",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_cotacao_usd_brl",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_precos_csfloat",
)

def test_coletar_preco_csfloat_sem_anuncios(
    mock_buscar_precos,
    mock_buscar_cotacao,
    mock_normalizar,
):
    """Testa coleta quando a CSFloat não possui anúncios."""

    mock_buscar_precos.return_value = (
        ConsultaPrecosCSFloat(
            nome_mercado="AK-47 | Redline",
            itens=(),
        )
    )

    resultado = coletar_preco_csfloat(
        nome_mercado="AK-47 | Redline",
    )

    assert resultado is None

    mock_buscar_cotacao.assert_not_called()
    mock_normalizar.assert_not_called()

@patch(
    "skinexa.services.precos.csfloat."
    "registrar_precos",
)
@patch(
    "skinexa.services.precos.csfloat."
    "engine.begin",
)
@patch(
    "skinexa.services.precos.csfloat."
    "normalizar_precos_csfloat",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_cotacao_usd_brl",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_precos_csfloat",
)

def test_sincronizar_preco_csfloat_com_sucesso(
    mock_buscar_precos,
    mock_buscar_cotacao,
    mock_normalizar,
    mock_begin,
    mock_registrar,
):
    """Testa sincronização completa do preço da CSFloat."""

    consulta = _criar_consulta_csfloat()
    cotacao = _criar_cotacao()
    preco = _criar_preco_mercado()

    mock_buscar_precos.return_value = consulta
    mock_buscar_cotacao.return_value = cotacao
    mock_normalizar.return_value = preco

    resultado_registro = ResultadoRegistroPrecos(
        total_recebido=1,
        total_registrado=1,
        total_ignorado=0,
    )

    mock_registrar.return_value = resultado_registro

    conexao = Mock()

    contexto = Mock()
    contexto.__enter__ = Mock(
        return_value=conexao,
    )
    contexto.__exit__ = Mock(
        return_value=None,
    )

    mock_begin.return_value = contexto

    resultado = sincronizar_preco_csfloat(
        nome_mercado=(
            "M4A1-S | Nitro (Factory New)"
        ),
    )

    assert resultado.nome_mercado == (
        "M4A1-S | Nitro (Factory New)"
    )

    assert resultado.total_anuncios == 2
    assert (
        resultado.resultado_registro
        == resultado_registro
    )

    mock_buscar_precos.assert_called_once_with(
        nome_mercado=(
            "M4A1-S | Nitro (Factory New)"
        ),
    )

    mock_buscar_cotacao.assert_called_once_with()

    mock_normalizar.assert_called_once_with(
        consulta.itens,
        taxa_usd_brl=Decimal("5.00"),
    )

    mock_begin.assert_called_once_with()

    mock_registrar.assert_called_once_with(
        conexao,
        [preco],
    )

@patch(
    "skinexa.services.precos.csfloat."
    "registrar_precos",
)
@patch(
    "skinexa.services.precos.csfloat."
    "engine.begin",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_cotacao_usd_brl",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_precos_csfloat",
)

def test_sincronizar_preco_csfloat_sem_anuncios(
    mock_buscar_precos,
    mock_buscar_cotacao,
    mock_begin,
    mock_registrar,
):
    """Testa sincronização quando não existem anúncios."""

    mock_buscar_precos.return_value = (
        ConsultaPrecosCSFloat(
            nome_mercado="AK-47 | Redline",
            itens=(),
        )
    )

    resultado = sincronizar_preco_csfloat(
        nome_mercado="AK-47 | Redline",
    )

    assert resultado.nome_mercado == (
        "AK-47 | Redline"
    )

    assert resultado.total_anuncios == 0

    assert (
        resultado.resultado_registro.total_recebido
        == 0
    )

    assert (
        resultado.resultado_registro.total_registrado
        == 0
    )

    assert (
        resultado.resultado_registro.total_ignorado
        == 0
    )

    mock_buscar_cotacao.assert_not_called()
    mock_begin.assert_not_called()
    mock_registrar.assert_not_called()

@patch(
    "skinexa.services.precos.csfloat."
    "engine.begin",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_cotacao_usd_brl",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_precos_csfloat",
)

def test_sincronizar_preco_csfloat_nao_abre_transacao_se_csfloat_falhar(
    mock_buscar_precos,
    mock_buscar_cotacao,
    mock_begin,
):
    """Testa que falha da CSFloat ocorre antes da transação."""

    mock_buscar_precos.side_effect = RuntimeError(
        "Falha na CSFloat."
    )

    with pytest.raises(
        RuntimeError,
        match="Falha na CSFloat",
    ):
        sincronizar_preco_csfloat(
            nome_mercado="AK-47 | Redline",
        )

    mock_buscar_cotacao.assert_not_called()
    mock_begin.assert_not_called()

@patch(
    "skinexa.services.precos.csfloat."
    "engine.begin",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_cotacao_usd_brl",
)
@patch(
    "skinexa.services.precos.csfloat."
    "buscar_precos_csfloat",
)

def test_sincronizar_preco_csfloat_nao_abre_transacao_se_bcb_falhar(
    mock_buscar_precos,
    mock_buscar_cotacao,
    mock_begin,
):
    """Testa que falha do BCB ocorre antes da transação."""

    mock_buscar_precos.return_value = (
        _criar_consulta_csfloat()
    )

    mock_buscar_cotacao.side_effect = RuntimeError(
        "Falha no BCB."
    )

    with pytest.raises(
        RuntimeError,
        match="Falha no BCB",
    ):
        sincronizar_preco_csfloat(
            nome_mercado=(
                "M4A1-S | Nitro (Factory New)"
            ),
        )

    mock_begin.assert_not_called()