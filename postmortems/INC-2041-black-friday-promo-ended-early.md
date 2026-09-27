# Postmortem INC-2041: Black Friday promo ended six hours early

| Field | Value |
|---|---|
| Date | 2025-11-28 |
| Severity | SEV-2 |
| Duration | 6h 01m of lost promo window |
| Customer impact | ~3,100 shoppers saw "code expired" for BF30 between 18:00 and 23:59 Central |
| Status | Mitigated (expiry manually extended). Root cause fix pending. |

## Summary
Marketing configured promo code `BF30` to expire at `2026-11-27T23:59:00-06:00` (midnight Central).
Starting at 18:00 Central the checkout rejected the code as expired. Support received 412 tickets and
we issued goodwill credits.

## Timeline (Central)
- 18:00 First "promo expired" complaint on social.
- 18:40 On-call confirms `is_active` returns False for BF30.
- 19:15 Marketing extends expiry to next day as a workaround.
- 23:59 Intended end of the promotion.

## What we know
- The expiry string includes the merchant's UTC offset.
- The checkout service clock runs in UTC.
- Engineers suspect "something about timezones" in the promotions module, but nobody has pinned the line.

## Action items
1. Find the root cause and fix it.
2. Add a regression test that reproduces the 18:00 Central failure.
3. Prevent this *class* of bug (timezone-naive datetime handling) from shipping again anywhere in the codebase.
