"""Invoice totals sent to the payment processor."""
from dataclasses import dataclass


@dataclass
class LineItem:
    sku: str
    unit_price: float  # dollars
    quantity: int
    tax_rate: float = 0.0


def line_total(item: LineItem) -> float:
    subtotal = item.unit_price * item.quantity
    return round(subtotal * (1 + item.tax_rate), 2)


def invoice_total(items: list[LineItem]) -> float:
    total = 0.0
    for item in items:
        total += line_total(item)
    return total


def invoice_total_cents(items: list[LineItem]) -> int:
    return int(invoice_total(items) * 100)
