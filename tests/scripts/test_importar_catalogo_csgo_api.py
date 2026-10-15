import pytest

from unittest.mock import MagicMock, Mock, patch

from scripts.importar_catalogo_csgo_api import (
    executar_validacao_catalogo,
    executar_importacao_catalogo,
    main,
)

from skinexa.integrations.catalogo.csgo_api_client import (
    ErroCSGOAPI,
)

from skinexa.dto.catalogo.importacao import (
    ItemImportacaoCatalogoDTO,
)

from skinexa.dto.catalogo.variante import (
    VarianteImportacaoCatalogoDTO,
)

from skinexa.dto.catalogo.normalizacao_lote import (
    RelatorioNormalizacaoCatalogoDTO,
)

def test_executar_validacao_catalogo_com_limite(capsys):
    """Testa a validação de um lote com quantidade limitada."""

    registros = [
        {"id": "skin-1"},
        {"id": "skin-2"},
        {"id": "skin-3"},
    ]

    item = Mock()
    item.app_id = 730
    item.nome_mercado = "AK-47 | Redline (Field-Tested)"
    item.tipo_item = "rifle"

    variante = Mock()
    variante.app_id = 730
    variante.nome_mercado = "AK-47 | Redline (Field-Tested)"

    relatorio = Mock()
    relatorio.total_recebidos = 2
    relatorio.total_normalizados = 1
    relatorio.total_variantes_normalizadas = 1
    relatorio.total_rejeitados = 0
    relatorio.total_duplicados = 1
    relatorio.total_variantes_duplicadas = 0
    relatorio.itens = (item,)
    relatorio.variantes = (variante,)
    relatorio.motivos_rejeicao = {}

    with (
        patch(
            "scripts.importar_catalogo_csgo_api."
            "buscar_itens_csgo_api"
        ) as mock_buscar,
        patch(
            "scripts.importar_catalogo_csgo_api."
            "normalizar_lote_skins_csgo_api"
        ) as mock_normalizar,
    ):
        mock_buscar.return_value = registros
        mock_normalizar.return_value = relatorio

        executar_validacao_catalogo(
            limite=2,
        )

    saida = capsys.readouterr().out

    assert "Registros selecionados: 2" in saida
    assert "Normalizacao concluida com sucesso." in saida
    assert "Nenhum registro foi gravado no MySQL." in saida

    mock_buscar.assert_called_once_with(
        "skins"
    )

    mock_normalizar.assert_called_once_with(
        registros[:2]
    )

def test_executar_validacao_catalogo_sem_limite(capsys):
    """Testa o processamento de todos os registros disponíveis."""

    registros = [
        {"id": "skin-1"},
        {"id": "skin-2"},
    ]

    relatorio = Mock()
    relatorio.total_recebidos = 2
    relatorio.total_normalizados = 0
    relatorio.total_variantes_normalizadas = 0
    relatorio.total_rejeitados = 0
    relatorio.total_duplicados = 0
    relatorio.total_variantes_duplicadas = 0
    relatorio.itens = ()
    relatorio.variantes = ()
    relatorio.motivos_rejeicao = {}

    with (
        patch(
            "scripts.importar_catalogo_csgo_api."
            "buscar_itens_csgo_api"
        ) as mock_buscar,
        patch(
            "scripts.importar_catalogo_csgo_api."
            "normalizar_lote_skins_csgo_api"
        ) as mock_normalizar,
    ):
        mock_buscar.return_value = registros
        mock_normalizar.return_value = relatorio

        executar_validacao_catalogo()

    saida = capsys.readouterr().out

    assert "Registros selecionados: 2" in saida

    mock_buscar.assert_called_once_with(
        "skins"
    )

    mock_normalizar.assert_called_once_with(
        registros
    )

def test_executar_validacao_catalogo_com_limite_invalido():
    """Testa a rejeição de um limite menor que um."""

    with patch(
        "scripts.importar_catalogo_csgo_api."
        "buscar_itens_csgo_api"
    ) as mock_buscar:
        with pytest.raises(
            ValueError,
            match="O limite deve ser maior que zero.",
        ):
            executar_validacao_catalogo(
                limite=0,
            )

    mock_buscar.assert_not_called()

