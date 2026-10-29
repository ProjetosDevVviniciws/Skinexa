"""Valida e importa categorias adicionais do catálogo CS2."""

import argparse
import sys

from collections import Counter

from skinexa.dto.catalogo.normalizacao_itens_adicionais import (
    RelatorioItensAdicionaisDTO,
)

from skinexa.dto.catalogo.normalizacao_lote import (
    RelatorioNormalizacaoCatalogoDTO,
)

from skinexa.integrations.catalogo.csgo_api_client import (
    ErroCSGOAPI,
    buscar_itens_csgo_api,
)

from skinexa.services.catalogo.normalizacao_itens_adicionais import (
    normalizar_lote_itens_adicionais_csgo_api,
)

from scripts.importar_catalogo_csgo_api import (
    executar_importacao_catalogo,
)

CATEGORIAS_ADICIONAIS = (
    "adesivos",
    "caixas",
    "agentes",
)

CATEGORIAS_EXPANSAO = (
    "patches",
    "chaveiros",
    "grafites",
    "musicas",
    "colecionaveis",
    "adesivos_encapsulados",
    "chaves",
    "destaques",
)

CATEGORIAS_DISPONIVEIS = (
    *CATEGORIAS_ADICIONAIS,
    *CATEGORIAS_EXPANSAO,
)

def adaptar_relatorio_importacao(
    relatorios: list[RelatorioItensAdicionaisDTO],
) -> RelatorioNormalizacaoCatalogoDTO:
    """Converte relatórios adicionais para o contrato do importador."""

    if not relatorios:
        raise ValueError(
            "Nenhum relatório foi informado."
        )

    itens = []
    variantes = []

    total_recebidos = 0
    total_pendentes = 0
    total_rejeitados = 0
    total_duplicados = 0
    total_variantes_duplicadas = 0

    chaves_comerciais = set()
    chaves_variantes = set()

    for relatorio in relatorios:
        total_recebidos += relatorio.total_recebidos
        total_pendentes += (
            relatorio.total_sem_identidade_comercial
        )
        total_rejeitados += relatorio.total_rejeitados
        total_duplicados += relatorio.total_duplicados
        total_variantes_duplicadas += (
            relatorio.total_variantes_duplicadas
        )

        for item in relatorio.itens:
            chave = (
                item.app_id,
                item.nome_mercado,
            )

            if chave in chaves_comerciais:
                raise ValueError(
                    "Item comercial duplicado entre categorias: "
                    f"{item.nome_mercado}"
                )

            chaves_comerciais.add(chave)
            itens.append(item)

        for variante in relatorio.variantes:
            chave = (
                variante.fonte,
                variante.id_externo,
            )

            if chave in chaves_variantes:
                raise ValueError(
                    "ID externo duplicado entre categorias: "
                    f"{variante.id_externo}"
                )

            chaves_variantes.add(chave)
            variantes.append(variante)

    if total_rejeitados:
        raise ValueError(
            "Existem registros rejeitados na normalização."
        )

    if not itens or not variantes:
        raise ValueError(
            "Não existem itens e variantes para importar."
        )

    for variante in variantes:
        chave_comercial = (
            variante.app_id,
            variante.nome_mercado,
        )

        if chave_comercial not in chaves_comerciais:
            raise ValueError(
                "Variante sem item comercial correspondente: "
                f"{variante.id_externo}"
            )

    if total_recebidos != (
        len(itens)
        + total_pendentes
        + total_rejeitados
        + total_duplicados
    ):
        raise ValueError(
            "Os totais dos relatórios estão inconsistentes."
        )

    if (
        len(variantes) + total_variantes_duplicadas
        != total_recebidos
        - total_pendentes
        - total_rejeitados
    ):
        raise ValueError(
            "Os totais das variantes estão inconsistentes."
        )

    return RelatorioNormalizacaoCatalogoDTO(
        total_recebidos=total_recebidos,
        total_normalizados=len(itens),
        total_rejeitados=0,
        total_duplicados=total_duplicados,
        itens=tuple(itens),
        erros=(),
        motivos_rejeicao={},
        total_variantes_normalizadas=len(variantes),
        total_variantes_duplicadas=(
            total_variantes_duplicadas
        ),
        variantes=tuple(variantes),
    )

