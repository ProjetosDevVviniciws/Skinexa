from flask import render_template, Blueprint
from flask_login import login_required

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard",
)

@dashboard_bp.get("/")
@login_required
def index():
    """Exibe o painel principal do usuário autenticado."""

    return render_template("dashboard/index.html")