# Centraliza a criação e inicialização das extensões do Flask

from flask_login import LoginManager # Gerencia a autenticação de usuários
from flask_wtf import CSRFProtect # Protege contra ataques CSRF (Cross-Site Request Forgery)

login_manager = LoginManager()

csrf = CSRFProtect()