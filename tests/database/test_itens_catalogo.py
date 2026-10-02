import pytest

from unittest.mock import Mock

from skinexa.database.queries.itens_catalogo import (
    contar_itens_catalogo,
    listar_itens_catalogo,
    obter_item_catalogo_por_id,
    obter_item_catalogo_por_nome_mercado,
    obter_itens_catalogo_ids_por_nomes_mercado,
    pesquisar_itens_catalogo_por_nome,
)

def criar_registro_item_catalogo(
    *,
    item_id: int = 1,
    nome_mercado: str = "AK-47 | Redline (Field-Tested)",
    nome_exibicao: str = "AK-47 | Redline",
) -> Mock:
    """Cria um registro simulado de item do catálogo."""

    registro = Mock()

    registro._mapping = {
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
        "float_minimo": None,
        "float_maximo": None,
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
        "criado_em": None,
        "atualizado_em": None,
    }

    return registro

def test_obter_item_catalogo_por_id():
    """Testa a obtenção de um item pelo ID."""

    conexao = Mock()

    registro = criar_registro_item_catalogo()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = (
        registro._mapping
    )

    conexao.execute.return_value = resultado_execute

    resultado = obter_item_catalogo_por_id(
        conexao,
        1,
    )

    assert resultado == registro._mapping

    conexao.execute.assert_called_once()

def test_obter_item_catalogo_por_id_inexistente():
    """Testa a busca por um ID inexistente."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = None

    conexao.execute.return_value = resultado_execute

    resultado = obter_item_catalogo_por_id(
        conexao,
        999,
    )

    assert resultado is None

    conexao.execute.assert_called_once()

def test_obter_item_catalogo_por_id_invalido():
    """Não consulta o banco quando o ID é inválido."""

    conexao = Mock()

    resultado = obter_item_catalogo_por_id(
        conexao,
        0,
    )

    assert resultado is None

    conexao.execute.assert_not_called()

def test_obter_item_catalogo_por_nome_mercado():
    """Testa a obtenção pelo nome de mercado."""

    conexao = Mock()

    registro = criar_registro_item_catalogo()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = (
        registro._mapping
    )

    conexao.execute.return_value = resultado_execute

    resultado = obter_item_catalogo_por_nome_mercado(
        conexao,
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
    )

    assert resultado == registro._mapping

    conexao.execute.assert_called_once()

def test_obter_item_catalogo_por_nome_mercado_inexistente():
    """Testa a busca por um nome de mercado inexistente."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = None

    conexao.execute.return_value = resultado_execute

    resultado = obter_item_catalogo_por_nome_mercado(
        conexao,
        app_id=730,
        nome_mercado="Item inexistente",
    )

    assert resultado is None

    conexao.execute.assert_called_once()

def test_obter_item_catalogo_por_nome_mercado_remove_espacos():
    """Testa a normalização do nome antes da consulta."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = None

    conexao.execute.return_value = resultado_execute

    obter_item_catalogo_por_nome_mercado(
        conexao,
        app_id=730,
        nome_mercado="  AK-47 | Redline (Field-Tested)  ",
    )

    argumentos = conexao.execute.call_args
    parametros = argumentos.args[1]

    assert parametros == {
        "app_id": 730,
        "nome_mercado": "AK-47 | Redline (Field-Tested)",
    }


def test_obter_item_catalogo_por_nome_mercado_invalido():
    """Não consulta o banco quando o nome é vazio."""

    conexao = Mock()

    resultado = obter_item_catalogo_por_nome_mercado(
        conexao,
        app_id=730,
        nome_mercado="   ",
    )

    assert resultado is None

    conexao.execute.assert_not_called()


def test_obter_item_catalogo_por_app_id_invalido():
    """Não consulta o banco quando o app_id é inválido."""

    conexao = Mock()

    resultado = obter_item_catalogo_por_nome_mercado(
        conexao,
        app_id=0,
        nome_mercado="AK-47 | Redline (Field-Tested)",
    )

    assert resultado is None

    conexao.execute.assert_not_called()


def test_obter_itens_catalogo_ids_por_nomes_mercado():
    """Testa busca em lote dos IDs dos itens."""

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

    resultado = obter_itens_catalogo_ids_por_nomes_mercado(
        conexao,
        {
            "AK-47 | Redline (Field-Tested)",
            "AWP | Asiimov (Field-Tested)",
        },
    )

    assert resultado == {
        "AK-47 | Redline (Field-Tested)": 15,
        "AWP | Asiimov (Field-Tested)": 20,
    }

    conexao.execute.assert_called_once()


def test_obter_itens_catalogo_ids_envia_app_id():
    """Testa o app_id enviado na busca em lote."""

    conexao = Mock()
    conexao.execute.return_value = []

    obter_itens_catalogo_ids_por_nomes_mercado(
        conexao,
        {
            "AK-47 | Redline (Field-Tested)",
        },
        app_id=730,
    )

    argumentos = conexao.execute.call_args
    parametros = argumentos.args[1]

    assert parametros["app_id"] == 730
    assert parametros["nomes_mercado"] == (
        "AK-47 | Redline (Field-Tested)",
    )


def test_obter_itens_catalogo_ids_com_conjunto_vazio():
    """Não consulta o banco quando não existem nomes."""

    conexao = Mock()

    resultado = obter_itens_catalogo_ids_por_nomes_mercado(
        conexao,
        set(),
    )

    assert resultado == {}

    conexao.execute.assert_not_called()

def test_listar_itens_catalogo():
    """Testa a listagem paginada do catálogo."""

    conexao = Mock()

    registro_1 = criar_registro_item_catalogo(
        item_id=1,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        nome_exibicao="AK-47 | Redline",
    )

    registro_2 = criar_registro_item_catalogo(
        item_id=2,
        nome_mercado="AWP | Asiimov (Field-Tested)",
        nome_exibicao="AWP | Asiimov",
    )

    conexao.execute.return_value = [
        registro_1,
        registro_2,
    ]

    resultado = listar_itens_catalogo(
        conexao,
        limite=20,
        deslocamento=0,
    )

    assert resultado == [
        registro_1._mapping,
        registro_2._mapping,
    ]

    conexao.execute.assert_called_once()

def test_listar_itens_catalogo_sem_resultados():
    """Testa a listagem de um catálogo sem resultados."""

    conexao = Mock()

    conexao.execute.return_value = []

    resultado = listar_itens_catalogo(
        conexao,
        limite=20,
        deslocamento=0,
    )

    assert resultado == []

    conexao.execute.assert_called_once()

def test_listar_itens_catalogo_envia_paginacao_correta():
    """Testa os parâmetros de paginação enviados ao banco."""

    conexao = Mock()

    conexao.execute.return_value = []

    listar_itens_catalogo(
        conexao,
        limite=25,
        deslocamento=50,
    )

    argumentos = conexao.execute.call_args

    parametros = argumentos.args[1]

    assert parametros == {
        "limite": 25,
        "deslocamento": 50,
    }

def test_listar_itens_catalogo_com_limite_invalido():
    """Testa erro para limite menor que um."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="O limite deve ser maior que zero.",
    ):
        listar_itens_catalogo(
            conexao,
            limite=0,
            deslocamento=0,
        )

    conexao.execute.assert_not_called()


