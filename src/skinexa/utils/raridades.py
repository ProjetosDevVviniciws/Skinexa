CORES_RARIDADES = {
    "consumer grade": "#B0C3D9",
    "industrial grade": "#5E98D9",
    "mil-spec grade": "#4B69FF",
    "high grade": "#4B69FF",
    "restricted": "#8847FF",
    "remarkable": "#8847FF",
    "classified": "#D32CE6",
    "exotic": "#D32CE6",
    "covert": "#EB4B4B",
    "extraordinary": "#E4AE39",
    "contraband": "#E4AE39",
    "base grade": "#B0C3D9",
    "distinguished": "#4B69FF",
    "exceptional": "#8847FF",
    "superior": "#D32CE6",
    "master": "#EB4B4B",
}

def obter_cor_raridade(raridade: str | None) -> str | None:
    """Obtém a cor conhecida de uma raridade, sem inferir valores."""

    if not isinstance(raridade, str):
        return None

    return CORES_RARIDADES.get(
        raridade.strip().casefold()
    )