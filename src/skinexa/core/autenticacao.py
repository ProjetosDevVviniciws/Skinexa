from skinexa.core.extensions import login_manager
from skinexa.services.usuarios import UsuarioService

@login_manager.user_loader
def carregar_usuario(
    usuario_id: str,
):
    """Reconstrói o usuário autenticado a cada nova requisição."""

    try:
        id_convertido = int(usuario_id)
    except (TypeError, ValueError):
        return None

    return UsuarioService.obter_usuario_sessao(
        id_convertido
    )