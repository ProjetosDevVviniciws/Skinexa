from flask import Blueprint, render_template

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
def item(item_catalogo_id: int,):
    """Renderiza a página individual de um item."""

    return render_template(
        "mercado/item.html",
        item_catalogo_id=item_catalogo_id,
    )