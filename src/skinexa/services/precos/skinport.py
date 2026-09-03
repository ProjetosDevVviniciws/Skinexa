from sqlalchemy.engine import Connection

from skinexa.database.connection import engine

from skinexa.integrations.skinport.client import (
    buscar_precos_skinport,
)
from skinexa.integrations.skinport.normalizador_preco import (
    normalizar_preco_skinport,
)
from skinexa.services.precos.service import (
    ResultadoRegistroPrecos,
    registrar_precos,
)

def coletar_precos_skinport(
    conexao: Connection,
    *,
    moeda: str = "BRL",
) -> ResultadoRegistroPrecos:
    """
    Coleta preços da Skinport e registra
    os itens conhecidos pelo Skinexa.
    """

    consulta = buscar_precos_skinport(
        moeda=moeda,
    )

    precos_normalizados = (
        normalizar_preco_skinport(preco)
        for preco in consulta.itens
    )

    return registrar_precos(
        conexao,
        precos_normalizados,
    )
    
def sincronizar_precos_skinport(
    *,
    moeda: str = "BRL",
) -> ResultadoRegistroPrecos:
    """
    Consulta a Skinport e registra os preços
    conhecidos pelo Skinexa em uma transação.
    """

    consulta = buscar_precos_skinport(
        moeda=moeda,
    )

    precos_normalizados = tuple(
        normalizar_preco_skinport(preco)
        for preco in consulta.itens
    )

    with engine.begin() as conexao:
        return registrar_precos(
            conexao,
            precos_normalizados,
        )