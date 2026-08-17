from flask import current_app, render_template, Blueprint, request, jsonify
from flask_login import login_required, current_user

from skinexa.integrations.steam.inventario import (
    ErroInventarioSteam,
    InventarioSteamIndisponivel,
    InventarioSteamPrivado,
    LimiteSteamExcedido,
    RespostaInventarioInvalida,
)

from skinexa.services.inventory.service import InventarioService

from skinexa.exceptions.inventario import (
    CooldownSincronizacaoAtivo,
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard",
)

@dashboard_bp.get("/")
@login_required
def index():
    """Exibe a estrutura principal do Dashboard."""

    return render_template(
        "dashboard/index.html"
    )

@dashboard_bp.get("/inventario")
@login_required
def obter_inventario():
    """Retorna os itens do inventário em formato JSON."""

    pagina = request.args.get(
        "pagina",
        default=1,
        type=int,
    )

    busca = request.args.get(
        "busca",
        default=None,
        type=str,
    )
        
    itens_por_pagina = 20

    itens, total_itens = (
        InventarioService.listar_inventario(
            usuario_id=current_user.id,
            pagina=pagina,
            itens_por_pagina=itens_por_pagina,
            busca=busca,
        )
    )

    dados = [
        {
            "instancia_id": item.instancia_id,
            "item_catalogo_id": item.item_catalogo_id,
            "nome_mercado": item.nome_mercado,
            "nome_exibicao": item.nome_exibicao,
            "tipo_item": item.tipo_item,
            "raridade": item.raridade,
            "estado_exterior": item.estado_exterior,
            "imagem": (
                item.url_icone_grande
                or item.url_icone
            ),
            "stattrak": item.stattrak,
            "souvenir": item.souvenir,
            "trocavel": item.trocavel,
            "comercializavel": (
                item.comercializavel
            ),
            "quantidade": item.quantidade,
        }
        for item in itens
    ]

    return jsonify(
        {
            "itens": dados,
            "total_itens": total_itens,
            "pagina": pagina,
            "itens_por_pagina": itens_por_pagina,
            "busca": busca or "",
            "tem_anterior": pagina > 1,
            "tem_proxima": (
                pagina * itens_por_pagina
                < total_itens
            ),
        }
    )

@dashboard_bp.post("/sincronizar-inventario")
@login_required
def sincronizar_inventario():
    """Sincroniza o inventário Steam do usuário autenticado."""

    try:
        resultado = InventarioService.sincronizar_inventario(
            usuario_id=current_user.id,
            steam_id=current_user.steam_id,
        )

        return jsonify(
            {
                "sucesso": True,
                "mensagem": (
                    "Inventário sincronizado com sucesso."
                ),
                "itens_ativos": resultado.itens_ativos,
                "itens_processados": (
                    resultado.itens_processados
                ),
            }
        ), 200

    except CooldownSincronizacaoAtivo as erro:
        return jsonify(
            {
                "sucesso": False,
                "codigo": "cooldown_sincronizacao",
                "mensagem": (
                    "Aguarde antes de sincronizar novamente."
                ),
                "segundos_restantes": (
                    erro.segundos_restantes
                ),
            }
        ), 429
    
    except InventarioSteamPrivado:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "Seu inventário da Steam está privado. "
                    "Torne-o público para realizar a sincronização."
                ),
            }
        ), 403

    except LimiteSteamExcedido:
        return jsonify(
            {
                "sucesso": False,
                "codigo": "limite_steam",
                "mensagem": (
                    "A Steam limitou temporariamente as consultas. "
                    "Tente novamente mais tarde."
                ),
            }
        ), 429

    except InventarioSteamIndisponivel:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "O inventário da Steam está "
                    "temporariamente indisponível."
                ),
            }
        ), 503

    except RespostaInventarioInvalida:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "A Steam retornou dados inesperados "
                    "durante a sincronização."
                ),
            }
        ), 502

    except ErroInventarioSteam:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "Não foi possível consultar seu inventário."
                ),
            }
        ), 502