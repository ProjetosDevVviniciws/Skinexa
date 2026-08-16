from skinexa.blueprints.auth.usuario_sessao import UsuarioSessao
from skinexa.database.queries.usuarios import (
    buscar_usuario_por_id,
    salvar_usuario_steam,
)

class UsuarioService:
    """Coordena operações relacionadas aos usuários do Skinexa."""

    @staticmethod
    def obter_usuario_sessao(
        usuario_id: int,
    ) -> UsuarioSessao | None:
        """Recupera um usuário e o converte para objeto de sessão."""

        registro = buscar_usuario_por_id(usuario_id)

        if registro is None:
            return None

        return UsuarioSessao.criar_de_registro(registro)

    @staticmethod
    def autenticar_usuario_steam(
        steam_id: str,
        nome_exibicao: str,
        url_avatar: str | None = None,
        url_perfil: str | None = None,
    ) -> UsuarioSessao:
        """Cria ou atualiza um usuário autenticado pela Steam."""

        registro = salvar_usuario_steam(
            steam_id=steam_id,
            nome_exibicao=nome_exibicao,
            url_avatar=url_avatar,
            url_perfil=url_perfil,
        )

        usuario = UsuarioSessao.criar_de_registro(registro)

        if not usuario.is_active:
            raise PermissionError(
                "A conta do usuário não está ativa."
            )

        return usuario