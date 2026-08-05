# Configurações da aplicação Flask, incluindo a chave secreta e o banco de dados

import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configurações base do Skinexa."""

    SECRET_KEY = os.getenv("SECRET_KEY")

    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    STEAM_OPENID_URL = os.getenv("STEAM_OPENID_URL")
    STEAM_OPENID_REALM = os.getenv("STEAM_OPENID_REALM")
    STEAM_OPENID_RETURN_URL = os.getenv("STEAM_OPENID_RETURN_URL")

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)


class DevelopmentConfig(Config):
    """Configurações básicas para  o ambiente de desenvolvimento."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Configurações básicas para o ambiente de produção."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Configurações básicas para o ambiente de testes."""
    TESTING = True
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
    
    SESSION_PROTECTION = None
    
    SERVER_NAME = "localhost"

    STEAM_OPENID_URL = (
        "https://steamcommunity.com/openid/login"
    )

    STEAM_OPENID_REALM = "http://localhost/"

    STEAM_OPENID_RETURN_URL = (
        "http://localhost/auth/steam/retorno"
    )