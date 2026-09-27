"""Charging customers through the payment gateway."""
import time


class GatewayTimeout(Exception):
    """The gateway did not answer in time. The charge may or may not have happened."""


def charge_with_retry(gateway, order_id: str, amount_cents: int, attempts: int = 3, backoff: float = 0.0) -> str:
    last_error = None
    for attempt in range(attempts):
        try:
            return gateway.charge(amount_cents=amount_cents, reference=order_id)
        except GatewayTimeout as err:
            last_error = err
            time.sleep(backoff * (attempt + 1))
    raise last_error
