from shopfront.billing import LineItem, invoice_total, invoice_total_cents


def test_single_item():
    assert invoice_total([LineItem("MUG", 12.00, 2)]) == 24.00


def test_cents():
    assert invoice_total_cents([LineItem("MUG", 12.00, 2)]) == 2400
