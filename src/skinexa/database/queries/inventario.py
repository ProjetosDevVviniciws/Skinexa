import json

from sqlalchemy import text
from sqlalchemy.engine import Connection

from skinexa.dto.steam.inventario import InstanciaItemSteamDTO

def desativar_instancias_usuario(
    conexao: Connection,
    usuario_id: int,
) -> None:
    """
    Marca temporariamente como inativos todos os itens do usuário.

    Os itens presentes na sincronização atual serão reativados
    pelas operações de criação ou atualização.
    """

    consulta = text(
        """
        UPDATE instancias_itens
        SET
            ativo = 0,
            removido_em = UTC_TIMESTAMP()
        WHERE usuario_id = :usuario_id
          AND ativo = 1
        """
    )

    conexao.execute(
        consulta,
        {"usuario_id": usuario_id},
    )

def salvar_instancia_item(
    conexao: Connection,
    *,
    usuario_id: int,
    item_catalogo_id: int,
    item: InstanciaItemSteamDTO,
) -> int:
    """Cria ou atualiza uma instância do inventário."""

    consulta = text(
        """
        INSERT INTO instancias_itens (
            usuario_id,
            item_catalogo_id,
            app_id,
            contexto_id,
            asset_id,
            class_id,
            instance_id,
            indice_definicao,
            indice_pintura,
            semente_pintura,
            valor_float,
            nome_personalizado,
            link_inspecao,
            stattrak,
            contador_stattrak,
            souvenir,
            trocavel,
            comercializavel,
            bloqueado_ate,
            quantidade,
            primeira_visualizacao_em,
            ultima_visualizacao_em,
            removido_em,
            ativo,
            fonte_dados,
            metadados_origem
        )
        VALUES (
            :usuario_id,
            :item_catalogo_id,
            :app_id,
            :contexto_id,
            :asset_id,
            :class_id,
            :instance_id,
            :indice_definicao,
            :indice_pintura,
            :semente_pintura,
            :valor_float,
            :nome_personalizado,
            :link_inspecao,
            :stattrak,
            :contador_stattrak,
            :souvenir,
            :trocavel,
            :comercializavel,
            :bloqueado_ate,
            :quantidade,
            UTC_TIMESTAMP(),
            UTC_TIMESTAMP(),
            NULL,
            1,
            :fonte_dados,
            CAST(:metadados_origem AS JSON)
        )
        ON DUPLICATE KEY UPDATE
            id = LAST_INSERT_ID(id),
            item_catalogo_id = VALUES(item_catalogo_id),
            contexto_id = VALUES(contexto_id),
            class_id = VALUES(class_id),
            instance_id = VALUES(instance_id),
            indice_definicao = VALUES(indice_definicao),
            indice_pintura = VALUES(indice_pintura),
            semente_pintura = VALUES(semente_pintura),
            valor_float = VALUES(valor_float),
            nome_personalizado = VALUES(nome_personalizado),
            link_inspecao = VALUES(link_inspecao),
            stattrak = VALUES(stattrak),
            contador_stattrak = VALUES(contador_stattrak),
            souvenir = VALUES(souvenir),
            trocavel = VALUES(trocavel),
            comercializavel = VALUES(comercializavel),
            bloqueado_ate = VALUES(bloqueado_ate),
            quantidade = VALUES(quantidade),
            ultima_visualizacao_em = UTC_TIMESTAMP(),
            removido_em = NULL,
            ativo = 1,
            fonte_dados = VALUES(fonte_dados),
            metadados_origem = VALUES(metadados_origem)
        """
    )

    parametros = {
        "usuario_id": usuario_id,
        "item_catalogo_id": item_catalogo_id,
        "app_id": item.app_id,
        "contexto_id": item.contexto_id,
        "asset_id": item.asset_id,
        "class_id": item.class_id,
        "instance_id": item.instance_id,
        "indice_definicao": item.indice_definicao,
        "indice_pintura": item.indice_pintura,
        "semente_pintura": item.semente_pintura,
        "valor_float": item.valor_float,
        "nome_personalizado": item.nome_personalizado,
        "link_inspecao": item.link_inspecao,
        "stattrak": int(item.stattrak),
        "contador_stattrak": item.contador_stattrak,
        "souvenir": int(item.souvenir),
        "trocavel": int(item.trocavel),
        "comercializavel": int(item.comercializavel),
        "bloqueado_ate": item.bloqueado_ate,
        "quantidade": item.quantidade,
        "fonte_dados": item.fonte_dados,
        "metadados_origem": json.dumps(
            item.metadados_origem,
            ensure_ascii=False,
        ),
    }

    resultado = conexao.execute(
        consulta,
        parametros,
    )

    instancia_id = resultado.lastrowid

    if instancia_id is None:
        raise RuntimeError(
            "O banco não retornou o ID da instância."
        )

    return int(instancia_id)

def contar_instancias_ativas_usuario(
    conexao: Connection,
    usuario_id: int,
) -> int:
    """Conta os itens ativos do inventário de um usuário."""

    consulta = text(
        """
        SELECT COUNT(*) AS total
        FROM instancias_itens
        WHERE usuario_id = :usuario_id
          AND ativo = 1
        """
    )

    total = conexao.execute(
        consulta,
        {"usuario_id": usuario_id},
    ).scalar_one()

    return int(total)