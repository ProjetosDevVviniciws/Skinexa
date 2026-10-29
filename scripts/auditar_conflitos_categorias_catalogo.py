"""Audita conflitos entre categorias adicionais e o catálogo MySQL."""

from sqlalchemy import text

from skinexa.database.connection import engine

from skinexa.integrations.catalogo.csgo_api_client import (
    buscar_itens_csgo_api,
)

from skinexa.services.catalogo.normalizacao_itens_adicionais import (
    normalizar_lote_itens_adicionais_csgo_api,
)

CATEGORIAS_AUDITORIA = (
    "patches",
    "chaveiros",
    "grafites",
    "musicas",
    "colecionaveis",
    "adesivos_encapsulados",
    "chaves",
    "destaques",
)

def carregar_dados_auditoria() -> tuple[list[dict], list[dict]]:
    """Normaliza as categorias e prepara os registros temporários."""

    itens = []
    variantes = []

    for categoria in CATEGORIAS_AUDITORIA:
        registros = buscar_itens_csgo_api(
            categoria
        )

        relatorio = normalizar_lote_itens_adicionais_csgo_api(
            registros,
            categoria=categoria,
        )

        print(
            f"{categoria.upper()}: "
            f"{relatorio.total_normalizados} itens | "
            f"{relatorio.total_variantes_normalizadas} variantes | "
            f"{relatorio.total_sem_identidade_comercial} pendentes"
        )

        if relatorio.total_rejeitados:
            raise RuntimeError(
                f"A categoria {categoria} apresentou "
                f"{relatorio.total_rejeitados} rejeições."
            )

        chaves_itens = {
            (item.app_id, item.nome_mercado)
            for item in relatorio.itens
        }

        for variante in relatorio.variantes:
            if (
                variante.app_id,
                variante.nome_mercado,
            ) not in chaves_itens:
                raise RuntimeError(
                    "Foi encontrada uma variante sem item comercial: "
                    f"{variante.id_externo}"
                )

        for item in relatorio.itens:
            itens.append(
                {
                    "categoria": categoria,
                    "app_id": item.app_id,
                    "nome_mercado": item.nome_mercado,
                    "tipo_item": item.tipo_item,
                }
            )

        for variante in relatorio.variantes:
            variantes.append(
                {
                    "categoria": categoria,
                    "app_id": variante.app_id,
                    "nome_mercado": variante.nome_mercado,
                    "fonte": variante.fonte,
                    "id_externo": variante.id_externo,
                }
            )

    return itens, variantes

def criar_tabelas_temporarias(conexao) -> None:
    """Cria tabelas de auditoria com a collation do catálogo."""

    conexao.execute(
        text(
            """
            CREATE TEMPORARY TABLE auditoria_adicionais_itens (
                categoria VARCHAR(50) NOT NULL,
                app_id INT UNSIGNED NOT NULL,
                nome_mercado VARCHAR(255) NOT NULL,
                tipo_item VARCHAR(50) NOT NULL,
                INDEX idx_auditoria_item (
                    app_id,
                    nome_mercado
                )
            )
            ENGINE = InnoDB
            DEFAULT CHARSET = utf8mb4
            COLLATE = utf8mb4_unicode_ci
            """
        )
    )

    conexao.execute(
        text(
            """
            CREATE TEMPORARY TABLE auditoria_adicionais_variantes (
                categoria VARCHAR(50) NOT NULL,
                app_id INT UNSIGNED NOT NULL,
                nome_mercado VARCHAR(255) NOT NULL,
                fonte VARCHAR(50) NOT NULL,
                id_externo VARCHAR(100) NOT NULL,
                INDEX idx_auditoria_variante (
                    fonte,
                    id_externo
                )
            )
            ENGINE = InnoDB
            DEFAULT CHARSET = utf8mb4
            COLLATE = utf8mb4_unicode_ci
            """
        )
    )

