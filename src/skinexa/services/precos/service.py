from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.engine import Connection

from skinexa.database.queries.historico_precos import (
    inserir_historico_preco,
    obter_item_catalogo_id_por_nome_mercado,
    obter_plataforma_mercado_id_por_identificador,
    obter_itens_catalogo_ids_por_nomes_mercado,
    obter_ultimos_precos_itens_plataforma,
)

from skinexa.domain.preco import PrecoMercado, UltimoPrecoMercado

class ErroPrecoService(RuntimeError):
    """Erro durante o processamento de preços."""

class PlataformaMercadoIndisponivel(ErroPrecoService):
    """A plataforma de mercado não está disponível."""

@dataclass(frozen=True, slots=True)
class ResultadoRegistroPrecos:
    """Resume o resultado do registro de preços."""

    total_recebido: int
    total_registrado: int
    total_ignorado: int

def registrar_precos(
    conexao: Connection,
    precos: Iterable[PrecoMercado],
) -> ResultadoRegistroPrecos:
    """
    Registra preços normalizados no histórico.

    Itens que ainda não existem no catálogo
    são ignorados.
    """

    precos_recebidos = tuple(precos)

    total_recebido = len(
        precos_recebidos
    )

    if not precos_recebidos:
        return ResultadoRegistroPrecos(
            total_recebido=0,
            total_registrado=0,
            total_ignorado=0,
        ) 

    nomes_mercado = {
        preco.nome_mercado
        for preco in precos_recebidos
    }

    itens_catalogo = (
        obter_itens_catalogo_ids_por_nomes_mercado(
            conexao,
            nomes_mercado,
        )
    )

    total_registrado = 0
    total_ignorado = 0

    plataformas: dict[str, int] = {}

    for preco in precos:

        plataforma_id = plataformas.get(
            preco.plataforma
        )

        if plataforma_id is None:
            plataforma_id = (
                obter_plataforma_mercado_id_por_identificador(
                    conexao,
                    preco.plataforma,
                )
            )

            if plataforma_id is None:
                raise PlataformaMercadoIndisponivel(
                    "A plataforma de mercado "
                    f"'{preco.plataforma}' não está disponível."
                )

            plataformas[preco.plataforma] = (
                plataforma_id
            )

        item_catalogo_id = itens_catalogo.get(
            preco.nome_mercado
        )

        if item_catalogo_id is None:
            total_ignorado += 1
            continue

        inserir_historico_preco(
            conexao,
            item_catalogo_id=item_catalogo_id,
            plataforma_mercado_id=plataforma_id,
            moeda=preco.moeda,
            menor_preco=preco.menor_preco,
            maior_preco=preco.maior_preco,
            preco_medio=preco.preco_medio,
            preco_mediano=preco.preco_mediano,
            maior_ordem_compra=preco.maior_ordem_compra,
            quantidade_anuncios=preco.quantidade_anuncios,
            volume_vendas=preco.volume_vendas,
            atualizado_na_origem_em=(
                preco.atualizado_na_origem_em
            ),
        )

        total_registrado += 1

    return ResultadoRegistroPrecos(
        total_recebido=total_recebido,
        total_registrado=total_registrado,
        total_ignorado=total_ignorado,
    )
    
def obter_ultimos_precos(
    conexao: Connection,
    *,
    item_catalogo_ids: set[int],
    plataforma: str,
) -> dict[int, UltimoPrecoMercado]:
    """
    Obtém o último preço conhecido de cada item
    para uma determinada plataforma.
    """

    if not item_catalogo_ids:
        return {}

    plataforma_id = (
        obter_plataforma_mercado_id_por_identificador(
            conexao,
            plataforma,
        )
    )

    if plataforma_id is None:
        raise PlataformaMercadoIndisponivel(
            "A plataforma de mercado "
            f"'{plataforma}' "
            "não está disponível."
        )

    registros = (
        obter_ultimos_precos_itens_plataforma(
            conexao,
            item_catalogo_ids=item_catalogo_ids,
            plataforma_mercado_id=plataforma_id,
        )
    )

    return {
        item_catalogo_id: UltimoPrecoMercado(
            item_catalogo_id=item_catalogo_id,
            plataforma=plataforma,
            moeda=str(registro["moeda"]),
            menor_preco=registro["menor_preco"],
            maior_preco=registro["maior_preco"],
            preco_medio=registro["preco_medio"],
            preco_mediano=registro["preco_mediano"],
            maior_ordem_compra=(
                registro["maior_ordem_compra"]
            ),
            quantidade_anuncios=(
                registro["quantidade_anuncios"]
            ),
            volume_vendas=registro["volume_vendas"],
            coletado_em=registro["coletado_em"],
            atualizado_na_origem_em=(
                registro["atualizado_na_origem_em"]
            ),
        )
        for item_catalogo_id, registro
        in registros.items()
    }