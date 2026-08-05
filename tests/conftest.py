# Configuração de testes para a aplicação Skinexa.

import pytest

from skinexa import create_app
from skinexa.core.config import TestingConfig

@pytest.fixture()
def app():
    """Cria uma aplicação isolada para cada teste."""

    aplicacao = create_app(TestingConfig)

    yield aplicacao

@pytest.fixture()
def client(app):
    """Disponibiliza um cliente HTTP de testes."""

    return app.test_client()

@pytest.fixture()
def runner(app):
    """Disponibiliza o executor de comandos Flask."""

    return app.test_cli_runner()