class CooldownSincronizacaoAtivo(Exception):
    """Indica que o usuário tentou sincronizar antes do intervalo permitido."""

    def __init__(
        self,
        segundos_restantes: int,
    ) -> None:
        self.segundos_restantes = segundos_restantes

        super().__init__(
            "A sincronização do inventário ainda está em cooldown."
        )