def test_executar_validacao_catalogo_com_rejeicoes():
    """Testa a falha quando a normalização rejeita registros."""

    registros = [
        {"id": "skin-invalida"},
    ]

    relatorio = Mock()
    relatorio.total_recebidos = 1
    relatorio.total_normalizados = 0
    relatorio.total_variantes_normalizadas = 0
    relatorio.total_rejeitados = 1
    relatorio.total_duplicados = 0
    relatorio.total_variantes_duplicadas = 0
    relatorio.itens = ()
    relatorio.variantes = ()
    relatorio.motivos_rejeicao = {
        "Registro inválido": 1,
    }

    with (
        patch(
            "scripts.importar_catalogo_csgo_api."
            "buscar_itens_csgo_api"
        ) as mock_buscar,
        patch(
            "scripts.importar_catalogo_csgo_api."
            "normalizar_lote_skins_csgo_api"
        ) as mock_normalizar,
    ):
        mock_buscar.return_value = registros
        mock_normalizar.return_value = relatorio

        with pytest.raises(
            RuntimeError,
            match="A validação identificou inconsistências",
        ):
            executar_validacao_catalogo()

    mock_buscar.assert_called_once()
    mock_normalizar.assert_called_once()

def test_executar_validacao_catalogo_com_variante_sem_item():
    """Testa a rejeição de variantes sem item comercial correspondente."""

    registros = [
        {"id": "skin-1"},
    ]

    variante = Mock()
    variante.app_id = 730
    variante.nome_mercado = "Item comercial inexistente"

    relatorio = Mock()
    relatorio.total_recebidos = 1
    relatorio.total_normalizados = 0
    relatorio.total_variantes_normalizadas = 1
    relatorio.total_rejeitados = 0
    relatorio.total_duplicados = 0
    relatorio.total_variantes_duplicadas = 0
    relatorio.itens = ()
    relatorio.variantes = (variante,)
    relatorio.motivos_rejeicao = {}

    with (
        patch(
            "scripts.importar_catalogo_csgo_api."
            "buscar_itens_csgo_api"
        ) as mock_buscar,
        patch(
            "scripts.importar_catalogo_csgo_api."
            "normalizar_lote_skins_csgo_api"
        ) as mock_normalizar,
    ):
        mock_buscar.return_value = registros
        mock_normalizar.return_value = relatorio

        with pytest.raises(
            RuntimeError,
            match="A validação identificou inconsistências",
        ):
            executar_validacao_catalogo()

    mock_buscar.assert_called_once()
    mock_normalizar.assert_called_once()

def test_main_trata_erro_csgo_api(capsys):
    """Testa o tratamento de falhas HTTP pelo ponto de entrada."""

    with (
        patch(
            "sys.argv",
            ["importar_catalogo_csgo_api.py"],
        ),
        patch(
            "scripts.importar_catalogo_csgo_api."
            "executar_validacao_catalogo"
        ) as mock_executar,
    ):
        mock_executar.side_effect = ErroCSGOAPI(
            "Não foi possível consultar a CSGO-API."
        )

        resultado = main()

    saida = capsys.readouterr()

    assert resultado == 1
    assert "ERRO:" in saida.err
    assert "Não foi possível consultar" in saida.err

    mock_executar.assert_called_once_with(
        limite=None,
    )
    
def test_main_sem_executar_nao_persiste():
    """Testa que o modo padrão não executa a importação no MySQL."""

    relatorio = Mock()

    with (
        patch(
            "sys.argv",
            ["importar_catalogo_csgo_api.py", "--limite", "10"],
        ),
        patch(
            "scripts.importar_catalogo_csgo_api."
            "executar_validacao_catalogo"
        ) as mock_validar,
        patch(
            "scripts.importar_catalogo_csgo_api."
            "executar_importacao_catalogo"
        ) as mock_importar,
    ):
        mock_validar.return_value = relatorio

        resultado = main()

    assert resultado == 0

    mock_validar.assert_called_once_with(
        limite=10,
    )

    mock_importar.assert_not_called()

