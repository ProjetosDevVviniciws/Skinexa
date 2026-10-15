"""Audita colisões comerciais usando a collation do MySQL."""

from sqlalchemy import text

from skinexa.database.connection import engine

from skinexa.integrations.catalogo.csgo_api_client import (
    buscar_itens_csgo_api,
)

from skinexa.services.catalogo.normalizacao_lote import (
    normalizar_lote_skins_csgo_api,
)

def auditar_colisoes_catalogo() -> int:
    """Identifica nomes distintos considerados equivalentes pelo MySQL."""

    registros = buscar_itens_csgo_api(
        "skins"
    )

    relatorio = normalizar_lote_skins_csgo_api(
        registros
    )

    print("\nAUDITORIA DE COLISOES DO CATALOGO")
    print("-" * 50)

    print(
        f"Itens comerciais normalizados: "
        f"{relatorio.total_normalizados}"
    )

    if relatorio.total_rejeitados:
        raise RuntimeError(
            "A normalização apresentou registros rejeitados."
        )

    with engine.connect() as conexao:
        conexao.execute(
            text(
                """
                CREATE TEMPORARY TABLE
                    auditoria_nomes_catalogo (
                        app_id INT UNSIGNED NOT NULL,
                        nome_mercado VARCHAR(255) NOT NULL
                    )
                    ENGINE = InnoDB
                    DEFAULT CHARSET = utf8mb4
                    COLLATE = utf8mb4_unicode_ci
                """
            )
        )

        try:
            parametros = [
                {
                    "app_id": item.app_id,
                    "nome_mercado": item.nome_mercado,
                }
                for item in relatorio.itens
            ]

            conexao.execute(
                text(
                    """
                    INSERT INTO auditoria_nomes_catalogo (
                        app_id,
                        nome_mercado
                    )
                    VALUES (
                        :app_id,
                        :nome_mercado
                    )
                    """
                ),
                parametros,
            )

            colisoes = conexao.execute(
                text(
                    """
                    SELECT
                        app_id,
                        MIN(nome_mercado) AS nome_referencia,
                        COUNT(*) AS quantidade
                    FROM auditoria_nomes_catalogo
                    GROUP BY
                        app_id,
                        nome_mercado
                    HAVING COUNT(*) > 1
                    ORDER BY quantidade DESC
                    """
                )
            ).mappings().all()

        finally:
            conexao.execute(
                text(
                    "DROP TEMPORARY TABLE IF EXISTS "
                    "auditoria_nomes_catalogo"
                )
            )

    print(
        f"Grupos com colisões: {len(colisoes)}"
    )

    for colisao in colisoes[:20]:
        print(
            f"{colisao['quantidade']} registros | "
            f"{colisao['nome_referencia']}"
        )

    if colisoes:
        print(
            "\nForam encontradas colisões que "
            "precisam ser analisadas."
        )

        return 1

    print(
        "\nNenhuma colisão encontrada "
        "segundo a collation do MySQL."
    )

    print(
        "Nenhum item comercial ou variante "
        "foi persistido."
    )

    return 0

if __name__ == "__main__":
    raise SystemExit(
        auditar_colisoes_catalogo()
    )