from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    abort,
)

from skinexa.blueprints.mercado.serializers import (
    serializar_pagina_mercado,
    serializar_preco_comparacao,
    serializar_sugestao_mercado,
)

from skinexa.database.connection import engine

from skinexa.services.catalogo.pesquisa import (
    LIMITE_MAXIMO_ITENS_POR_PAGINA,
    autocomplete_itens,
    listar_itens_paginados,
    pesquisar_itens_paginados,
)

from skinexa.services.precos.consulta import (
    consultar_comparacao_precos,
)

from skinexa.database.queries.itens_catalogo import (
    ORDENACOES_CATALOGO,
)

from skinexa.services.catalogo.service import obter_item

mercado_bp = Blueprint(
    "mercado",
    __name__,
    url_prefix="/mercado",
)

@mercado_bp.get("/")
def index():
    """Renderiza a página principal do mercado."""
    
    pagina = request.args.get(
        "pagina",
        default=1,
        type=int,
    )

    por_pagina = request.args.get(
        "por_pagina",
        default=20,
        type=int,
    )

    ordenacao = request.args.get(
        "ordenacao",
        default="nome_asc",
        type=str,
    )

    termo = request.args.get(
        "q",
        default="",
        type=str,
    ).strip()
    
    if (
            pagina < 1
            or por_pagina < 1
            or por_pagina > LIMITE_MAXIMO_ITENS_POR_PAGINA
            or ordenacao not in ORDENACOES_CATALOGO
            or len(termo) > 100
        ):
            abort(400) 
    
    with engine.connect() as conexao:
        if termo:
            resultado = pesquisar_itens_paginados(
                conexao,
                termo=termo,
                pagina=pagina,
                por_pagina=por_pagina,
                ordenacao=ordenacao,
            )
        else:
            resultado = listar_itens_paginados(
                conexao,
                pagina=pagina,
                por_pagina=por_pagina,
                ordenacao=ordenacao,
            )

    return render_template(
        "mercado/index.html",
        resultado=resultado,
        ordenacao=ordenacao,
        termo=termo,
    )

@mercado_bp.get("/itens")
def listar_itens_json():
    """Retorna itens paginados do Mercado em formato JSON."""

    pagina = request.args.get(
        "pagina",
        default=1,
        type=int,
    )

    por_pagina = request.args.get(
        "por_pagina",
        default=20,
        type=int,
    )

    ordenacao = request.args.get(
        "ordenacao",
        default="nome_asc",
        type=str,
    )

    termo = request.args.get(
        "q",
        default="",
        type=str,
    ).strip()    
    
    if (
        pagina < 1
        or por_pagina < 1
        or por_pagina > LIMITE_MAXIMO_ITENS_POR_PAGINA
        or ordenacao not in ORDENACOES_CATALOGO
        or len(termo) > 100
    ):
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "Parâmetros de paginação ou "
                    "ordenação inválidos."
                ),
            }
        ), 400
    
    with engine.connect() as conexao:
        if termo:
            resultado = pesquisar_itens_paginados(
                conexao,
                termo=termo,
                pagina=pagina,
                por_pagina=por_pagina,
                ordenacao=ordenacao,
            )
        else:
            resultado = listar_itens_paginados(
                conexao,
                pagina=pagina,
                por_pagina=por_pagina,
                ordenacao=ordenacao,
            )

    return jsonify(
        serializar_pagina_mercado(
            resultado,
            ordenacao=ordenacao,
        )
    )

@mercado_bp.get("/sugestoes")
def sugestoes_itens_json():
    """Retorna sugestões de itens para o autocomplete."""

    termo = request.args.get(
        "q",
        default="",
        type=str,
    ).strip()

    if len(termo) > 100:
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "O termo de pesquisa deve ter "
                    "no máximo 100 caracteres."
                ),
            }
        ), 400

    if len(termo) < 2:
        return jsonify(
            {
                "sugestoes": [],
            }
        )

    with engine.connect() as conexao:
        sugestoes = autocomplete_itens(
            conexao,
            termo=termo,
            limite=8,
        )

    return jsonify(
        {
            "sugestoes": [
                serializar_sugestao_mercado(sugestao)
                for sugestao in sugestoes
            ],
        }
    )

@mercado_bp.get("/item/<int:item_catalogo_id>")
def item(item_catalogo_id: int):
    """Renderiza a página individual de um item do catálogo."""

    with engine.connect() as conexao:
        item_catalogo = obter_item(
            conexao,
            item_catalogo_id,
        )

    if item_catalogo is None:
        abort(404)

    return render_template(
        "mercado/item.html",
        item=item_catalogo,
    )
    
@mercado_bp.get("/item/<int:item_catalogo_id>/precos")
def precos_item(
    item_catalogo_id: int,
):
    """Retorna os preços mais recentes do item por marketplace."""

    precos = consultar_comparacao_precos(
        item_catalogo_id=item_catalogo_id,
    )

    return jsonify(
        {
            "item_catalogo_id": item_catalogo_id,
            "mercados": [
                serializar_preco_comparacao(preco)
                for preco in precos
            ],
        }
    )