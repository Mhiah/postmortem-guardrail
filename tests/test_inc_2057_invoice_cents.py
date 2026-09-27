"""Regression tests for INC-2057.

Incident summary
----------------
1,870 invoices were off by exactly $0.01 because:

1. ``line_total()`` uses Python's built-in ``round(..., 2)`` which applies
   banker's rounding (round-half-to-even) instead of the finance-mandated
   round-half-UP per line item.
2. ``invoice_total_cents()`` converts the float dollar sum to cents via
   ``int(total * 100)``, which truncates instead of rounding.  Float
   arithmetic can produce e.g. 69.56999...9 from a true value of 69.57,
   so the truncation yields 6956 instead of the correct 6957.

Root cause: shopfront/billing.py lines 15 and 26.
"""
import pytest
from shopfront.billing import LineItem, invoice_total_cents, line_total


# ---------------------------------------------------------------------------
# Order #88213 items (8.25 % tax on all lines)
# ---------------------------------------------------------------------------
ORDER_88213 = [
    LineItem(sku="SOCKS", unit_price=4.35,  quantity=1, tax_rate=0.0825),
    LineItem(sku="TEE",   unit_price=29.81, quantity=2, tax_rate=0.0825),
    LineItem(sku="PIN",   unit_price=0.10,  quantity=3, tax_rate=0.0825),
]


def test_order_88213_total_cents():
    """Order #88213 must total 6957 cents (receipt showed $69.57).

    The processor received 6956 cents due to float truncation in
    invoice_total_cents().  This test pins the correct value.
    """
    result = invoice_total_cents(ORDER_88213)
    assert result == 6957, (
        f"Expected 6957 cents for order #88213, got {result}. "
        "Likely caused by int(float * 100) truncation in invoice_total_cents()."
    )


def test_line_total_round_half_up():
    """A unit price of $1.005 × 1 with 0 % tax must round UP to $1.01.

    Python's built-in round() uses banker's rounding: round(1.005, 2) → 1.00
    (rounds to even).  Finance policy requires round-half-up → 1.01.
    """
    item = LineItem(sku="TESTSKU", unit_price=1.005, quantity=1, tax_rate=0.0)
    result_cents = invoice_total_cents([item])
    assert result_cents == 101, (
        f"Expected 101 cents for $1.005 SKU (round-half-up), got {result_cents}. "
        "Likely caused by banker's rounding in line_total()."
    )
