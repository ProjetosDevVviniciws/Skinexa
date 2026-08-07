from dataclasses import dataclass

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

@dataclass(frozen=True, slots=True)
class ResultadoSincronizacaoInventario:
    usuario_id: int
    total_informado_steam: int | None
    itens_processados: int
    itens_ativos: int

class InventarioService:
    """Coordena consulta, normalização e persistência do inventário."""

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

        return ResultadoSincronizacaoInventario(
            usuario_id=usuario_id,
            total_informado_steam=(
                inventario_bruto.total_informado
            ),
            itens_processados=len(itens),
            itens_ativos=total_ativos,
        )