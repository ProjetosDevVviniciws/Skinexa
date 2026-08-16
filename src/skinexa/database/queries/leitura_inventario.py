from typing import Any

from sqlalchemy import text

from skinexa.database.connection import engine

def listar_itens_inventario(
    usuario_id: int,
    *,
    limite: int = 20,
    deslocamento: int = 0,
    busca: str | None = None,
) -> list[dict[str, Any]]:
    """Retorna os itens ativos do inventário do usuário."""

    busca_normalizada = (
        busca.strip()
        if busca is not None
        else None
    )
    
    if not busca_normalizada:
        busca_normalizada = None
    
    consulta = text(
        """
        SELECT
            ii.id AS instancia_id,
            ii.asset_id,
            ii.quantidade,
            ii.valor_float,
            ii.stattrak,
            ii.souvenir,
            ii.trocavel,
            ii.comercializavel,
            ii.bloqueado_ate,
            ii.ultima_visualizacao_em,

            ic.id AS item_catalogo_id,
            ic.nome_mercado,
            ic.nome_exibicao,
            ic.tipo_item,
            ic.nome_arma,
            ic.nome_acabamento,
            ic.estado_exterior,
            ic.raridade,
            ic.qualidade,
            ic.colecao,
            ic.url_icone,
            ic.url_icone_grande

        FROM instancias_itens AS ii

        INNER JOIN itens_catalogo AS ic
            ON ic.id = ii.item_catalogo_id

        WHERE ii.usuario_id = :usuario_id
          AND ii.ativo = 1

        AND (
            :busca IS NULL
            OR ic.nome_mercado LIKE :busca_like
            OR ic.nome_exibicao LIKE :busca_like
            OR ic.nome_arma LIKE :busca_like
            OR ic.nome_acabamento LIKE :busca_like
        )
        
        ORDER BY ic.nome_mercado ASC

        LIMIT :limite
        OFFSET :deslocamento
        """
    )

    parametros = {
        "usuario_id": usuario_id,
        "limite": limite,
        "deslocamento": deslocamento,
        "busca": busca_normalizada,
        "busca_like": (
            f"%{busca_normalizada}%"
            if busca_normalizada
            else None
        ),
    }   

    with engine.connect() as conexao:
        resultado = conexao.execute(
            consulta,
            parametros,
        ).mappings().all()

    return [
        dict(registro)
        for registro in resultado
    ]

def contar_itens_inventario(
    usuario_id: int,
    *,
    busca: str | None = None,
) -> int:
    """Retorna a quantidade de itens ativos do usuário."""

    busca_normalizada = (
        busca.strip()
        if busca is not None
        else None
    )

    if not busca_normalizada:
        busca_normalizada = None
    
    consulta = text(
        """
        SELECT COUNT(*)
        
        FROM instancias_itens AS ii
        
        INNER JOIN itens_catalogo AS ic
            ON ic.id = ii.item_catalogo_id
            
        WHERE ii.usuario_id = :usuario_id
          AND ii.ativo = 1
          AND (
            :busca IS NULL
            OR ic.nome_mercado LIKE :busca_like
            OR ic.nome_exibicao LIKE :busca_like
            OR ic.nome_arma LIKE :busca_like
            OR ic.nome_acabamento LIKE :busca_like
          )
        """
    )

    parametros = {
        "usuario_id": usuario_id,
        "busca": busca_normalizada,
        "busca_like": (
            f"%{busca_normalizada}%"
            if busca_normalizada
            else None
        ),
    }
    
    with engine.connect() as conexao:
        total = conexao.execute(
            consulta,
            parametros,
        ).scalar_one()

    return int(total)