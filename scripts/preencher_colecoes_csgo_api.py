"""
Preenche a coluna legada de coleção dos itens do catálogo.

Utiliza as associações entre skins e coleções fornecidas
pela CSGO-API, preservando os registros existentes.

Não gerencia os relacionamentos normalizados entre
coleções, contêineres e itens do catálogo.
"""

import argparse
import sys
import time

from collections import defaultdict
from typing import Any, Callable, TypeVar

from sqlalchemy import bindparam, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import (
    OperationalError,
    SQLAlchemyError,
)

from skinexa.database.connection import engine

from skinexa.integrations.catalogo.csgo_api_client import (
    ErroCSGOAPI,
    buscar_itens_csgo_api,
)

TAMANHO_LOTE = 250
MAX_TENTATIVAS = 3
ESPERA_RECONEXAO = 2
RENOVAR_POOL_CADA = 10

T = TypeVar("T")

def construir_mapa_colecoes(
    colecoes: list[dict[str, Any]],
) -> dict[str, str]:
    """Relaciona cada skin_id à sua coleção."""

    mapa: dict[str, str] = {}

    for colecao in colecoes:
        nome = colecao.get("name")
        itens = colecao.get("contains")

        if not isinstance(nome, str) or not nome.strip():
            raise ValueError(
                "Coleção sem nome válido."
            )

        if not isinstance(itens, list):
            raise ValueError(
                f"Relacionamentos inválidos: {nome}."
            )

        nome = nome.strip()

        for item in itens:
            if not isinstance(item, dict):
                raise ValueError(
                    f"Item inválido na coleção: {nome}."
                )

            skin_id = item.get("id")

            if not isinstance(skin_id, str) or not skin_id.strip():
                raise ValueError(
                    f"Skin sem identificador: {nome}."
                )

            skin_id = skin_id.strip()
            anterior = mapa.get(skin_id)

            if anterior is not None and anterior != nome:
                raise ValueError(
                    f"Skin {skin_id} associada a "
                    f"coleções diferentes: "
                    f"{anterior} / {nome}."
                )

            mapa[skin_id] = nome

    return mapa

def obter_registros_catalogo(
    conexao: Connection,
) -> list[dict[str, Any]]:
    """Lê itens com skin_id da CSGO-API."""

    consulta = text(
        """
        SELECT
            id,
            colecao,
            JSON_UNQUOTE(
                JSON_EXTRACT(
                    metadados_origem,
                    '$.skin_id'
                )
            ) AS skin_id
        FROM itens_catalogo
        WHERE JSON_VALID(metadados_origem)
          AND JSON_UNQUOTE(
                JSON_EXTRACT(
                    metadados_origem,
                    '$.fonte'
                )
              ) = 'csgo_api'
          AND JSON_EXTRACT(
                metadados_origem,
                '$.skin_id'
              ) IS NOT NULL
        """
    )

    return [
        dict(registro)
        for registro in conexao.execute(
            consulta
        ).mappings()
    ]

def preparar_atualizacoes(
    registros: list[dict[str, Any]],
    mapa: dict[str, str],
) -> tuple[dict[str, list[int]], dict[str, int]]:
    """Identifica associações válidas e conflitos."""

    atualizacoes: dict[str, list[int]] = defaultdict(list)

    ids_encontrados: set[str] = set()

    total_sem_correspondencia = 0
    total_ja_preenchidos = 0
    total_conflitos = 0

    for registro in registros:
        skin_id = registro["skin_id"]
        nome_colecao = mapa.get(skin_id)

        if nome_colecao is None:
            total_sem_correspondencia += 1
            continue

        ids_encontrados.add(skin_id)

        colecao_atual = registro["colecao"]

        if (
            isinstance(colecao_atual, str)
            and colecao_atual.strip()
        ):
            if colecao_atual.strip() == nome_colecao:
                total_ja_preenchidos += 1
            else:
                total_conflitos += 1

            continue

        atualizacoes[nome_colecao].append(
            int(registro["id"])
        )

    resumo = {
        "registros_analisados": len(registros),
        "skin_ids_correspondentes": len(ids_encontrados),
        "skin_ids_api_sem_correspondencia": (
            len(mapa) - len(ids_encontrados)
        ),
        "registros_sem_correspondencia": (
            total_sem_correspondencia
        ),
        "registros_ja_preenchidos": (
            total_ja_preenchidos
        ),
        "registros_com_conflito": total_conflitos,
        "registros_para_atualizar": sum(
            len(ids)
            for ids in atualizacoes.values()
        ),
    }

    return dict(atualizacoes), resumo

