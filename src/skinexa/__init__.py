# Cria e configura a aplicação Flask e registra seus Blueprints

import mimetypes
from flask import Flask
from skinexa.core.config import DevelopmentConfig
from skinexa.core.extensions import login_manager, csrf
from skinexa.blueprints.home.routes import home_bp
from skinexa.blueprints.auth.routes import auth_bp
from skinexa.blueprints.dashboard.routes import dashboard_bp
from skinexa.core.errors import registrar_tratadores_erros

mimetypes.add_type(
    "text/javascript",
    ".js",
)

def create_app(
    config_class: type = DevelopmentConfig,
) -> Flask:
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    
    _configurar_app(app, config_class)
    _inicializar_extensoes(app)
    _configurar_autenticacao()
    _registrar_blueprints(app)
    
    registrar_tratadores_erros(app)
    
    return app

def _configurar_app(
    app: Flask,
    config_class: type,
) -> None:
    """Carrega as configurações selecionadasda aplicação."""

    app.config.from_object(config_class)
    
def _inicializar_extensoes(app: Flask) -> None:
    """Inicializa as extensões."""

    login_manager.init_app(app)
    csrf.init_app(app)
    
def _registrar_blueprints(app: Flask) -> None:
    """Registra todos os Blueprints."""

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    
def _configurar_autenticacao() -> None:
    """Configura toda a autenticação da aplicação."""
    from skinexa.core import autenticacao  

    # Import necessário para registrar o callback
    # @login_manager.user_loader.
    login_manager.login_view = "auth.login"
    
    login_manager.login_message = (
        "Entre com sua conta Steam para acessar esta página."
    )
    
    login_manager.login_message_category = "warning"
    
    login_manager.session_protection = "strong"
    