def test_listar_itens_catalogo_com_deslocamento_invalido():
    """Testa erro para deslocamento negativo."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="O deslocamento não pode ser negativo.",
    ):
        listar_itens_catalogo(
            conexao,
            limite=20,
            deslocamento=-1,
        )

    conexao.execute.assert_not_called()

def test_contar_itens_catalogo():
    """Testa a contagem total de itens do catálogo."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = 150

    conexao.execute.return_value = resultado_execute

    resultado = contar_itens_catalogo(
        conexao,
    )

    assert resultado == 150

    conexao.execute.assert_called_once()

def test_pesquisar_itens_catalogo_por_nome():
    """Testa pesquisa textual no catálogo."""

    conexao = Mock()

    registro_1 = criar_registro_item_catalogo(
        item_id=1,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        nome_exibicao="AK-47 | Redline",
    )

    registro_2 = criar_registro_item_catalogo(
        item_id=2,
        nome_mercado="AK-47 | Redline (Minimal Wear)",
        nome_exibicao="AK-47 | Redline",
    )

    conexao.execute.return_value = [
        registro_1,
        registro_2,
    ]

    resultado = pesquisar_itens_catalogo_por_nome(
        conexao,
        termo="Redline",
        limite=20,
        deslocamento=0,
    )

    assert resultado == [
        registro_1._mapping,
        registro_2._mapping,
    ]

    conexao.execute.assert_called_once()

def test_pesquisar_itens_catalogo_por_nome_envia_parametros_corretos():
    """Testa os parâmetros enviados na pesquisa."""

    conexao = Mock()

    conexao.execute.return_value = []

    pesquisar_itens_catalogo_por_nome(
        conexao,
        termo="Redline",
        limite=25,
        deslocamento=50,
    )

    argumentos = conexao.execute.call_args

    parametros = argumentos.args[1]

    assert parametros == {
        "termo": "%Redline%",
        "limite": 25,
        "deslocamento": 50,
    }
    
def test_pesquisar_itens_catalogo_por_nome_remove_espacos():
    """Testa remoção de espaços do termo de pesquisa."""

    conexao = Mock()

    conexao.execute.return_value = []

    pesquisar_itens_catalogo_por_nome(
        conexao,
        termo="  Redline  ",
        limite=20,
        deslocamento=0,
    )

    argumentos = conexao.execute.call_args

    parametros = argumentos.args[1]

    assert parametros["termo"] == "%Redline%"
    
def test_pesquisar_itens_catalogo_por_nome_com_termo_vazio():
    """Não consulta o banco quando o termo está vazio."""

    conexao = Mock()

    resultado = pesquisar_itens_catalogo_por_nome(
        conexao,
        termo="   ",
        limite=20,
        deslocamento=0,
    )

    assert resultado == []

    conexao.execute.assert_not_called()

def test_pesquisar_itens_catalogo_por_nome_sem_resultados():
    """Testa pesquisa sem itens encontrados."""

    conexao = Mock()

    conexao.execute.return_value = []

    resultado = pesquisar_itens_catalogo_por_nome(
        conexao,
        termo="Item inexistente",
        limite=20,
        deslocamento=0,
    )

    assert resultado == []

    conexao.execute.assert_called_once()
    
def test_pesquisar_itens_catalogo_por_nome_com_limite_invalido():
    """Testa pesquisa com limite inválido."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="O limite deve ser maior que zero.",
    ):
        pesquisar_itens_catalogo_por_nome(
            conexao,
            termo="Redline",
            limite=0,
            deslocamento=0,
        )

    conexao.execute.assert_not_called()

def test_pesquisar_itens_catalogo_por_nome_com_deslocamento_invalido():
    """Testa pesquisa com deslocamento inválido."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match=(
            "O deslocamento não pode ser negativo."
        ),
    ):
        pesquisar_itens_catalogo_por_nome(
            conexao,
            termo="Redline",
            limite=20,
            deslocamento=-1,
        )

    conexao.execute.assert_not_called()