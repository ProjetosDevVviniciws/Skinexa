from dataclasses import dataclass

from skinexa.database.connection import engine

from skinexa.integrations.bcb.client import (
    buscar_cotacao_usd_brl,
)

from skinexa.integrations.csfloat.client import (
    buscar_precos_csfloat,
)

from skinexa.integrations.csfloat.normalizador_preco import (
    normalizar_precos_csfloat,
)

from skinexa.services.precos.service import (
    ResultadoRegistroPrecos,
    registrar_precos,
)

@dataclass(frozen=True, slots=True)
class ResultadoSincronizacaoPrecosCSFloat:
    """Resultado da sincronização de preços da CSFloat."""

    nome_mercado: str
    total_anuncios: int
    resultado_registro: ResultadoRegistroPrecos

def coletar_preco_csfloat(
    *,
    nome_mercado: str,
):
    """
    Consulta os anúncios da CSFloat e converte
    os preços para o formato interno do Skinexa.
    """

    consulta = buscar_precos_csfloat(
        nome_mercado=nome_mercado,
    )

    if not consulta.itens:
        return None

    cotacao = buscar_cotacao_usd_brl()

    return normalizar_precos_csfloat(
        consulta.itens,
        taxa_usd_brl=cotacao.taxa,
    )

def sincronizar_preco_csfloat(
    *,
    nome_mercado: str,
) -> ResultadoSincronizacaoPrecosCSFloat:
    """
    Consulta, normaliza e persiste o preço
    de um item obtido da CSFloat.
    """

    consulta = buscar_precos_csfloat(
        nome_mercado=nome_mercado,
    )

    total_anuncios = len(
        consulta.itens
    )

    if not consulta.itens:
        return ResultadoSincronizacaoPrecosCSFloat(
            nome_mercado=nome_mercado,
            total_anuncios=0,
            resultado_registro=ResultadoRegistroPrecos(
                total_recebido=0,
                total_registrado=0,
                total_ignorado=0,
            ),
        )

    cotacao = buscar_cotacao_usd_brl()

    preco = normalizar_precos_csfloat(
        consulta.itens,
        taxa_usd_brl=cotacao.taxa,
    )

    with engine.begin() as conexao:
        resultado_registro = registrar_precos(
            conexao,
            [preco],
        )

    return ResultadoSincronizacaoPrecosCSFloat(
        nome_mercado=nome_mercado,
        total_anuncios=total_anuncios,
        resultado_registro=resultado_registro,
    )