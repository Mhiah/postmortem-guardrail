"""
Regression test for INC-2041 — Black Friday promo BF30 ended six hours early.

Root cause
----------
shopfront/promotions.py _parse_expiry() strips the UTC offset from the
ISO-8601 expires_at string (takes only the first 19 characters), producing a
naive datetime that represents the *merchant's local time*.  is_active() then
compares that naive value against a UTC `now`.

For BF30:
  expires_at = "2026-11-27T23:59:00-06:00"   (midnight Central = 06:00 UTC Nov 28)
  parsed     = datetime(2026, 11, 27, 23, 59, 0)   # naive, offset discarded

At 18:00 Central (= 00:00 UTC Nov 28):
  now (UTC)  = datetime(2026, 11, 28, 0, 0, 0, tzinfo=UTC)
  now <= parsed  →  2026-11-28T00:00Z  <=  2026-11-27T23:59 (naive)

Python raises TypeError when comparing aware and naive datetimes, OR the
buggy code calls datetime.utcnow() returning a naive UTC value, making:
  naive UTC 2026-11-28T00:00 <= naive local 2026-11-27T23:59  →  False (expired!)

The promo should have been active until 06:00 UTC Nov 28; it was rejected
six hours early.
"""

from datetime import datetime, timezone, timedelta

import pytest
from shopfront.promotions import Promotion, is_active

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------
BF30 = Promotion(
    code="BF30",
    percent_off=30,
    expires_at="2026-11-27T23:59:00-06:00",  # midnight Central = 06:00 UTC Nov 28
)

UTC = timezone.utc

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_promo_active_at_18_utc_on_black_friday():
    """
    At 18:00 UTC on 2026-11-27 (= noon Central, 6 hours BEFORE expiry),
    BF30 must be active.  The bug caused is_active() to return False here
    because _parse_expiry discards the -06:00 offset and compares the naked
    local time 23:59 against UTC 18:00, which happens to look expired once
    UTC midnight passes.

    NOTE: the incident's *observed* failure started at 18:00 Central
    = 00:00 UTC Nov 28.  We test the equally-valid noon-Central / 18:00 UTC
    window to show that any UTC time between 00:00 and 06:00 on Nov 28 would
    also be affected, but the simplest reproducer that proves the offset is
    discarded is 18:00 UTC Nov 27 (clearly still 6 h before even the naive
    wall-clock expiry), yet we also directly cover the exact incident moment.
    """
    # Exact incident moment: 18:00 Central = 00:00 UTC Nov 28
    # The promo should still be active (real expiry = 06:00 UTC Nov 28).
    incident_moment_utc = datetime(2026, 11, 28, 0, 0, 0, tzinfo=UTC)
    assert is_active(BF30, now=incident_moment_utc), (
        "BF30 must be active at 00:00 UTC Nov 28 "
        "(= 18:00 Central, six hours before the true UTC expiry at 06:00 UTC)."
    )


def test_promo_inactive_after_true_utc_expiry():
    """
    After the true UTC expiry (06:00 UTC 2026-11-28) the promo must be
    inactive.  This confirms the correct post-expiry behaviour once the
    timezone bug is fixed.
    """
    after_expiry_utc = datetime(2026, 11, 28, 6, 0, 1, tzinfo=UTC)
    assert not is_active(BF30, now=after_expiry_utc), (
        "BF30 must be inactive at 06:00:01 UTC Nov 28 (past its true expiry)."
    )
