from flask import Blueprint, render_template, jsonify

from skinexa.services.precos.consulta import consultar_comparacao_precos

from skinexa.blueprints.mercado.serializers import serializar_preco_comparacao 

mercado_bp = Blueprint(
    "mercado",
    __name__,
    url_prefix="/mercado",
)

@mercado_bp.get("/")
def index():
    """Renderiza a página principal do mercado."""

    return render_template(
        "mercado/index.html",
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