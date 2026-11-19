from unittest.mock import Mock

import pytest

from skinexa.database.queries.conteudos_conteineres_catalogo import (
    contar_conteudos_conteineres_catalogo,
    inserir_ou_atualizar_conteudo_conteiner_catalogo,
    listar_conteudos_por_conteiner_catalogo,
)

def criar_registro_conteudo_conteiner(
    *,
    conteudo_id: int = 1,
    conteiner_catalogo_id: int = 10,
    id_externo_conteudo: str = "skin-2ca8cb95f31e",
    nome_conteudo: str = "MP7 | Skulls",
    tipo_conteudo: str = "contains",
) -> Mock:
    """Cria um registro simulado de conteúdo de contêiner."""

    registro = Mock()

    registro._mapping = {
        "id": conteudo_id,
        "conteiner_catalogo_id": conteiner_catalogo_id,
        "fonte": "csgo_api",
        "id_externo_conteudo": id_externo_conteudo,
        "nome_conteudo": nome_conteudo,
        "tipo_conteudo": tipo_conteudo,
        "raridade": "Mil-Spec Grade",
        "indice_pintura": 11,
        "nome_fase": None,
        "url_imagem": None,
        "criado_em": None,
        "atualizado_em": None,
    }

    return registro

def test_importacao_conteudo_retorna_id():
    """Testa o retorno do ID interno do conteúdo persistido."""

    conexao = Mock()

    conexao.execute.return_value.lastrowid = 35

    resultado = inserir_ou_atualizar_conteudo_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-2ca8cb95f31e",
        nome_conteudo="MP7 | Skulls",
        tipo_conteudo="contains",
    )

    assert resultado == 35
    conexao.execute.assert_called_once()

def test_importacao_conteudo_envia_parametros():
    """Testa os parâmetros enviados para persistência."""

    conexao = Mock()

    conexao.execute.return_value.lastrowid = 35

    inserir_ou_atualizar_conteudo_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-2ca8cb95f31e",
        nome_conteudo="MP7 | Skulls",
        tipo_conteudo="contains",
        raridade="Mil-Spec Grade",
        indice_pintura=11,
        nome_fase="Phase 1",
        url_imagem="https://exemplo.com/mp7.png",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros == {
        "conteiner_catalogo_id": 10,
        "fonte": "csgo_api",
        "id_externo_conteudo": "skin-2ca8cb95f31e",
        "nome_conteudo": "MP7 | Skulls",
        "tipo_conteudo": "contains",
        "raridade": "Mil-Spec Grade",
        "indice_pintura": 11,
        "nome_fase": "Phase 1",
        "url_imagem": "https://exemplo.com/mp7.png",
    }

def test_importacao_conteudo_normaliza_textos():
    """Remove espaços dos campos textuais."""

    conexao = Mock()

    conexao.execute.return_value.lastrowid = 35

    inserir_ou_atualizar_conteudo_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
        fonte="  csgo_api  ",
        id_externo_conteudo="  skin-2ca8cb95f31e  ",
        nome_conteudo="  MP7 | Skulls  ",
        tipo_conteudo="  contains  ",
        raridade="  Mil-Spec Grade  ",
        nome_fase="  Phase 1  ",
        url_imagem="  https://exemplo.com/mp7.png  ",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros["fonte"] == "csgo_api"
    assert parametros["id_externo_conteudo"] == "skin-2ca8cb95f31e"
    assert parametros["nome_conteudo"] == "MP7 | Skulls"
    assert parametros["tipo_conteudo"] == "contains"
    assert parametros["raridade"] == "Mil-Spec Grade"
    assert parametros["nome_fase"] == "Phase 1"
    assert parametros["url_imagem"] == "https://exemplo.com/mp7.png"

def test_importacao_conteudo_normaliza_opcionais_vazios():
    """Converte campos opcionais vazios em None."""

    conexao = Mock()

    conexao.execute.return_value.lastrowid = 35

    inserir_ou_atualizar_conteudo_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-2ca8cb95f31e",
        nome_conteudo="MP7 | Skulls",
        tipo_conteudo="contains",
        raridade="   ",
        nome_fase="   ",
        url_imagem="   ",
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros["raridade"] is None
    assert parametros["nome_fase"] is None
    assert parametros["url_imagem"] is None
    assert parametros["indice_pintura"] is None

