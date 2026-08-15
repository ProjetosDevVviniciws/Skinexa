from typing import Any

from sqlalchemy import text

from skinexa.database.connection import engine

from sqlalchemy.engine import Connection

from datetime import datetime

def buscar_usuario_por_steam_id(
    steam_id: str,
) -> dict[str, Any] | None:
    """Busca um usuário pelo identificador da Steam."""

    consulta = text(
        """
        SELECT
            id,
            steam_id,
            nome_exibicao,
            url_avatar,
            url_perfil,
            status_conta,
            criado_em,
            atualizado_em,
            ultimo_login_em
        FROM usuarios
        WHERE steam_id = :steam_id
        LIMIT 1
        """
    )

    with engine.connect() as conexao:
        resultado = conexao.execute(
            consulta,
            {"steam_id": steam_id},
        ).mappings().first()

    return dict(resultado) if resultado else None

def buscar_usuario_por_id(
    usuario_id: int,
) -> dict[str, Any] | None:
    """Busca um usuário pelo ID interno do Skinexa."""

    consulta = text(
        """
        SELECT
            id,
            steam_id,
            nome_exibicao,
            url_avatar,
            url_perfil,
            status_conta,
            criado_em,
            atualizado_em,
            ultimo_login_em
        FROM usuarios
        WHERE id = :usuario_id
        LIMIT 1
        """
    )

    with engine.connect() as conexao:
        resultado = conexao.execute(
            consulta,
            {"usuario_id": usuario_id},
        ).mappings().first()

    return dict(resultado) if resultado else None

def criar_usuario(
    steam_id: str,
    nome_exibicao: str,
    url_avatar: str | None = None,
    url_perfil: str | None = None,
) -> int:
    """Cria um usuário e retorna seu ID."""

    consulta = text(
        """
        INSERT INTO usuarios (
            steam_id,
            nome_exibicao,
            url_avatar,
            url_perfil,
            ultimo_login_em
        )
        VALUES (
            :steam_id,
            :nome_exibicao,
            :url_avatar,
            :url_perfil,
            UTC_TIMESTAMP()
        )
        """
    )

    parametros = {
        "steam_id": steam_id,
        "nome_exibicao": nome_exibicao,
        "url_avatar": url_avatar,
        "url_perfil": url_perfil,
    }

    with engine.begin() as conexao:
        resultado = conexao.execute(
            consulta,
            parametros,
        )

        usuario_id = resultado.lastrowid

        conexao.execute(
            text(
                """
                INSERT INTO configuracoes_usuario (
                    usuario_id
                )
                VALUES (
                    :usuario_id
                )
                """
            ),
            {"usuario_id": usuario_id},
        )

    if usuario_id is None:
        raise RuntimeError(
            "O banco não retornou o ID do usuário criado."
        )

    return int(usuario_id)

def atualizar_usuario_steam(
    steam_id: str,
    nome_exibicao: str,
    url_avatar: str | None,
    url_perfil: str | None,
) -> bool:
    """Atualiza informações públicas obtidas da Steam."""

    consulta = text(
        """
        UPDATE usuarios
        SET
            nome_exibicao = :nome_exibicao,
            url_avatar = :url_avatar,
            url_perfil = :url_perfil,
            ultimo_login_em = UTC_TIMESTAMP()
        WHERE steam_id = :steam_id
        """
    )

    parametros = {
        "steam_id": steam_id,
        "nome_exibicao": nome_exibicao,
        "url_avatar": url_avatar,
        "url_perfil": url_perfil,
    }

    with engine.begin() as conexao:
        resultado = conexao.execute(
            consulta,
            parametros,
        )

    return resultado.rowcount > 0

def salvar_usuario_steam(
    steam_id: str,
    nome_exibicao: str,
    url_avatar: str | None = None,
    url_perfil: str | None = None,
) -> dict[str, Any]:
    """Cria ou atualiza um usuário autenticado pela Steam."""

    usuario = buscar_usuario_por_steam_id(steam_id)

    if usuario is None:
        criar_usuario(
            steam_id=steam_id,
            nome_exibicao=nome_exibicao,
            url_avatar=url_avatar,
            url_perfil=url_perfil,
        )
    else:
        atualizar_usuario_steam(
            steam_id=steam_id,
            nome_exibicao=nome_exibicao,
            url_avatar=url_avatar,
            url_perfil=url_perfil,
        )

    usuario_atualizado = buscar_usuario_por_steam_id(
        steam_id
    )

    if usuario_atualizado is None:
        raise RuntimeError(
            "Não foi possível recuperar o usuário salvo."
        )

    return usuario_atualizado

def buscar_ultima_sincronizacao_inventario(
    conexao: Connection,
    usuario_id: int
) -> datetime | None:
    """Retorna a última sincronização bem-sucedida do inventário."""

    consulta = text(
        """
        SELECT
            ultima_sincronizacao_inventario_em
        FROM usuarios
        WHERE id = :usuario_id
        LIMIT 1
        """
    )

    resultado = conexao.execute(
        consulta,
        {"usuario_id": usuario_id},
    ).scalar_one_or_none()

    return resultado

def atualizar_ultima_sincronizacao_inventario(
    conexao: Connection,
    usuario_id: int,
) -> bool:
    """Registra uma sincronização de inventário bem-sucedida."""

    consulta = text(
        """
        UPDATE usuarios
        SET
            ultima_sincronizacao_inventario_em = UTC_TIMESTAMP()
        WHERE id = :usuario_id
        """
    )

    resultado = conexao.execute(
        consulta,
        {"usuario_id": usuario_id},
    )

    return resultado.rowcount > 0