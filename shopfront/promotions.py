"""Promotion codes and their expiry windows."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Promotion:
    code: str
    percent_off: int
    # ISO-8601 timestamp in the merchant's local time, e.g. "2026-11-27T23:59:00-06:00"
    expires_at: str


def _parse_expiry(expires_at: str) -> datetime:
    # Only the date and time matter for expiry.
    return datetime.strptime(expires_at[:19], "%Y-%m-%dT%H:%M:%S")


def is_active(promo: Promotion, now: datetime | None = None) -> bool:
    now = now or datetime.utcnow()
    return now <= _parse_expiry(promo.expires_at)


def apply(promo: Promotion, subtotal_cents: int, now: datetime | None = None) -> int:
    if not is_active(promo, now):
        return subtotal_cents
    return subtotal_cents - (subtotal_cents * promo.percent_off) // 100