def executar_validacao_categorias_adicionais(
    *,
    limite: int | None = None,
    categorias: tuple[str, ...] = CATEGORIAS_ADICIONAIS,
) -> RelatorioNormalizacaoCatalogoDTO:
    """Valida categorias adicionais sem persistir dados."""

    if limite is not None and limite < 1:
        raise ValueError(
            "O limite deve ser maior que zero."
        )

    if not categorias:
        raise ValueError(
            "É necessário informar pelo menos uma categoria."
        )

    if len(categorias) != len(set(categorias)):
        raise ValueError(
            "Foram informadas categorias repetidas."
        )

    categorias_invalidas = (
        set(categorias) - set(CATEGORIAS_DISPONIVEIS)
    )

    if categorias_invalidas:
        raise ValueError(
            "Categorias não suportadas: "
            + ", ".join(sorted(categorias_invalidas))
        )
    
    print("\nSKINEXA - VALIDACAO DE CATEGORIAS ADICIONAIS")
    print("=" * 50)

    relatorios = []

    for categoria in categorias:
        print(
            f"\nConsultando categoria: {categoria.upper()}"
        )

        registros = buscar_itens_csgo_api(
            categoria
        )

        if limite is not None:
            registros = registros[:limite]

        relatorio = normalizar_lote_itens_adicionais_csgo_api(
            registros,
            categoria=categoria,
        )

        relatorios.append(relatorio)

        print(
            f"Recebidos: {relatorio.total_recebidos}"
        )
        print(
            f"Itens comerciais: {relatorio.total_normalizados}"
        )
        print(
            "Variantes externas: "
            f"{relatorio.total_variantes_normalizadas}"
        )
        print(
            "Sem identidade comercial: "
            f"{relatorio.total_sem_identidade_comercial}"
        )
        print(
            f"Rejeitados: {relatorio.total_rejeitados}"
        )

    relatorio_importacao = adaptar_relatorio_importacao(
        relatorios
    )

    total_pendentes = sum(
        relatorio.total_sem_identidade_comercial
        for relatorio in relatorios
    )

    print("\nRELATORIO CONSOLIDADO")
    print("-" * 50)

    print(
        f"Registros recebidos: "
        f"{relatorio_importacao.total_recebidos}"
    )
    print(
        f"Itens comerciais: "
        f"{relatorio_importacao.total_normalizados}"
    )
    print(
        "Variantes externas: "
        f"{relatorio_importacao.total_variantes_normalizadas}"
    )
    print(
        f"Sem identidade comercial: {total_pendentes}"
    )

    tipos = Counter(
        item.tipo_item
        for item in relatorio_importacao.itens
    )

    print("\nDISTRIBUICAO POR TIPO")
    print("-" * 50)

    for tipo, quantidade in sorted(
        tipos.items()
    ):
        print(
            f"{tipo}: {quantidade}"
        )

    print("\nValidacao concluida com sucesso.")
    print("Nenhum registro foi gravado no MySQL.")

    return relatorio_importacao

def main() -> int:
    """Processa argumentos e valida ou importa as categorias."""

    parser = argparse.ArgumentParser(
        description=(
            "Valida ou importa adesivos, caixas "
            "e agentes da CSGO-API."
        )
    )

    parser.add_argument(
        "--limite",
        type=int,
        default=None,
        help="Limite de registros por categoria.",
    )

    parser.add_argument(
        "--categorias",
        nargs="+",
        choices=CATEGORIAS_DISPONIVEIS,
        default=None,
        help=(
            "Categorias a processar. "
            "Por padrão, utiliza adesivos, caixas e agentes."
        ),
    )
    
    parser.add_argument(
        "--executar",
        action="store_true",
        help="Habilita a importação no MySQL.",
    )

    parser.add_argument(
        "--confirmar-importacao",
        action="store_true",
        help="Confirma explicitamente a gravação.",
    )

    argumentos = parser.parse_args()

    categorias_selecionadas = (
        tuple(argumentos.categorias)
        if argumentos.categorias is not None
        else CATEGORIAS_ADICIONAIS
    )
    
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
            "Para gravar no MySQL, informe também "
            "--confirmar-importacao."
        )

    try:
        relatorio = executar_validacao_categorias_adicionais(
            limite=argumentos.limite,
            categorias=categorias_selecionadas,
        )

        if argumentos.executar:
            executar_importacao_catalogo(
                relatorio,
                tamanho_lote=100,
                validar_vinculos=True,
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