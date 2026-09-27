"""Invoice totals sent to the payment processor."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

_CENT = Decimal("0.01")


@dataclass
class LineItem:
    sku: str
    unit_price: float  # dollars
    quantity: int
    tax_rate: float = 0.0


def line_total(item: LineItem) -> float:
    unit_price = Decimal(str(item.unit_price))
    tax_rate = Decimal(str(item.tax_rate))
    subtotal = unit_price * item.quantity
    total = subtotal * (1 + tax_rate)
    return float(total.quantize(_CENT, rounding=ROUND_HALF_UP))


def invoice_total(items: list[LineItem]) -> float:
    total = 0.0
    for item in items:
        total += line_total(item)
    return total


def invoice_total_cents(items: list[LineItem]) -> int:
    total = sum(
        Decimal(str(item.unit_price)) * item.quantity
        * (1 + Decimal(str(item.tax_rate)))
        for item in items
    )
    return int(total.quantize(_CENT, rounding=ROUND_HALF_UP) * 100)
