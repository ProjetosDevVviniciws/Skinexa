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
    buscar_inventario_publico,
)

from skinexa.integrations.steam.normalizador_inventario import (
    normalizar_inventario_steam,
)

from skinexa.database.queries.leitura_inventario import (
    contar_itens_inventario,
    listar_itens_inventario,
    listar_tipos_itens_inventario,
    listar_raridades_itens_inventario,
    listar_estados_exteriores_inventario,
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
        tipo_item: str | None = None,
        raridade: str | None = None,
        estado_exterior: str | None = None,
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
        
        tipo_item_normalizado = (
            tipo_item.strip()
            if tipo_item is not None
            else None
        )

        if not tipo_item_normalizado:
            tipo_item_normalizado = None
        
        raridade_normalizada = (
            raridade.strip()
            if raridade is not None
            else None
        )

        if not raridade_normalizada:
            raridade_normalizada = None
        
        estado_exterior_normalizado = (
            estado_exterior.strip()
            if estado_exterior is not None
            else None
        )

        if not estado_exterior_normalizado:
            estado_exterior_normalizado = None
        
        deslocamento = (
            pagina - 1
        ) * itens_por_pagina

        registros = listar_itens_inventario(
            usuario_id,
            limite=itens_por_pagina,
            deslocamento=deslocamento,
            busca=busca_normalizada,
            tipo_item=tipo_item_normalizado,
            raridade=raridade_normalizada,
            estado_exterior=estado_exterior_normalizado,
        )

        itens = [
            ItemInventarioDTO.criar_de_registro(
                registro
            )
            for registro in registros
        ]

        total = contar_itens_inventario(
            usuario_id,
            busca=busca_normalizada,
            tipo_item=tipo_item_normalizado,
            raridade=raridade_normalizada,
            estado_exterior=estado_exterior_normalizado,
        )

        return itens, total
    
    @staticmethod
    def listar_tipos_inventario(
        *,
        usuario_id: int,
    ) -> list[str]:
        """Retorna os tipos distintos de itens ativos do inventário."""

        return listar_tipos_itens_inventario(
            usuario_id
        )
        
    @staticmethod
    def listar_raridades_inventario(
        *,
        usuario_id: int,
    ) -> list[str]:
        """Retorna as raridades distintas dos itens ativos."""

        return listar_raridades_itens_inventario(
            usuario_id
        )
        
    @staticmethod
    def listar_estados_inventario(
        *,
        usuario_id: int,
    ) -> list[str]:
        """Retorna os estados exteriores distintos dos itens ativos."""

        return listar_estados_exteriores_inventario(
            usuario_id
        )