from dataclasses import dataclass

from sqlalchemy import Connection

from skinexa.database.connection import engine
from skinexa.database.queries.inventario import (
    contar_instancias_ativas_usuario,
    desativar_instancias_usuario,
    salvar_instancia_item
)

from skinexa.database.queries.itens_catalogo import (
    salvar_item_catalogo
)

from skinexa.integrations.steam.inventario import (
    buscar_inventario_publico
)

from skinexa.integrations.steam.normalizador_inventario import (
    normalizar_inventario_steam,
)

from skinexa.database.queries.leitura_inventario import (
    contar_itens_inventario,
    listar_itens_inventario,
)

from skinexa.dto.steam.inventario import ItemInventarioDTO

from datetime import UTC, datetime

from flask import current_app

from skinexa.database.queries.usuarios import (
    atualizar_ultima_sincronizacao_inventario,
    buscar_ultima_sincronizacao_inventario,
)

from skinexa.exceptions.inventario import (
    CooldownSincronizacaoAtivo,
)

@dataclass(frozen=True, slots=True)
class ResultadoSincronizacaoInventario:
    usuario_id: int
    total_informado_steam: int | None
    itens_processados: int
    itens_ativos: int

class InventarioService:
    """Coordena consulta, normalização e persistência do inventário."""

    @staticmethod
    def validar_cooldown_sincronizacao(
        *,
        conexao: Connection,
        usuario_id: int,
    ) -> None:
        """Verifica se o usuário já pode sincronizar novamente."""

        ultima_sincronizacao = (
            buscar_ultima_sincronizacao_inventario(
                conexao,
                usuario_id
            )
        )

        if ultima_sincronizacao is None:
            return

        cooldown_segundos = int(
            current_app.config[
                "INVENTARIO_COOLDOWN_SEGUNDOS"
            ]
        )

        agora_utc = datetime.now(
            UTC
        ).replace(tzinfo=None)

        segundos_decorridos = int(
            (
                agora_utc
                - ultima_sincronizacao
            ).total_seconds()
        )

        segundos_restantes = (
            cooldown_segundos
            - segundos_decorridos
        )

        if segundos_restantes > 0:
            raise CooldownSincronizacaoAtivo(
                segundos_restantes
            )
    
    @staticmethod
    def sincronizar_inventario(
        *,
        usuario_id: int,
        steam_id: str,
    ) -> ResultadoSincronizacaoInventario:
        """
        Sincroniza o inventário público do usuário com o MySQL.

        Toda a persistência ocorre em uma única transação.
        """

        with engine.connect() as conexao:
        
            InventarioService.validar_cooldown_sincronizacao(
                conexao=conexao,
                usuario_id=usuario_id
            )
        
        inventario_bruto = buscar_inventario_publico(
            steam_id
        )

        itens = normalizar_inventario_steam(
            inventario_bruto
        )

        with engine.begin() as conexao:
            # Tudo começa inativo. Cada item encontrado nesta
            # sincronização será reativado pelo upsert abaixo.
            desativar_instancias_usuario(
                conexao,
                usuario_id,
            )

            for item in itens:
                if (
                    item.instancia.steam_id_usuario
                    != steam_id
                ):
                    raise ValueError(
                        "A instância não pertence ao SteamID "
                        "informado para a sincronização."
                    )

                item_catalogo_id = salvar_item_catalogo(
                    conexao,
                    item.catalogo,
                )

                salvar_instancia_item(
                    conexao,
                    usuario_id=usuario_id,
                    item_catalogo_id=item_catalogo_id,
                    item=item.instancia,
                )

            total_ativos = (
                contar_instancias_ativas_usuario(
                    conexao,
                    usuario_id,
                )
            )

            sincronizacao_registrada = (
                atualizar_ultima_sincronizacao_inventario(
                    conexao,
                    usuario_id,
                )
            )

            if not sincronizacao_registrada:
                raise RuntimeError(
                    "Não foi possível registrar a última "
                    "sincronização do inventário."
                )
    
        return ResultadoSincronizacaoInventario(
            usuario_id=usuario_id,
            total_informado_steam=(
                inventario_bruto.total_informado
            ),
            itens_processados=len(itens),
            itens_ativos=total_ativos,
        )
        
    @staticmethod
    def listar_inventario(
        *,
        usuario_id: int,
        pagina: int = 1,
        itens_por_pagina: int = 20,
        busca: str | None = None,
    ) -> tuple[list[ItemInventarioDTO], int]:
        """Retorna os itens do inventário e sua quantidade total."""

        if pagina < 1:
            pagina = 1

        if itens_por_pagina < 1:
            itens_por_pagina = 20

        busca_normalizada = (
            busca.strip()
            if busca is not None
            else None
        )
        
        if not busca_normalizada:
            busca_normalizada = None
        
        deslocamento = (
            pagina - 1
        ) * itens_por_pagina

        registros = listar_itens_inventario(
            usuario_id,
            limite=itens_por_pagina,
            deslocamento=deslocamento,
            busca=busca_normalizada,
        )

        itens = [
            ItemInventarioDTO.criar_de_registro(
                registro
            )
            for registro in registros
        ]

        total = contar_itens_inventario(
            usuario_id,
            busca=busca_normalizada
        )

        return itens, total