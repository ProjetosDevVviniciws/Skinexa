"""Executa a validação da alimentação inicial do catálogo CS2."""

import argparse

import sys

import time

from sqlalchemy.exc import OperationalError

from collections import Counter

from dataclasses import replace

from skinexa.integrations.catalogo.csgo_api_client import (
    ErroCSGOAPI,
    buscar_itens_csgo_api,
)

from skinexa.services.catalogo.normalizacao_lote import (
    normalizar_lote_skins_csgo_api,
)

from skinexa.dto.catalogo.normalizacao_lote import (
    RelatorioNormalizacaoCatalogoDTO,
)

def executar_validacao_catalogo(
    *,
    limite: int | None = None,
) -> RelatorioNormalizacaoCatalogoDTO:
    """Consulta e normaliza skins sem persistir dados no banco."""

    if limite is not None and limite < 1:
        raise ValueError(
            "O limite deve ser maior que zero."
        )

    print("\nSKINEXA - VALIDACAO DO CATALOGO CS2")
    print("-" * 50)

    print("\nConsultando a CSGO-API...")

    registros = buscar_itens_csgo_api(
        "skins"
    )

    total_disponiveis = len(registros)

    if limite is not None:
        registros = registros[:limite]

    print(
        f"Registros disponíveis na origem: "
        f"{total_disponiveis}"
    )

    print(
        f"Registros selecionados: "
        f"{len(registros)}"
    )

    print("\nNormalizando registros...")

    relatorio = normalizar_lote_skins_csgo_api(
        registros
    )

    print("\nRELATORIO DE NORMALIZACAO")
    print("-" * 50)

    print(
        f"Recebidos: "
        f"{relatorio.total_recebidos}"
    )

    print(
        f"Itens comerciais: "
        f"{relatorio.total_normalizados}"
    )

    print(
        f"Variantes: "
        f"{relatorio.total_variantes_normalizadas}"
    )

    print(
        f"Rejeitados: "
        f"{relatorio.total_rejeitados}"
    )

    print(
        f"Duplicacoes comerciais: "
        f"{relatorio.total_duplicados}"
    )

    print(
        f"Variantes duplicadas: "
        f"{relatorio.total_variantes_duplicadas}"
    )

    print("\nINTEGRIDADE DOS RELACIONAMENTOS")
    print("-" * 50)

    chaves_comerciais = {
        (
            item.app_id,
            item.nome_mercado,
        )
        for item in relatorio.itens
    }

    variantes_sem_item = [
        variante
        for variante in relatorio.variantes
        if (
            variante.app_id,
            variante.nome_mercado,
        ) not in chaves_comerciais
    ]

    print(
        f"Variantes sem item comercial: "
        f"{len(variantes_sem_item)}"
    )

    print("\nDISTRIBUICAO POR TIPO DE ITEM")
    print("-" * 50)

    tipos = Counter(
        item.tipo_item
        for item in relatorio.itens
    )

    for tipo, quantidade in sorted(
        tipos.items()
    ):
        print(
            f"{tipo}: {quantidade}"
        )

    print("\nMOTIVOS DE REJEICAO")
    print("-" * 50)

    if relatorio.motivos_rejeicao:
        for motivo, quantidade in sorted(
            relatorio.motivos_rejeicao.items()
        ):
            print(
                f"{quantidade} | {motivo}"
            )
    else:
        print("Nenhuma rejeicao encontrada.")

    print("\nRESULTADO DA VALIDACAO")
    print("-" * 50)

    if (
        relatorio.total_rejeitados > 0
        or variantes_sem_item
    ):
        raise RuntimeError(
            "A validação identificou inconsistências "
            "que precisam ser analisadas."
        )

    print("Normalizacao concluida com sucesso.")
    print("Nenhum registro foi gravado no MySQL.")
    
    return relatorio