@pytest.mark.parametrize(
    "conteiner_catalogo_id",
    [0, -1, -100],
)

def test_importacao_conteudo_rejeita_conteiner_id_invalido(
    conteiner_catalogo_id,
):
    """Rejeita identificadores internos inválidos."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="ID do contêiner deve ser maior que zero",
    ):
        inserir_ou_atualizar_conteudo_conteiner_catalogo(
            conexao,
            conteiner_catalogo_id=conteiner_catalogo_id,
            fonte="csgo_api",
            id_externo_conteudo="skin-2ca8cb95f31e",
            nome_conteudo="MP7 | Skulls",
            tipo_conteudo="contains",
        )

    conexao.execute.assert_not_called()

@pytest.mark.parametrize(
    ("fonte", "id_externo_conteudo", "nome_conteudo", "mensagem"),
    [
        (
            "   ",
            "skin-2ca8cb95f31e",
            "MP7 | Skulls",
            "fonte do conteúdo",
        ),
        (
            "csgo_api",
            "   ",
            "MP7 | Skulls",
            "ID externo do conteúdo",
        ),
        (
            "csgo_api",
            "skin-2ca8cb95f31e",
            "   ",
            "nome do conteúdo",
        ),
    ],
)

def test_importacao_conteudo_rejeita_campos_obrigatorios_vazios(
    fonte,
    id_externo_conteudo,
    nome_conteudo,
    mensagem,
):
    """Rejeita informações obrigatórias vazias."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match=mensagem,
    ):
        inserir_ou_atualizar_conteudo_conteiner_catalogo(
            conexao,
            conteiner_catalogo_id=10,
            fonte=fonte,
            id_externo_conteudo=id_externo_conteudo,
            nome_conteudo=nome_conteudo,
            tipo_conteudo="contains",
        )

    conexao.execute.assert_not_called()

@pytest.mark.parametrize(
    "tipo_conteudo",
    ["", "   ", "outro", "rare"],
)

