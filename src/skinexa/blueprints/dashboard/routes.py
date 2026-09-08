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

from skinexa.utils.conversores import (
    converter_booleano_query,
)

from skinexa.utils.normalizadores import (
    normalizar_ordenacao_inventario,
)

from skinexa.services.precos.consulta import (
    consultar_ultimos_precos,
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
    
    tipo_item = request.args.get(
        "tipo",
        default=None,
        type=str,
    )
    
    raridade = request.args.get(
        "raridade",
        default=None,
        type=str,
    )
    
    estado_exterior = request.args.get(
        "estado",
        default=None,
        type=str,
    )
    
    stattrak = converter_booleano_query(
        request.args.get("stattrak")
    )

    souvenir = converter_booleano_query(
        request.args.get("souvenir")
    )
    
    ordenacao = normalizar_ordenacao_inventario (
        request.args.get("ordenacao")
    )
        
    itens_por_pagina = 20

    itens, total_itens = (
        InventarioService.listar_inventario(
            usuario_id=current_user.id,
            pagina=pagina,
            itens_por_pagina=itens_por_pagina,
            busca=busca,
            tipo_item=tipo_item,
            raridade=raridade,
            estado_exterior=estado_exterior,
            stattrak=stattrak,
            souvenir=souvenir,
            ordenacao=ordenacao,
        )
    )

    item_catalogo_ids = {
        item.item_catalogo_id
        for item in itens
    }

    precos = consultar_ultimos_precos(
        item_catalogo_ids=item_catalogo_ids,
        plataforma="skinport",
    )
    
    dados = []

    for item in itens:
        preco = precos.get(
            item.item_catalogo_id
        )

        dados.append(
            {
                "instancia_id": item.instancia_id,
                "item_catalogo_id": (
                    item.item_catalogo_id
                ),
                "nome_mercado": item.nome_mercado,
                "nome_exibicao": item.nome_exibicao,
                "tipo_item": item.tipo_item,
                "raridade": item.raridade,
                "estado_exterior": (
                    item.estado_exterior
                ),
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
                "preco": (
                    {
                        "plataforma": (
                            preco.plataforma
                        ),
                        "moeda": preco.moeda,
                        "menor_preco": (
                            str(preco.menor_preco)
                            if preco.menor_preco
                            is not None
                            else None
                        ),
                        "maior_preco": (
                            str(preco.maior_preco)
                            if preco.maior_preco
                            is not None
                            else None
                        ),
                        "preco_medio": (
                            str(preco.preco_medio)
                            if preco.preco_medio
                            is not None
                            else None
                        ),
                        "preco_mediano": (
                            str(preco.preco_mediano)
                            if preco.preco_mediano
                            is not None
                            else None
                        ),
                        "quantidade_anuncios": (
                            preco.quantidade_anuncios
                        ),
                        "coletado_em": (
                            preco.coletado_em.isoformat()
                        ),
                        "atualizado_na_origem_em": (
                            preco
                            .atualizado_na_origem_em
                            .isoformat()
                            if (
                                preco
                                .atualizado_na_origem_em
                                is not None
                            )
                            else None
                        ),
                    }
                    if preco is not None
                    else None
                ),
            }
        )

    return jsonify(
        {
            "itens": dados,
            "total_itens": total_itens,
            "pagina": pagina,
            "itens_por_pagina": itens_por_pagina,
            "busca": busca or "",
            "tipo": tipo_item or "",
            "raridade": raridade or "",
            "estado": estado_exterior or "",
            "stattrak": stattrak,
            "souvenir": souvenir,
            "ordenacao": ordenacao,
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
        
@dashboard_bp.get("/inventario/tipos")
@login_required
def obter_tipos_inventario():
    """Retorna os tipos distintos de itens ativos do inventário."""

    tipos = InventarioService.listar_tipos_inventario(
        usuario_id=current_user.id,
    )

    return jsonify(
        {
            "tipos": tipos,
        }
    )
    
@dashboard_bp.get("/inventario/raridades")
@login_required
def obter_raridades_inventario():
    """Retorna as raridades distintas dos itens ativos."""

    raridades = (
        InventarioService.listar_raridades_inventario(
            usuario_id=current_user.id,
        )
    )

    return jsonify(
        {
            "raridades": raridades,
        }
    )
    
@dashboard_bp.get("/inventario/estados")
@login_required
def obter_estados_inventario():
    """Retorna os estados exteriores distintos dos itens ativos."""

    estados = (
        InventarioService.listar_estados_inventario(
            usuario_id=current_user.id,
        )
    )

    return jsonify(
        {
            "estados": estados,
        }
    )