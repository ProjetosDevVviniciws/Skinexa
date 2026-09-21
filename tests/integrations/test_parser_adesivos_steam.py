from skinexa.integrations.steam.parsers.adesivos import (
    ParserAdesivosSteam,
)

def test_parser_extrai_adesivos():
    """Testa a extração de adesivos do HTML da Steam."""

    html = """
    <div id="sticker_info">
        <center>
            <img
                width="64"
                height="48"
                src="https://cdn.steamstatic.com/getright.png"
                title="Adesivo: GeT_RiGhT | Colônia 2015"
            >
            <img
                width="64"
                height="48"
                src="https://cdn.steamstatic.com/nip.png"
                title="Adesivo: Ninjas in Pyjamas | Colônia 2015"
            >
        </center>
    </div>
    """

    parser = ParserAdesivosSteam()
    parser.feed(html)

    assert len(parser.adesivos) == 2

    primeiro = parser.adesivos[0]

    assert (
        primeiro.nome_exibicao
        == "GeT_RiGhT | Colônia 2015"
    )
    assert (
        primeiro.url_icone
        == "https://cdn.steamstatic.com/getright.png"
    )

    segundo = parser.adesivos[1]

    assert (
        segundo.nome_exibicao
        == "Ninjas in Pyjamas | Colônia 2015"
    )
    assert (
        segundo.url_icone
        == "https://cdn.steamstatic.com/nip.png"
    )
    
def test_parser_ignora_imagem_que_nao_e_adesivo():
    """Ignora imagens que não representam adesivos."""

    html = """
    <div>
        <img
            src="https://example.com/item.png"
            title="Imagem do item"
        >
    </div>
    """

    parser = ParserAdesivosSteam()
    parser.feed(html)

    assert parser.adesivos == []
    
def test_parser_aceita_adesivo_sem_url():
    """Permite adesivo quando a Steam não fornece imagem."""

    html = """
    <img title="Adesivo: Exemplo | 2026">
    """

    parser = ParserAdesivosSteam()
    parser.feed(html)

    assert len(parser.adesivos) == 1

    adesivo = parser.adesivos[0]

    assert (
        adesivo.nome_exibicao
        == "Exemplo | 2026"
    )
    assert adesivo.url_icone is None