def executar_com_retentativas(
    operacao: Callable[[], T],
    *,
    descricao: str,
) -> T:
    """
    Repete uma operação após perda de conexão MySQL.

    A operação deve abrir e fechar sua própria conexão.
    """

    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            return operacao()

        except OperationalError as erro:
            codigo_mysql = (
                erro.orig.args[0]
                if getattr(erro.orig, "args", None)
                else None
            )

            conexao_perdida = (
                codigo_mysql in (2006, 2013)
                or erro.connection_invalidated
            )

            if not conexao_perdida:
                raise

            engine.dispose()

            if tentativa == MAX_TENTATIVAS:
                print(
                    f"Falha definitiva: {descricao}. "
                    f"Tentativas: {MAX_TENTATIVAS}."
                )
                raise

            print(
                f"Conexão perdida em {descricao}. "
                f"Nova tentativa: "
                f"{tentativa + 1}/{MAX_TENTATIVAS}."
            )

            time.sleep(ESPERA_RECONEXAO)

    raise RuntimeError(
        "Não foi possível concluir a operação."
    )

def consultar_catalogo() -> tuple[str, list[dict[str, Any]]]:
    """Consulta o MySQL com recuperação de conexão."""

    def operacao() -> tuple[str, list[dict[str, Any]]]:
        with engine.connect() as conexao:
            banco = conexao.execute(
                text("SELECT DATABASE()")
            ).scalar_one()

            if not banco:
                raise RuntimeError(
                    "Nenhum banco de dados foi selecionado."
                )

            registros = obter_registros_catalogo(
                conexao
            )

            return str(banco), registros

    return executar_com_retentativas(
        operacao,
        descricao="leitura do catálogo",
    )

def criar_lotes(
    atualizacoes: dict[str, list[int]],
) -> list[tuple[str, list[int]]]:
    """Organiza os IDs em lotes de até TAMANHO_LOTE."""

    lotes: list[tuple[str, list[int]]] = []

    for nome_colecao, ids in sorted(
        atualizacoes.items()
    ):
        ids_ordenados = sorted(ids)

        for inicio in range(
            0,
            len(ids_ordenados),
            TAMANHO_LOTE,
        ):
            lotes.append(
                (
                    nome_colecao,
                    ids_ordenados[
                        inicio:inicio + TAMANHO_LOTE
                    ],
                )
            )

    return lotes


CONSULTA_ATUALIZACAO = text(
    """
    UPDATE itens_catalogo
    SET colecao = :colecao
    WHERE id IN :ids
      AND (
          colecao IS NULL
          OR TRIM(colecao) = ''
      )
    """
).bindparams(
    bindparam("ids", expanding=True)
)

CONSULTA_VERIFICACAO = text(
    """
    SELECT COUNT(*)
    FROM itens_catalogo
    WHERE id IN :ids
      AND colecao = :colecao
    """
).bindparams(
    bindparam("ids", expanding=True)
)

def atualizar_lote(
    nome_colecao: str,
    ids: list[int],
) -> int:
    """
    Atualiza um lote em transação independente.

    A verificação permite repetir o lote mesmo
    quando há perda de conexão durante o commit.
    """

    if not ids:
        return 0

    def operacao() -> int:
        with engine.begin() as conexao:
            conexao.execute(
                CONSULTA_ATUALIZACAO,
                {
                    "colecao": nome_colecao,
                    "ids": ids,
                },
            )

            total_confirmado = int(
                conexao.execute(
                    CONSULTA_VERIFICACAO,
                    {
                        "colecao": nome_colecao,
                        "ids": ids,
                    },
                ).scalar_one()
            )

            if total_confirmado != len(ids):
                raise RuntimeError(
                    "O lote contém registros ausentes "
                    "ou coleções conflitantes. "
                    "A transação será revertida."
                )

        return len(ids)

    return executar_com_retentativas(
        operacao,
        descricao=f"coleção {nome_colecao}",
    )