def executar_importacao_catalogo(
    relatorio: RelatorioNormalizacaoCatalogoDTO,
    *,
    tamanho_lote: int = 100,
    validar_vinculos: bool = False,
) -> tuple[int, int]:
    """
    Importa itens e variantes em transações independentes.

    Cada lote agrupa os itens comerciais e todas as
    variantes pertencentes a esses itens.
    """

    from sqlalchemy import text

    from skinexa.database.connection import engine

    from skinexa.services.catalogo.importacao import (
        importar_lote_catalogo,
    )

    if tamanho_lote <= 0:
        raise ValueError(
            "O tamanho do lote deve ser maior que zero."
        )

    if relatorio.total_rejeitados > 0:
        raise ValueError(
            "Não é permitido importar um lote com rejeições."
        )

    if (
        relatorio.total_normalizados == 0
        or relatorio.total_variantes_normalizadas == 0
    ):
        raise ValueError(
            "Não é permitido importar um lote vazio."
        )

    chaves_comerciais = {
        (
            item.app_id,
            item.nome_mercado,
        )
        for item in relatorio.itens
    }

    variantes_por_item = {
        chave: []
        for chave in chaves_comerciais
    }

    for variante in relatorio.variantes:
        chave = (
            variante.app_id,
            variante.nome_mercado,
        )

        if chave not in variantes_por_item:
            raise ValueError(
                "Variante sem item comercial correspondente."
            )

        variantes_por_item[chave].append(
            variante
        )

    total_itens = 0
    total_variantes = 0

    itens = relatorio.itens

    total_lotes = (
        len(itens) + tamanho_lote - 1
    ) // tamanho_lote

    print("\nINICIANDO IMPORTACAO NO MYSQL")
    print("-" * 50)

    max_tentativas = 3
    for indice_lote, inicio in enumerate(
        range(0, len(itens), tamanho_lote),
        start=1,
    ):
        itens_lote = itens[
            inicio:inicio + tamanho_lote
        ]

        variantes_lote = []

        for item in itens_lote:
            chave = (
                item.app_id,
                item.nome_mercado,
            )

            variantes_lote.extend(
                variantes_por_item[chave]
            )

        relatorio_lote = replace(
            relatorio,
            total_recebidos=len(variantes_lote),
            total_normalizados=len(itens_lote),
            total_rejeitados=0,
            total_duplicados=(
                len(variantes_lote) - len(itens_lote)
            ),
            itens=tuple(itens_lote),
            erros=(),
            motivos_rejeicao={},
            total_variantes_normalizadas=len(
                variantes_lote
            ),
            total_variantes_duplicadas=0,
            variantes=tuple(variantes_lote),
        )

        for tentativa in range(1, max_tentativas + 1):
            try:
                with engine.begin() as conexao:
                    if indice_lote == 1:
                        banco_atual = conexao.execute(
                            text("SELECT DATABASE()")
                        ).scalar_one()

                        if not banco_atual:
                            raise RuntimeError(
                                "Nenhum banco de dados foi selecionado."
                            )

                        print(
                            f"Banco de dados: {banco_atual}"
                        )

                    if validar_vinculos:
                        itens_processados, variantes_processadas = (
                            importar_lote_catalogo(
                                conexao,
                                relatorio_lote,
                                validar_vinculos=True,
                            )
                        )
                    else:
                        itens_processados, variantes_processadas = (
                            importar_lote_catalogo(
                                conexao,
                                relatorio_lote,
                            )
                        )

                break

            except OperationalError as erro:
                codigo_mysql = (
                    erro.orig.args[0]
                    if getattr(erro.orig, "args", None)
                    else None
                )

                if codigo_mysql not in (2006, 2013):
                    raise

                engine.dispose()

                if tentativa == max_tentativas:
                    print(
                        f"Falha definitiva no lote "
                        f"{indice_lote}/{total_lotes}."
                    )
                    raise

                print(
                    f"Conexao perdida no lote "
                    f"{indice_lote}/{total_lotes}. "
                    f"Nova tentativa: "
                    f"{tentativa + 1}/{max_tentativas}"
                )

                time.sleep(2)

        total_itens += itens_processados
        total_variantes += variantes_processadas

        print(
            f"Lote {indice_lote}/{total_lotes} confirmado | "
            f"Itens: {itens_processados} | "
            f"Variantes: {variantes_processadas}"
        )

        if (
            indice_lote % 10 == 0
            and indice_lote < total_lotes
        ):
            engine.dispose()
    print("\nIMPORTACAO CONCLUIDA")
    print("-" * 50)

    print(
        f"Itens comerciais processados: {total_itens}"
    )

    print(
        f"Variantes processadas: {total_variantes}"
    )

    return total_itens, total_variantes

def main() -> int:
    """Processa argumentos e executa a validação ou importação."""

    parser = argparse.ArgumentParser(
        description=(
            "Valida ou importa as skins "
            "do catálogo CS2."
        )
    )

    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help=(
            "Quantidade máxima de registros "
            "processados."
        ),
    )

    parser.add_argument(
        "--executar",
        action="store_true",
        help=(
            "Habilita a persistência "
            "dos registros no MySQL."
        ),
    )

    parser.add_argument(
        "--confirmar-importacao",
        action="store_true",
        help=(
            "Confirma explicitamente a operação "
            "de gravação no banco de dados."
        ),
    )

    argumentos = parser.parse_args()

    if (
        argumentos.confirmar_importacao
        and not argumentos.executar
    ):
        parser.error(
            "--confirmar-importacao exige --executar."
        )

    if (
        argumentos.executar
        and not argumentos.confirmar_importacao
    ):
        parser.error(
            "Para gravar no banco, utilize também "
            "--confirmar-importacao."
        )

    try:
        relatorio = executar_validacao_catalogo(
            limite=argumentos.limite,
        )

        if argumentos.executar:
            executar_importacao_catalogo(
                relatorio,
            )

    except (
        ErroCSGOAPI,
        ValueError,
        RuntimeError,
    ) as erro:
        print(
            f"\nERRO: {erro}",
            file=sys.stderr,
        )

        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())