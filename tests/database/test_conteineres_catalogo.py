from unittest.mock import Mock

import pytest

from skinexa.database.queries.conteineres_catalogo import (
    contar_conteineres_catalogo,
    inserir_ou_atualizar_conteiner_catalogo,
    obter_conteiner_catalogo_por_id_externo,
)

def criar_registro_conteiner_catalogo(
    *,
    conteiner_id: int = 1,
    id_externo: str = "crate-4001",
    nome: str = "CS:GO Weapon Case",
) -> dict:
    """Cria um registro simulado de contêiner."""

    return {
        "id": conteiner_id,
        "fonte": "csgo_api",
        "id_externo": id_externo,
        "item_catalogo_id": 100,
        "nome": nome,
        "tipo_conteiner": "Case",
        "url_imagem": None,
        "criado_em": None,
        "atualizado_em": None,
    }

def test_obter_conteiner_por_id_externo():
    """Testa a obtenção de um contêiner por identidade externa."""

    conexao = Mock()
    registro = criar_registro_conteiner_catalogo()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = registro

    conexao.execute.return_value = resultado_execute

    resultado = obter_conteiner_catalogo_por_id_externo(
        conexao,
        fonte="csgo_api",
        id_externo="crate-4001",
    )

    assert resultado == registro
    conexao.execute.assert_called_once()

