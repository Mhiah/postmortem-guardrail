import pytest

from shopfront.payments import GatewayTimeout, charge_with_retry


class FlakyGateway:
    """Fails the first N calls before charging."""

    def __init__(self, failures: int):
        self.failures = failures
        self.charges = []

    def charge(self, amount_cents, reference, idempotency_key=None):
        if self.failures:
            self.failures -= 1
            raise GatewayTimeout()
        self.charges.append((reference, amount_cents))
        return f"ch_{len(self.charges)}"


def test_charges_once_when_healthy():
    gw = FlakyGateway(failures=0)
    assert charge_with_retry(gw, "order-1", 500) == "ch_1"
    assert gw.charges == [("order-1", 500)]


def test_retries_then_succeeds():
    gw = FlakyGateway(failures=2)
    assert charge_with_retry(gw, "order-1", 500) == "ch_1"


def test_gives_up():
    with pytest.raises(GatewayTimeout):
        charge_with_retry(FlakyGateway(failures=5), "order-1", 500)
