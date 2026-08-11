from flask import (Flask,current_app,jsonify,render_template,request)
from werkzeug.exceptions import HTTPException

def registrar_tratadores_erros(
    app: Flask,
) -> None:
    """Registra os tratadores globais de erros da aplicação."""

    app.register_error_handler(
        404,
        _tratar_nao_encontrado,
    )

    app.register_error_handler(
        405,
        _tratar_metodo_nao_permitido,
    )

    app.register_error_handler(
        Exception,
        _tratar_excecao_inesperada,
    )

def _tratar_nao_encontrado(
    erro: HTTPException,
):
    """Trata páginas ou recursos inexistentes."""

    if _espera_json():
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "O recurso solicitado não foi encontrado."
                ),
            }
        ), 404

    return render_template(
        "errors/404.html"
    ), 404

def _tratar_metodo_nao_permitido(
    erro: HTTPException,
):
    """Trata métodos HTTP não permitidos."""

    if _espera_json():
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "O método HTTP utilizado não é permitido "
                    "para este recurso."
                ),
            }
        ), 405

    return render_template(
        "errors/405.html"
    ), 405

def _tratar_excecao_inesperada(
    erro: Exception,
):
    """Trata exceções não previstas pela aplicação."""

    if isinstance(erro, HTTPException):
        return erro

    current_app.logger.exception(
        "Exceção inesperada não tratada.",
        exc_info=erro,
    )

    if _espera_json():
        return jsonify(
            {
                "sucesso": False,
                "mensagem": (
                    "Ocorreu um erro interno. "
                    "Tente novamente mais tarde."
                ),
            }
        ), 500

    return render_template(
        "errors/500.html"
    ), 500

def _espera_json() -> bool:
    """Verifica se o cliente prefere receber JSON."""

    melhor_resposta = request.accept_mimetypes.best_match(
        [
            "text/html",
            "application/json",
        ]
    )

    return melhor_resposta == "application/json"