def test_main_rejeita_execucao_sem_confirmacao():
    """Testa o bloqueio de gravação sem confirmação explícita."""

    with (
        patch(
            "sys.argv",
            [
                "importar_catalogo_csgo_api.py",
                "--executar",
            ],
        ),
        patch(
            "scripts.importar_catalogo_csgo_api."
            "executar_validacao_catalogo"
        ) as mock_validar,
    ):
        with pytest.raises(
            SystemExit,
        ) as erro:
            main()

    assert erro.value.code == 2

    mock_validar.assert_not_called()

def test_main_rejeita_confirmacao_sem_executar():
    """Testa a rejeição da confirmação sem habilitar a importação."""

    with (
        patch(
            "sys.argv",
            [
                "importar_catalogo_csgo_api.py",
                "--confirmar-importacao",
            ],
        ),
        patch(
            "scripts.importar_catalogo_csgo_api."
            "executar_validacao_catalogo"
        ) as mock_validar,
    ):
        with pytest.raises(
            SystemExit,
        ) as erro:
            main()

    assert erro.value.code == 2

    mock_validar.assert_not_called()

def test_main_executa_importacao_confirmada():
    """Testa o encaminhamento do relatório para a importação."""

    relatorio = Mock()

    with (
        patch(
            "sys.argv",
            [
                "importar_catalogo_csgo_api.py",
                "--limite",
                "10",
                "--executar",
                "--confirmar-importacao",
            ],
        ),
        patch(
            "scripts.importar_catalogo_csgo_api."
            "executar_validacao_catalogo"
        ) as mock_validar,
        patch(
            "scripts.importar_catalogo_csgo_api."
            "executar_importacao_catalogo"
        ) as mock_importar,
    ):
        mock_validar.return_value = relatorio

        resultado = main()

    assert resultado == 0

    mock_validar.assert_called_once_with(
        limite=10,
    )

    mock_importar.assert_called_once_with(
        relatorio,
    )

def test_importacao_rejeita_lote_com_erros():
    """Testa a rejeição de lotes que possuem registros inválidos."""

    relatorio = Mock()

    relatorio.total_rejeitados = 1
    relatorio.total_normalizados = 9
    relatorio.total_variantes_normalizadas = 9

    with patch(
        "skinexa.database.connection.engine.begin"
    ) as mock_begin:
        with pytest.raises(
            ValueError,
            match="lote com rejeições",
        ):
            executar_importacao_catalogo(
                relatorio,
            )

    mock_begin.assert_not_called()

def test_importacao_rejeita_lote_vazio():
    """Testa a rejeição de lotes sem itens comerciais."""

    relatorio = Mock()

    relatorio.total_rejeitados = 0
    relatorio.total_normalizados = 0
    relatorio.total_variantes_normalizadas = 0

    with patch(
        "skinexa.database.connection.engine.begin"
    ) as mock_begin:
        with pytest.raises(
            ValueError,
            match="lote vazio",
        ):
            executar_importacao_catalogo(
                relatorio,
            )

    mock_begin.assert_not_called()

def test_importacao_rejeita_variante_sem_item():
    """Testa a rejeição de uma variante sem item comercial no lote."""

    relatorio = Mock()

    relatorio.total_rejeitados = 0
    relatorio.total_normalizados = 1
    relatorio.total_variantes_normalizadas = 1

    item = Mock()
    item.app_id = 730
    item.nome_mercado = "AK-47 | Redline (Field-Tested)"

    variante = Mock()
    variante.app_id = 730
    variante.nome_mercado = "Item inexistente"

    relatorio.itens = (item,)
    relatorio.variantes = (variante,)

    with patch(
        "skinexa.database.connection.engine.begin"
    ) as mock_begin:
        with pytest.raises(
            ValueError,
            match="Variante sem item comercial",
        ):
            executar_importacao_catalogo(
                relatorio,
            )

    mock_begin.assert_not_called()

