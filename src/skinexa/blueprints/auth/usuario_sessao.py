from dataclasses import dataclass
from datetime import datetime

from flask_login import UserMixin

@dataclass(slots=True)
class UsuarioSessao(UserMixin):
    """Representa o usuário autenticado durante a sessão Flask."""

    id: int
    steam_id: str
    nome_exibicao: str
    url_avatar: str | None
    url_perfil: str | None
    status_conta: str
    criado_em: datetime
    atualizado_em: datetime
    ultimo_login_em: datetime | None

    def get_id(self) -> str:
        """Retorna o identificador salvo pelo Flask-Login na sessão."""

        return str(self.id)

    @property
    def is_active(self) -> bool:
        """Indica se a conta local está autorizada a usar a aplicação."""

        return self.status_conta == "ativa"

    @classmethod
    def criar_de_registro(
        cls,
        registro: dict,
    ) -> "UsuarioSessao":
        """Converte um registro do banco em objeto de sessão."""

        return cls(
            id=int(registro["id"]),
            steam_id=registro["steam_id"],
            nome_exibicao=registro["nome_exibicao"],
            url_avatar=registro["url_avatar"],
            url_perfil=registro["url_perfil"],
            status_conta=registro["status_conta"],
            criado_em=registro["criado_em"],
            atualizado_em=registro["atualizado_em"],
            ultimo_login_em=registro["ultimo_login_em"],
        )