def test_importacao_conteudo_rejeita_tipo_invalido(
    tipo_conteudo,
):
    """Rejeita classificações não previstas no banco."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="tipo do conteúdo deve ser contains",
    ):
        inserir_ou_atualizar_conteudo_conteiner_catalogo(
            conexao,
            conteiner_catalogo_id=10,
            fonte="csgo_api",
            id_externo_conteudo="skin-2ca8cb95f31e",
            nome_conteudo="MP7 | Skulls",
            tipo_conteudo=tipo_conteudo,
        )

    conexao.execute.assert_not_called()

def test_importacao_conteudo_aceita_contains_rare():
    """Aceita conteúdos classificados como contains_rare."""

    conexao = Mock()

    conexao.execute.return_value.lastrowid = 35

    resultado = inserir_ou_atualizar_conteudo_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-vanilla-weapon_bayonet",
        nome_conteudo="Bayonet",
        tipo_conteudo="contains_rare",
    )

    assert resultado == 35

    parametros = conexao.execute.call_args.args[1]
    assert parametros["tipo_conteudo"] == "contains_rare"

def test_importacao_conteudo_rejeita_paint_index_negativo():
    """Rejeita índices de pintura negativos."""

    conexao = Mock()

    with pytest.raises(
        ValueError,
        match="índice de pintura não pode ser negativo",
    ):
        inserir_ou_atualizar_conteudo_conteiner_catalogo(
            conexao,
            conteiner_catalogo_id=10,
            fonte="csgo_api",
            id_externo_conteudo="skin-2ca8cb95f31e",
            nome_conteudo="MP7 | Skulls",
            tipo_conteudo="contains",
            indice_pintura=-1,
        )

    conexao.execute.assert_not_called()

def test_importacao_conteudo_aceita_paint_index_zero():
    """Aceita paint index igual a zero."""

    conexao = Mock()

    conexao.execute.return_value.lastrowid = 35

    inserir_ou_atualizar_conteudo_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-2ca8cb95f31e",
        nome_conteudo="MP7 | Skulls",
        tipo_conteudo="contains",
        indice_pintura=0,
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros["indice_pintura"] == 0

def test_importacao_conteudo_utiliza_upsert_mysql():
    """Verifica a estratégia SQL para evitar duplicidades."""

    conexao = Mock()

    conexao.execute.return_value.lastrowid = 35

    inserir_ou_atualizar_conteudo_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
        fonte="csgo_api",
        id_externo_conteudo="skin-2ca8cb95f31e",
        nome_conteudo="MP7 | Skulls",
        tipo_conteudo="contains",
    )

    consulta = str(conexao.execute.call_args.args[0])

    assert "ON DUPLICATE KEY UPDATE" in consulta
    assert "LAST_INSERT_ID(id)" in consulta
    assert "nome_conteudo = VALUES(nome_conteudo)" in consulta
    assert "indice_pintura = COALESCE(" in consulta

    conexao.execute.assert_called_once()

@pytest.mark.parametrize(
    "id_retornado",
    [None, 0, -1],
)

def test_importacao_conteudo_rejeita_id_nao_retornado(
    id_retornado,
):
    """Rejeita retorno de identificador interno inválido."""

    conexao = Mock()

    conexao.execute.return_value.lastrowid = id_retornado

    with pytest.raises(
        RuntimeError,
        match="ID do conteúdo",
    ):
        inserir_ou_atualizar_conteudo_conteiner_catalogo(
            conexao,
            conteiner_catalogo_id=10,
            fonte="csgo_api",
            id_externo_conteudo="skin-2ca8cb95f31e",
            nome_conteudo="MP7 | Skulls",
            tipo_conteudo="contains",
        )

    conexao.execute.assert_called_once()

def test_listar_conteudos_por_conteiner():
    """Testa a listagem dos conteúdos de um contêiner."""

    conexao = Mock()

    registro_1 = criar_registro_conteudo_conteiner(
        conteudo_id=1,
        nome_conteudo="MP7 | Skulls",
    )

    registro_2 = criar_registro_conteudo_conteiner(
        conteudo_id=2,
        id_externo_conteudo="skin-vanilla-weapon_bayonet",
        nome_conteudo="Bayonet",
        tipo_conteudo="contains_rare",
    )

    conexao.execute.return_value = [
        registro_1,
        registro_2,
    ]

    resultado = listar_conteudos_por_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
    )

    assert resultado == [
        registro_1._mapping,
        registro_2._mapping,
    ]

    conexao.execute.assert_called_once()

def test_listar_conteudos_sem_resultados():
    """Retorna lista vazia quando o contêiner não possui conteúdos."""

    conexao = Mock()
    conexao.execute.return_value = []

    resultado = listar_conteudos_por_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
    )

    assert resultado == []
    conexao.execute.assert_called_once()

def test_listar_conteudos_envia_parametro():
    """Verifica o identificador usado na consulta."""

    conexao = Mock()
    conexao.execute.return_value = []

    listar_conteudos_por_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
    )

    parametros = conexao.execute.call_args.args[1]

    assert parametros == {
        "conteiner_catalogo_id": 10,
    }

def test_listar_conteudos_ordena_resultados():
    """Verifica a ordenação aplicada na consulta."""

    conexao = Mock()
    conexao.execute.return_value = []

    listar_conteudos_por_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=10,
    )

    consulta = str(conexao.execute.call_args.args[0])

    assert "tipo_conteudo ASC" in consulta
    assert "nome_conteudo ASC" in consulta
    assert "id ASC" in consulta

@pytest.mark.parametrize(
    "conteiner_catalogo_id",
    [0, -1],
)

def test_listar_conteudos_rejeita_conteiner_id_invalido(
    conteiner_catalogo_id,
):
    """Evita consultas com identificadores inválidos."""

    conexao = Mock()

    resultado = listar_conteudos_por_conteiner_catalogo(
        conexao,
        conteiner_catalogo_id=conteiner_catalogo_id,
    )

    assert resultado == []
    conexao.execute.assert_not_called()

def test_contar_conteudos_conteineres_catalogo():
    """Testa a contagem total de conteúdos."""

    conexao = Mock()

    conexao.execute.return_value.scalar_one.return_value = 19127

    resultado = contar_conteudos_conteineres_catalogo(
        conexao,
    )

    assert resultado == 19127
    conexao.execute.assert_called_once()

def test_contar_conteudos_conteineres_catalogo_vazio():
    """Testa contagem quando não existem conteúdos."""

    conexao = Mock()

    conexao.execute.return_value.scalar_one.return_value = 0

    resultado = contar_conteudos_conteineres_catalogo(
        conexao,
    )

    assert resultado == 0
    conexao.execute.assert_called_once()