def test_importacao_utiliza_transacao():
    """Testa a persistência dos registros dentro de uma transação."""

    item = ItemImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        nome_exibicao="AK-47 | Redline",
        tipo_item="rifle",
    )

    variante = VarianteImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        fonte="csgo_api",
        id_externo="skin-abc_0",
    )

    relatorio = RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=1,
        total_normalizados=1,
        total_rejeitados=0,
        total_duplicados=0,
        itens=(item,),
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=1,
        total_variantes_duplicadas=0,
        variantes=(variante,),
    )

    conexao = MagicMock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = (
        "b5ygvcodkj02gnmloode"
    )

    conexao.execute.return_value = resultado_execute

    with (
        patch(
            "skinexa.database.connection.engine.begin"
        ) as mock_begin,
        patch(
            "skinexa.services.catalogo.importacao."
            "importar_lote_catalogo"
        ) as mock_importar,
    ):
        mock_begin.return_value.__enter__.return_value = (
            conexao
        )

        mock_importar.return_value = (1, 1)

        resultado = executar_importacao_catalogo(
            relatorio,
            tamanho_lote=100,
        )

    assert resultado == (1, 1)

    mock_begin.assert_called_once()

    conexao.execute.assert_called_once()

    mock_importar.assert_called_once()

    argumentos = mock_importar.call_args

    assert argumentos.args[0] == conexao

    relatorio_lote = argumentos.args[1]

    assert relatorio_lote.total_normalizados == 1
    assert relatorio_lote.total_variantes_normalizadas == 1

    assert relatorio_lote.itens == (item,)
    assert relatorio_lote.variantes == (variante,)

    mock_begin.return_value.__exit__.assert_called_once()
    
def test_importacao_catalogo_processa_multiplos_lotes():
    """Testa a divisão dos itens comerciais em transações menores."""

    itens = (
        ItemImportacaoCatalogoDTO(
            app_id=730,
            nome_mercado=f"Item comercial {indice}",
            nome_exibicao=f"Item comercial {indice}",
            tipo_item="rifle",
        )
        for indice in range(1, 6)
    )

    itens = tuple(itens)

    variantes = tuple(
        VarianteImportacaoCatalogoDTO(
            app_id=730,
            nome_mercado=item.nome_mercado,
            fonte="csgo_api",
            id_externo=f"skin-{indice}",
        )
        for indice, item in enumerate(
            itens,
            start=1,
        )
    )

    relatorio = RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=5,
        total_normalizados=5,
        total_rejeitados=0,
        total_duplicados=0,
        itens=itens,
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=5,
        total_variantes_duplicadas=0,
        variantes=variantes,
    )

    conexao = MagicMock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = (
        "b5ygvcodkj02gnmloode"
    )

    conexao.execute.return_value = resultado_execute

    with (
        patch(
            "skinexa.database.connection.engine.begin"
        ) as mock_begin,
        patch(
            "skinexa.services.catalogo.importacao."
            "importar_lote_catalogo"
        ) as mock_importar,
    ):
        mock_begin.return_value.__enter__.return_value = (
            conexao
        )

        mock_importar.side_effect = [
            (2, 2),
            (2, 2),
            (1, 1),
        ]

        resultado = executar_importacao_catalogo(
            relatorio,
            tamanho_lote=2,
        )

    assert resultado == (5, 5)

    assert mock_begin.call_count == 3
    assert mock_importar.call_count == 3

    relatorio_lote_1 = (
        mock_importar.call_args_list[0].args[1]
    )

    relatorio_lote_2 = (
        mock_importar.call_args_list[1].args[1]
    )

    relatorio_lote_3 = (
        mock_importar.call_args_list[2].args[1]
    )

    assert relatorio_lote_1.itens == itens[:2]
    assert relatorio_lote_2.itens == itens[2:4]
    assert relatorio_lote_3.itens == itens[4:]

    assert relatorio_lote_1.variantes == variantes[:2]
    assert relatorio_lote_2.variantes == variantes[2:4]
    assert relatorio_lote_3.variantes == variantes[4:]