def test_obter_conteiner_inexistente():
    """Retorna None quando o contêiner não existe."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = None

    conexao.execute.return_value = resultado_execute

    resultado = obter_conteiner_catalogo_por_id_externo(
        conexao,
        fonte="csgo_api",
        id_externo="crate-inexistente",
    )

    assert resultado is None
    conexao.execute.assert_called_once()

def test_obter_conteiner_normaliza_identidade():
    """Remove espaços da fonte e do identificador externo."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.mappings.return_value.first.return_value = None

    conexao.execute.return_value = resultado_execute

    obter_conteiner_catalogo_por_id_externo(
        conexao,
        fonte="  csgo_api  ",
        id_externo="  crate-4001  ",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros == {
        "fonte": "csgo_api",
        "id_externo": "crate-4001",
    }

@pytest.mark.parametrize(
    ("fonte", "id_externo"),
    [
        ("   ", "crate-4001"),
        ("csgo_api", "   "),
        ("   ", "   "),
    ],
)

def test_obter_conteiner_com_identidade_invalida(
    fonte,
    id_externo,
):
    """Não consulta o banco com identidade externa inválida."""

    conexao = Mock()

    resultado = obter_conteiner_catalogo_por_id_externo(
        conexao,
        fonte=fonte,
        id_externo=id_externo,
    )

    assert resultado is None
    conexao.execute.assert_not_called()

def test_importacao_conteiner_retorna_id():
    """Testa o retorno do ID interno após a persistência."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 25

    conexao.execute.return_value = resultado_execute

    resultado = inserir_ou_atualizar_conteiner_catalogo(
        conexao,
        fonte="csgo_api",
        id_externo="crate-4001",
        nome="CS:GO Weapon Case",
    )

    assert resultado == 25
    conexao.execute.assert_called_once()

def test_importacao_conteiner_envia_parametros():
    """Verifica os parâmetros enviados ao banco."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 25

    conexao.execute.return_value = resultado_execute

    inserir_ou_atualizar_conteiner_catalogo(
        conexao,
        fonte="csgo_api",
        id_externo="crate-4001",
        nome="CS:GO Weapon Case",
        item_catalogo_id=100,
        tipo_conteiner="Case",
        url_imagem="https://exemplo.com/caixa.png",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros == {
        "fonte": "csgo_api",
        "id_externo": "crate-4001",
        "item_catalogo_id": 100,
        "nome": "CS:GO Weapon Case",
        "tipo_conteiner": "Case",
        "url_imagem": "https://exemplo.com/caixa.png",
    }

def test_importacao_conteiner_remove_espacos():
    """Normaliza campos textuais antes da persistência."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 25

    conexao.execute.return_value = resultado_execute

    inserir_ou_atualizar_conteiner_catalogo(
        conexao,
        fonte="  csgo_api  ",
        id_externo="  crate-4001  ",
        nome="  CS:GO Weapon Case  ",
        tipo_conteiner="  Case  ",
        url_imagem="  https://exemplo.com/caixa.png  ",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros == {
        "fonte": "csgo_api",
        "id_externo": "crate-4001",
        "item_catalogo_id": None,
        "nome": "CS:GO Weapon Case",
        "tipo_conteiner": "Case",
        "url_imagem": "https://exemplo.com/caixa.png",
    }

def test_importacao_conteiner_normaliza_opcionais_vazios():
    """Converte campos opcionais vazios em None."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 25

    conexao.execute.return_value = resultado_execute

    inserir_ou_atualizar_conteiner_catalogo(
        conexao,
        fonte="csgo_api",
        id_externo="crate-4001",
        nome="CS:GO Weapon Case",
        tipo_conteiner="   ",
        url_imagem="   ",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros["tipo_conteiner"] is None
    assert parametros["url_imagem"] is None
    assert parametros["item_catalogo_id"] is None

@pytest.mark.parametrize(
    ("fonte", "id_externo", "nome", "mensagem"),
    [
        (
            "   ",
            "crate-4001",
            "CS:GO Weapon Case",
            "fonte do contêiner",
        ),
        (
            "csgo_api",
            "   ",
            "CS:GO Weapon Case",
            "ID externo do contêiner",
        ),
        (
            "csgo_api",
            "crate-4001",
            "   ",
            "nome do contêiner",
        ),
    ],
)

def test_importacao_conteiner_rejeita_campos_obrigatorios_vazios(
    fonte,
    id_externo,
    nome,
    mensagem,
):
    """Rejeita campos obrigatórios inválidos."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match=mensagem,
    ):
        inserir_ou_atualizar_conteiner_catalogo(
            conexao,
            fonte=fonte,
            id_externo=id_externo,
            nome=nome,
        )

    conexao.execute.assert_not_called()

@pytest.mark.parametrize(
    "item_catalogo_id",
    [0, -1, -100],
)

def test_importacao_conteiner_rejeita_item_id_invalido(
    item_catalogo_id,
):
    """Rejeita associação com identificador comercial inválido."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="ID do item comercial deve ser maior que zero",
    ):
        inserir_ou_atualizar_conteiner_catalogo(
            conexao,
            fonte="csgo_api",
            id_externo="crate-4001",
            nome="CS:GO Weapon Case",
            item_catalogo_id=item_catalogo_id,
        )

    conexao.execute.assert_not_called()

def test_importacao_conteiner_preserva_opcionais_existentes():
    """Verifica que campos opcionais não são apagados no upsert."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 25

    conexao.execute.return_value = resultado_execute

    inserir_ou_atualizar_conteiner_catalogo(
        conexao,
        fonte="csgo_api",
        id_externo="crate-4001",
        nome="CS:GO Weapon Case",
    )

    consulta = str(conexao.execute.call_args.args[0])

    assert "ON DUPLICATE KEY UPDATE" in consulta
    assert "LAST_INSERT_ID(id)" in consulta

    assert "item_catalogo_id = COALESCE(" in consulta
    assert "tipo_conteiner = COALESCE(" in consulta
    assert "url_imagem = COALESCE(" in consulta

    conexao.execute.assert_called_once()

def test_importacao_conteiner_rejeita_id_nao_retornado():
    """Rejeita ausência de identificador interno após a escrita."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = None

    conexao.execute.return_value = resultado_execute

    with pytest.raises(
        RuntimeError,
        match="ID do contêiner",
    ):
        inserir_ou_atualizar_conteiner_catalogo(
            conexao,
            fonte="csgo_api",
            id_externo="crate-4001",
            nome="CS:GO Weapon Case",
        )

    conexao.execute.assert_called_once()

def test_importacao_conteiner_rejeita_id_zero():
    """Rejeita identificador interno inválido."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.lastrowid = 0

    conexao.execute.return_value = resultado_execute

    with pytest.raises(
        RuntimeError,
        match="ID do contêiner",
    ):
        inserir_ou_atualizar_conteiner_catalogo(
            conexao,
            fonte="csgo_api",
            id_externo="crate-4001",
            nome="CS:GO Weapon Case",
        )

    conexao.execute.assert_called_once()

def test_contar_conteineres_catalogo():
    """Testa a contagem de contêineres cadastrados."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = 481

    conexao.execute.return_value = resultado_execute

    resultado = contar_conteineres_catalogo(
        conexao
    )

    assert resultado == 481
    conexao.execute.assert_called_once()

def test_contar_conteineres_catalogo_vazio():
    """Testa a contagem sem contêineres cadastrados."""

    conexao = Mock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = 0

    conexao.execute.return_value = resultado_execute

    resultado = contar_conteineres_catalogo(
        conexao
    )

    assert resultado == 0
    conexao.execute.assert_called_once()