def executar(*, gravar: bool = False) -> None:
    """Exibe a prévia e opcionalmente grava por lotes."""

    print("\nSKINEXA - ENRIQUECIMENTO DE COLECOES")
    print("-" * 50)

    print("\nConsultando coleções da CSGO-API...")

    colecoes = buscar_itens_csgo_api(
        "collections"
    )

    mapa = construir_mapa_colecoes(
        colecoes
    )

    print(f"Coleções recebidas: {len(colecoes)}")
    print(f"Skins mapeadas: {len(mapa)}")

    print("\nConsultando o catálogo MySQL...")

    banco, registros = consultar_catalogo()

    print(f"Banco de dados: {banco}")

    atualizacoes, resumo = preparar_atualizacoes(
        registros,
        mapa,
    )

    print("\nDIAGNOSTICO DO MYSQL")
    print("-" * 50)

    for campo, quantidade in resumo.items():
        print(f"{campo}: {quantidade}")

    lotes = criar_lotes(atualizacoes)

    print(
        "Coleções com atualizações: "
        f"{len(atualizacoes)}"
    )

    print(f"Lotes preparados: {len(lotes)}")

    if resumo["registros_com_conflito"] > 0:
        raise RuntimeError(
            "Foram identificadas coleções conflitantes. "
            "Nenhuma atualização será executada."
        )

    if not gravar:
        print("\nMODO PREVIA")
        print("Nenhum registro foi alterado.")
        return

    if not lotes:
        print("\nNenhuma atualização necessária.")
        return

    print("\nINICIANDO ATUALIZACAO NO MYSQL")
    print("-" * 50)

    total_confirmado = 0
    colecoes_confirmadas: set[str] = set()

    total_lotes = len(lotes)

    for indice_lote, (nome_colecao, ids) in enumerate(
        lotes,
        start=1,
    ):
        total_lote = atualizar_lote(
            nome_colecao,
            ids,
        )

        total_confirmado += total_lote
        colecoes_confirmadas.add(nome_colecao)

        print(
            f"Lote {indice_lote}/{total_lotes} "
            f"confirmado | "
            f"Coleção: {nome_colecao} | "
            f"Itens: {total_lote} | "
            f"Total confirmado: {total_confirmado}"
        )

        if (
            indice_lote % RENOVAR_POOL_CADA == 0
            and indice_lote < total_lotes
        ):
            engine.dispose()

            print(
                "Pool de conexões renovado "
                f"após {indice_lote} lotes."
            )

    if total_confirmado != resumo["registros_para_atualizar"]:
        raise RuntimeError(
            "A quantidade de itens confirmados "
            "divergiu da quantidade planejada."
        )

    print("\nENRIQUECIMENTO CONCLUIDO")
    print("-" * 50)

    print(
        "Coleções processadas: "
        f"{len(colecoes)}"
    )

    print(
        "Coleções enriquecidas: "
        f"{len(colecoes_confirmadas)}"
    )

    print(
        "Lotes confirmados: "
        f"{total_lotes}"
    )

    print(
        "Itens confirmados: "
        f"{total_confirmado}"
    )

def main() -> int:
    """Processa argumentos de execução."""

    parser = argparse.ArgumentParser(
        description=(
            "Enriquece as coleções dos itens "
            "existentes no catálogo Skinexa."
        )
    )

    parser.add_argument(
        "--executar",
        action="store_true",
        help="Habilita a atualização do MySQL.",
    )

    parser.add_argument(
        "--confirmar-atualizacao",
        action="store_true",
        help="Confirma explicitamente a gravação.",
    )

    argumentos = parser.parse_args()

    if argumentos.executar != argumentos.confirmar_atualizacao:
        parser.error(
            "Para atualizar, utilize --executar "
            "e --confirmar-atualizacao juntos."
        )

    try:
        executar(
            gravar=argumentos.executar
        )

    except (
        ErroCSGOAPI,
        SQLAlchemyError,
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