def inserir_dados_temporarios(
    conexao,
    itens: list[dict],
    variantes: list[dict],
) -> None:
    """Insere os registros exclusivamente nas tabelas temporárias."""

    if itens:
        conexao.execute(
            text(
                """
                INSERT INTO auditoria_adicionais_itens (
                    categoria,
                    app_id,
                    nome_mercado,
                    tipo_item
                )
                VALUES (
                    :categoria,
                    :app_id,
                    :nome_mercado,
                    :tipo_item
                )
                """
            ),
            itens,
        )

    if variantes:
        conexao.execute(
            text(
                """
                INSERT INTO auditoria_adicionais_variantes (
                    categoria,
                    app_id,
                    nome_mercado,
                    fonte,
                    id_externo
                )
                VALUES (
                    :categoria,
                    :app_id,
                    :nome_mercado,
                    :fonte,
                    :id_externo
                )
                """
            ),
            variantes,
        )

def executar_consulta(conexao, consulta: str) -> list[dict]:
    """Executa uma consulta de auditoria e retorna seus resultados."""

    return [
        dict(linha)
        for linha in conexao.execute(
            text(consulta)
        ).mappings().all()
    ]

def exibir_resultados(
    titulo: str,
    registros: list[dict],
) -> None:
    """Apresenta a quantidade e exemplos encontrados na auditoria."""

    print(f"\n{titulo}")
    print("-" * 50)
    print(f"Total: {len(registros)}")

    for registro in registros[:10]:
        print(registro)

