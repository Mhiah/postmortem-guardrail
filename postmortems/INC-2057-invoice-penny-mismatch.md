# Postmortem INC-2057: Invoices off by one cent, reconciliation failed

| Field | Value |
|---|---|
| Date | 2026-02-03 |
| Severity | SEV-3 |
| Duration | 9 days before detection |
| Customer impact | 1,870 invoices charged 1 cent less or more than the itemized receipt |
| Status | Finance reconciled by hand (~14 engineer-hours). Root cause fix pending. |

## Summary
Nightly reconciliation against the payment processor flagged 1,870 mismatches, each of exactly $0.01.
Example order #88213: receipt showed $69.57, the processor received 6956 cents.
Another example: a $1.005 test SKU billed at $1.00 instead of $1.01.

## What we know
- Line items carry prices as dollars with tax rates such as 8.25%.
- The receipt renderer and the charge path both call `shopfront.billing`.
- Finance policy: amounts round half-up to the cent, per line item.

## Action items
1. Find the root cause and fix it so totals are exact to the cent.
2. Add regression tests using order #88213: SOCKS $4.35 x1, TEE $19.99 x3 at 8.25% tax, PIN $0.10 x3 must total 6957 cents.
3. Prevent binary floating point from being used for money anywhere in the codebase.
