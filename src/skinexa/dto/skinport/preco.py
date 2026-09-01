from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass(frozen=True, slots=True)
class PrecoSkinportDTO:
    """Representa os dados de preço recebidos da Skinport."""

    market_hash_name: str
    currency: str

    min_price: Decimal | None
    max_price: Decimal | None
    mean_price: Decimal | None
    median_price: Decimal | None

    quantity: int | None

    updated_at: datetime | None