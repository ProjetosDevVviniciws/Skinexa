from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class PrecoMercado:
    """Representa um preço normalizado dentro do Skinexa."""

    nome_mercado: str
    plataforma: str
    moeda: str

    menor_preco: Decimal | None
    maior_preco: Decimal | None
    preco_medio: Decimal | None
    preco_mediano: Decimal | None

    maior_ordem_compra: Decimal | None

    quantidade_anuncios: int | None
    volume_vendas: int | None

    atualizado_na_origem_em: datetime | None