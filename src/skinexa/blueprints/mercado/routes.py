from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
)

from skinexa.blueprints.mercado.serializers import (
    serializar_preco_comparacao,
)

from skinexa.database.connection import engine

from skinexa.services.catalogo.pesquisa import (
    listar_itens_paginados,
)

from skinexa.services.precos.consulta import (
    consultar_comparacao_precos,
)

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

    with engine.connect() as conexao:
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
    )

@mercado_bp.get("/item/<int:item_catalogo_id>")
def item(item_catalogo_id: int):
    """Renderiza a página individual de um item."""

    return render_template(
        "mercado/item.html",
        item_catalogo_id=item_catalogo_id,
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