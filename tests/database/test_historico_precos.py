from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

import pytest

from skinexa.database.queries.historico_precos import (
    inserir_historico_preco,
    obter_item_catalogo_id_por_nome_mercado,
    obter_plataforma_mercado_id_por_identificador,
    obter_itens_catalogo_ids_por_nomes_mercado,
)

def test_obter_item_catalogo_id_por_nome_mercado():
    """Testa a obtenção do ID de um item do catálogo."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one_or_none.return_value = 15

    conexao.execute.return_value = resultado_execute

    resultado = obter_item_catalogo_id_por_nome_mercado(
        conexao,
        "AK-47 | Redline (Field-Tested)",
    )

    assert resultado == 15

    conexao.execute.assert_called_once()

def test_obter_item_catalogo_id_inexistente():
    """Testa a busca por um item inexistente no catálogo."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one_or_none.return_value = None

    conexao.execute.return_value = resultado_execute

    resultado = obter_item_catalogo_id_por_nome_mercado(
        conexao,
        "Item inexistente",
    )

    assert resultado is None

    conexao.execute.assert_called_once()

def test_obter_plataforma_mercado_id_por_identificador():
    """Testa a obtenção do ID de uma plataforma ativa."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one_or_none.return_value = 2

    conexao.execute.return_value = resultado_execute

    resultado = (
        obter_plataforma_mercado_id_por_identificador(
            conexao,
            "skinport",
        )
    )

    assert resultado == 2

    conexao.execute.assert_called_once()

def test_obter_plataforma_mercado_inexistente():
    """Testa a busca por uma plataforma inexistente."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one_or_none.return_value = None

    conexao.execute.return_value = resultado_execute

    resultado = (
        obter_plataforma_mercado_id_por_identificador(
            conexao,
            "skinport",
        )
    )

    assert resultado is None

    conexao.execute.assert_called_once()

def test_inserir_historico_preco():
    """Testa a criação de um registro no histórico de preços."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 37

    conexao.execute.return_value = resultado_execute

    atualizado_em = datetime(
        2026,
        9,
        1,
        12,
        30,
    )

    resultado = inserir_historico_preco(
        conexao,
        item_catalogo_id=15,
        plataforma_mercado_id=2,
        moeda="BRL",
        menor_preco=Decimal("145.50"),
        maior_preco=Decimal("230.00"),
        preco_medio=Decimal("167.30"),
        preco_mediano=Decimal("160.00"),
        maior_ordem_compra=None,
        quantidade_anuncios=42,
        volume_vendas=None,
        atualizado_na_origem_em=atualizado_em,
    )

    assert resultado == 37

    conexao.execute.assert_called_once()

def test_inserir_historico_preco_sem_id():
    """Testa erro quando o banco não retorna o ID criado."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = None

    conexao.execute.return_value = resultado_execute

    with pytest.raises(
        RuntimeError,
        match=(
            "O banco não retornou o ID "
            "do histórico de preço."
        ),
    ):
        inserir_historico_preco(
            conexao,
            item_catalogo_id=15,
            plataforma_mercado_id=2,
            moeda="BRL",
            menor_preco=Decimal("145.50"),
            maior_preco=None,
            preco_medio=None,
            preco_mediano=None,
            maior_ordem_compra=None,
            quantidade_anuncios=None,
            volume_vendas=None,
            atualizado_na_origem_em=None,
        )
        
def test_inserir_historico_preco_envia_parametros_corretos():
    """Testa os parâmetros enviados ao banco."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 37

    conexao.execute.return_value = resultado_execute

    atualizado_em = datetime(
        2026,
        9,
        1,
        12,
        30,
    )

    inserir_historico_preco(
        conexao,
        item_catalogo_id=15,
        plataforma_mercado_id=2,
        moeda="BRL",
        menor_preco=Decimal("145.50"),
        maior_preco=Decimal("230.00"),
        preco_medio=Decimal("167.30"),
        preco_mediano=Decimal("160.00"),
        maior_ordem_compra=None,
        quantidade_anuncios=42,
        volume_vendas=None,
        atualizado_na_origem_em=atualizado_em,
    )

    argumentos = conexao.execute.call_args

    parametros = argumentos.args[1]

    assert parametros == {
        "item_catalogo_id": 15,
        "plataforma_mercado_id": 2,
        "moeda": "BRL",
        "menor_preco": Decimal("145.50"),
        "maior_preco": Decimal("230.00"),
        "preco_medio": Decimal("167.30"),
        "preco_mediano": Decimal("160.00"),
        "maior_ordem_compra": None,
        "quantidade_anuncios": 42,
        "volume_vendas": None,
        "atualizado_na_origem_em": atualizado_em,
    }
    
def test_obter_itens_catalogo_ids_por_nomes_mercado():
    """Testa busca em lote dos itens do catálogo."""

    conexao = Mock()

    registro_1 = Mock()
    registro_1.id = 15
    registro_1.nome_mercado = (
        "AK-47 | Redline (Field-Tested)"
    )

    registro_2 = Mock()
    registro_2.id = 20
    registro_2.nome_mercado = (
        "AWP | Asiimov (Field-Tested)"
    )

    conexao.execute.return_value = [
        registro_1,
        registro_2,
    ]

    resultado = (
        obter_itens_catalogo_ids_por_nomes_mercado(
            conexao,
            {
                "AK-47 | Redline (Field-Tested)",
                "AWP | Asiimov (Field-Tested)",
            },
        )
    )

    assert resultado == {
        "AK-47 | Redline (Field-Tested)": 15,
        "AWP | Asiimov (Field-Tested)": 20,
    }

    conexao.execute.assert_called_once()
    
def test_obter_itens_catalogo_ids_com_conjunto_vazio():
    """Não consulta o banco quando não existem nomes."""

    conexao = Mock()

    resultado = (
        obter_itens_catalogo_ids_por_nomes_mercado(
            conexao,
            set(),
        )
    )

    assert resultado == {}

    conexao.execute.assert_not_called()