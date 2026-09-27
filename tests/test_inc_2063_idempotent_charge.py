"""
Regression test for INC-2063 — double/triple charges on gateway timeout.

Scenario
--------
The payment gateway captured the charge on the first call but returned
GatewayTimeout (network latency spike).  charge_with_retry retried without
an idempotency_key, so the gateway had no way to know it was a duplicate
and created a second real charge.

233 customers were double-charged; 12 were triple-charged.

Fix requirement
---------------
charge_with_retry must pass a stable idempotency_key (derived from order_id)
on every attempt so the gateway deduplicates retries and returns the original
receipt instead of capturing again.
"""

import pytest
from unittest.mock import MagicMock
from shopfront.payments import charge_with_retry, GatewayTimeout


def test_idempotency_key_passed_on_every_call():
    """
    charge() must be called with an idempotency_key on every attempt,
    and the key must be identical across retries so the gateway can deduplicate.

    FAILS on the buggy code because charge() is called with only
    amount_cents and reference — no idempotency_key.
    """
    gateway = MagicMock()
    # First attempt: gateway captures but times out.
    # Second attempt: gateway deduplicates and returns original receipt.
    gateway.charge.side_effect = [
        GatewayTimeout("upstream timeout"),
        "ch_abc123",
    ]

    result = charge_with_retry(
        gateway, order_id="order-42", amount_cents=4999, attempts=2, backoff=0.0
    )

    assert result == "ch_abc123"

    # Every call must have carried an idempotency_key.
    for i, c in enumerate(gateway.charge.call_args_list):
        assert "idempotency_key" in c.kwargs, (
            f"Attempt {i + 1}: charge() was called without idempotency_key — "
            "retries create duplicate charges (INC-2063)"
        )

    # The key must be the same on every attempt (stable per order).
    keys = [c.kwargs["idempotency_key"] for c in gateway.charge.call_args_list]
    assert len(set(keys)) == 1, (
        f"idempotency_key changed between retries {keys}; "
        "gateway cannot deduplicate (INC-2063)"
    )


def test_idempotency_key_is_derived_from_order_id():
    """
    The idempotency_key must be deterministically derived from the order_id
    so the same key is always produced for the same order across process
    restarts or service instances.
    """
    gateway = MagicMock()
    gateway.charge.side_effect = [
        GatewayTimeout("timeout"),
        "ch_xyz",
    ]

    charge_with_retry(
        gateway, order_id="order-99", amount_cents=1000, attempts=2, backoff=0.0
    )

    keys = [c.kwargs["idempotency_key"] for c in gateway.charge.call_args_list]

    # Key must contain or equal the order_id so it is scoped to this order.
    for key in keys:
        assert "order-99" in str(key), (
            f"idempotency_key '{key}' does not reference the order_id 'order-99'; "
            "a random key per attempt will cause duplicate charges (INC-2063)"
        )