def test_importacao_agrupa_variantes_do_mesmo_item():
    """Testa que variantes do mesmo item permanecem no mesmo lote."""

    item = ItemImportacaoCatalogoDTO(
        app_id=730,
        nome_mercado="AK-47 | Redline (Field-Tested)",
        nome_exibicao="AK-47 | Redline",
        tipo_item="rifle",
    )

    variantes = (
        VarianteImportacaoCatalogoDTO(
            app_id=730,
            nome_mercado=item.nome_mercado,
            fonte="csgo_api",
            id_externo="skin-abc_0",
        ),
        VarianteImportacaoCatalogoDTO(
            app_id=730,
            nome_mercado=item.nome_mercado,
            fonte="csgo_api",
            id_externo="skin-abc_1",
        ),
    )

    relatorio = RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=2,
        total_normalizados=1,
        total_rejeitados=0,
        total_duplicados=1,
        itens=(item,),
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=2,
        total_variantes_duplicadas=0,
        variantes=variantes,
    )

    conexao = MagicMock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = (
        "b5ygvcodkj02gnmloode"
    )

    conexao.execute.return_value = resultado_execute

    with (
        patch(
            "skinexa.database.connection.engine.begin"
        ) as mock_begin,
        patch(
            "skinexa.services.catalogo.importacao."
            "importar_lote_catalogo"
        ) as mock_importar,
    ):
        mock_begin.return_value.__enter__.return_value = conexao
        mock_importar.return_value = (1, 2)

        resultado = executar_importacao_catalogo(
            relatorio,
            tamanho_lote=100,
        )

    assert resultado == (1, 2)

    mock_begin.assert_called_once()
    mock_importar.assert_called_once()

    relatorio_lote = mock_importar.call_args.args[1]

    assert relatorio_lote.itens == (item,)
    assert relatorio_lote.variantes == variantes
    assert relatorio_lote.total_variantes_normalizadas == 2

def test_importacao_interrompe_apos_falha_no_segundo_lote():
    """Testa a interrupção da importação após uma falha intermediária."""

    itens = tuple(
        ItemImportacaoCatalogoDTO(
            app_id=730,
            nome_mercado=f"Item comercial {indice}",
            nome_exibicao=f"Item comercial {indice}",
            tipo_item="rifle",
        )
        for indice in range(1, 4)
    )

    variantes = tuple(
        VarianteImportacaoCatalogoDTO(
            app_id=730,
            nome_mercado=item.nome_mercado,
            fonte="csgo_api",
            id_externo=f"skin-{indice}",
        )
        for indice, item in enumerate(
            itens,
            start=1,
        )
    )

    relatorio = RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=3,
        total_normalizados=3,
        total_rejeitados=0,
        total_duplicados=0,
        itens=itens,
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=3,
        total_variantes_duplicadas=0,
        variantes=variantes,
    )

    conexao = MagicMock()

    resultado_execute = Mock()
    resultado_execute.scalar_one.return_value = (
        "b5ygvcodkj02gnmloode"
    )

    conexao.execute.return_value = resultado_execute

    with (
        patch(
            "skinexa.database.connection.engine.begin"
        ) as mock_begin,
        patch(
            "skinexa.services.catalogo.importacao."
            "importar_lote_catalogo"
        ) as mock_importar,
    ):
        mock_begin.return_value.__enter__.return_value = conexao

        mock_importar.side_effect = [
            (1, 1),
            RuntimeError("Falha ao importar o segundo lote."),
        ]

        with pytest.raises(
            RuntimeError,
            match="Falha ao importar o segundo lote",
        ):
            executar_importacao_catalogo(
                relatorio,
                tamanho_lote=1,
            )

    assert mock_begin.call_count == 2
    assert mock_importar.call_count == 2

    relatorio_lote_1 = mock_importar.call_args_list[0].args[1]
    relatorio_lote_2 = mock_importar.call_args_list[1].args[1]

    assert relatorio_lote_1.itens == (itens[0],)
    assert relatorio_lote_2.itens == (itens[1],)