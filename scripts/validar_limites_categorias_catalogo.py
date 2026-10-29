"""Valida limites de campos das novas categorias do catálogo."""

import json

from scripts.importar_categorias_adicionais_csgo_api import (
    CATEGORIAS_EXPANSAO,
)

from skinexa.integrations.catalogo.csgo_api_client import (
    buscar_itens_csgo_api,
)

from skinexa.services.catalogo.normalizacao_itens_adicionais import (
    normalizar_lote_itens_adicionais_csgo_api,
)

LIMITES_ITENS = {
    "nome_mercado": 255,
    "nome_exibicao": 255,
    "tipo_item": 50,
}

LIMITES_VARIANTES = {
    "fonte": 50,
    "id_externo": 100,
}

def validar_limites_categorias_catalogo() -> int:
    """Verifica comprimentos e serialização dos dados normalizados."""

    print("\nSKINEXA - VALIDACAO DOS LIMITES DO CATALOGO")
    print("=" * 50)

    inconsistencias = []
    total_itens = 0
    total_variantes = 0

    for categoria in CATEGORIAS_EXPANSAO:
        registros = buscar_itens_csgo_api(
            categoria
        )

        relatorio = normalizar_lote_itens_adicionais_csgo_api(
            registros,
            categoria=categoria,
        )

        if relatorio.total_rejeitados:
            inconsistencias.append(
                f"{categoria}: "
                f"{relatorio.total_rejeitados} rejeições."
            )

        for item in relatorio.itens:
            total_itens += 1

            for campo, limite in LIMITES_ITENS.items():
                valor = getattr(item, campo)

                if len(valor) > limite:
                    inconsistencias.append(
                        f"{categoria}: {campo} excede "
                        f"{limite} caracteres: "
                        f"{item.nome_mercado}"
                    )

            if item.metadados_origem is not None:
                try:
                    json.dumps(
                        item.metadados_origem,
                        ensure_ascii=False,
                    )
                except (TypeError, ValueError) as erro:
                    inconsistencias.append(
                        f"{categoria}: metadados inválidos "
                        f"em {item.nome_mercado}: {erro}"
                    )

        for variante in relatorio.variantes:
            total_variantes += 1

            for campo, limite in LIMITES_VARIANTES.items():
                valor = getattr(variante, campo)

                if len(valor) > limite:
                    inconsistencias.append(
                        f"{categoria}: {campo} excede "
                        f"{limite} caracteres: "
                        f"{variante.id_externo}"
                    )

        print(
            f"{categoria.upper()}: "
            f"{relatorio.total_normalizados} itens | "
            f"{relatorio.total_variantes_normalizadas} variantes"
        )

    print("\nRESULTADO")
    print("-" * 50)

    print(f"Itens analisados: {total_itens}")
    print(f"Variantes analisadas: {total_variantes}")
    print(f"Inconsistências: {len(inconsistencias)}")

    for inconsistencia in inconsistencias[:20]:
        print(inconsistencia)

    if inconsistencias:
        print("\nValidação não aprovada.")
        return 1

    print("\nLimites verificados com sucesso.")
    print("Nenhum registro foi gravado no MySQL.")

    return 0

if __name__ == "__main__":
    raise SystemExit(
        validar_limites_categorias_catalogo()
    )