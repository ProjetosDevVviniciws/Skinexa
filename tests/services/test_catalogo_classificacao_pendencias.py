import pytest

from skinexa.services.catalogo.classificacao_pendencias import (
    MOTIVO_NAO_COMERCIALIZAVEL,
    MOTIVO_SEM_IDENTIDADE,
    classificar_pendencia_catalogo,
)

@pytest.mark.parametrize(
    "registro,motivo_esperado",
    [
        (
            {
                "market_hash_name": None,
                "marketable": False,
            },
            MOTIVO_NAO_COMERCIALIZAVEL,
        ),
        (
            {
                "market_hash_name": None,
                "marketable": True,
            },
            MOTIVO_SEM_IDENTIDADE,
        ),
        (
            {
                "market_hash_name": None,
            },
            MOTIVO_SEM_IDENTIDADE,
        ),
        (
            {
                "market_hash_name": None,
                "exclusive": True,
            },
            MOTIVO_SEM_IDENTIDADE,
        ),
        (
            {
                "market_hash_name": None,
                "genuine": True,
            },
            MOTIVO_SEM_IDENTIDADE,
        ),
    ],
)

def test_classificar_pendencia_catalogo(
    registro,
    motivo_esperado,
):
    """Classifica apenas restrições explícitas da origem."""

    assert (
        classificar_pendencia_catalogo(registro)
        == motivo_esperado
    )