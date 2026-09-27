from datetime import datetime, timezone

from shopfront.promotions import Promotion, apply, is_active

PROMO = Promotion(code="FALL10", percent_off=10, expires_at="2026-10-31T23:59:00+00:00")

UTC = timezone.utc


def test_active_before_expiry():
    assert is_active(PROMO, now=datetime(2026, 10, 30, 12, 0, tzinfo=UTC))


def test_inactive_after_expiry():
    assert not is_active(PROMO, now=datetime(2026, 11, 1, 0, 1, tzinfo=UTC))


def test_apply_discount():
    assert apply(PROMO, 10_000, now=datetime(2026, 10, 1, tzinfo=UTC)) == 9_000