def auditar_conflitos_categorias_catalogo() -> int:
    """Verifica colisões comerciais e conflitos de identidades externas."""

    print("\nSKINEXA - AUDITORIA DE CONFLITOS DO CATALOGO")
    print("=" * 50)

    itens, variantes = carregar_dados_auditoria()

    print("\nREGISTROS PREPARADOS")
    print("-" * 50)
    print(f"Itens comerciais: {len(itens)}")
    print(f"Variantes externas: {len(variantes)}")

    with engine.connect() as conexao:
        try:
            criar_tabelas_temporarias(
                conexao
            )

            inserir_dados_temporarios(
                conexao,
                itens,
                variantes,
            )

            # 1. Nomes equivalentes pela collation do MySQL.
            colisoes_comerciais = executar_consulta(
                conexao,
                """
                SELECT
                    app_id,
                    MIN(nome_mercado) AS nome_referencia,
                    COUNT(*) AS quantidade,
                    COUNT(DISTINCT categoria) AS categorias_distintas,
                    COUNT(DISTINCT tipo_item) AS tipos_distintos
                FROM auditoria_adicionais_itens
                GROUP BY
                    app_id,
                    nome_mercado
                HAVING COUNT(*) > 1
                ORDER BY quantidade DESC, nome_referencia
                """,
            )

            # 2. IDs externos equivalentes pela collation.
            colisoes_variantes = executar_consulta(
                conexao,
                """
                SELECT
                    fonte,
                    MIN(id_externo) AS id_referencia,
                    COUNT(*) AS quantidade,
                    COUNT(DISTINCT categoria) AS categorias_distintas
                FROM auditoria_adicionais_variantes
                GROUP BY
                    fonte,
                    id_externo
                HAVING COUNT(*) > 1
                ORDER BY quantidade DESC, id_referencia
                """,
            )

            # 3. Nomes comerciais já presentes no banco.
            itens_existentes = executar_consulta(
                conexao,
                """
                SELECT
                    novo.categoria,
                    novo.nome_mercado AS nome_novo,
                    novo.tipo_item AS tipo_novo,
                    existente.id AS item_catalogo_id,
                    existente.nome_mercado AS nome_existente,
                    existente.tipo_item AS tipo_existente
                FROM auditoria_adicionais_itens AS novo
                INNER JOIN itens_catalogo AS existente
                    ON existente.app_id = novo.app_id
                    AND existente.nome_mercado = novo.nome_mercado
                ORDER BY novo.categoria, novo.nome_mercado
                """,
            )

            # 4. Variantes já cadastradas, com seus vínculos.
            variantes_existentes = executar_consulta(
                conexao,
                """
                SELECT
                    nova.categoria,
                    nova.fonte,
                    nova.id_externo,
                    nova.nome_mercado AS nome_novo,
                    existente.id AS variante_id,
                    existente.item_catalogo_id,
                    item_atual.app_id AS app_id_atual,
                    item_atual.nome_mercado AS nome_atual,
                    item_atual.tipo_item AS tipo_atual,
                    item_esperado.id AS item_esperado_id
                FROM auditoria_adicionais_variantes AS nova
                INNER JOIN variantes_itens_catalogo AS existente
                    ON existente.fonte = nova.fonte
                    AND existente.id_externo = nova.id_externo
                INNER JOIN itens_catalogo AS item_atual
                    ON item_atual.id = existente.item_catalogo_id
                LEFT JOIN itens_catalogo AS item_esperado
                    ON item_esperado.app_id = nova.app_id
                    AND item_esperado.nome_mercado = nova.nome_mercado
                ORDER BY nova.categoria, nova.id_externo
                """,
            )

        finally:
            conexao.execute(
                text(
                    "DROP TEMPORARY TABLE IF EXISTS "
                    "auditoria_adicionais_variantes"
                )
            )

            conexao.execute(
                text(
                    "DROP TEMPORARY TABLE IF EXISTS "
                    "auditoria_adicionais_itens"
                )
            )

    conflitos_tipos = [
        registro
        for registro in itens_existentes
        if registro["tipo_novo"] != registro["tipo_existente"]
    ]

    variantes_compativeis = [
        registro
        for registro in variantes_existentes
        if (
            registro["item_esperado_id"] is not None
            and registro["item_catalogo_id"]
            == registro["item_esperado_id"]
        )
    ]

    conflitos_vinculos = [
        registro
        for registro in variantes_existentes
        if (
            registro["item_esperado_id"] is None
            or registro["item_catalogo_id"]
            != registro["item_esperado_id"]
        )
    ]

    exibir_resultados(
        "COLISOES COMERCIAIS ENTRE NOVAS CATEGORIAS",
        colisoes_comerciais,
    )

    exibir_resultados(
        "COLISOES DE IDS EXTERNOS ENTRE NOVAS CATEGORIAS",
        colisoes_variantes,
    )

    exibir_resultados(
        "ITENS COMERCIAIS JA EXISTENTES NO MYSQL",
        itens_existentes,
    )

    exibir_resultados(
        "CONFLITOS DE TIPO COM ITENS EXISTENTES",
        conflitos_tipos,
    )

    exibir_resultados(
        "VARIANTES EXISTENTES COM VINCULOS COMPATIVEIS",
        variantes_compativeis,
    )

    exibir_resultados(
        "CONFLITOS DE VINCULO COM VARIANTES EXISTENTES",
        conflitos_vinculos,
    )

    problemas = (
        len(colisoes_comerciais)
        + len(colisoes_variantes)
        + len(conflitos_tipos)
        + len(conflitos_vinculos)
    )

    print("\nRESULTADO FINAL")
    print("-" * 50)

    if problemas:
        print(
            f"Auditoria encontrou {problemas} "
            "ocorrencias que exigem analise."
        )
        print(
            "Nao execute a importacao antes "
            "de investigar os conflitos."
        )
        return 1

    print(
        "Nenhum conflito bloqueante identificado "
        "nas verificacoes executadas."
    )

    print(
        "Nenhum item ou variante permanente "
        "foi inserido, atualizado ou excluido."
    )

    return 0

if __name__ == "__main__":
    raise SystemExit(
        auditar_conflitos_categorias_catalogo()
    )