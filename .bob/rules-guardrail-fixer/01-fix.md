# Fixer rules

1. Read the RCA and the failing test. Do not edit the regression test's assertions.
2. Make the smallest correct change in `shopfront/`. Prefer standard-library solutions
   (`zoneinfo`/aware datetimes, `decimal.Decimal`, idempotency keys).
3. Keep public function signatures compatible unless the postmortem requires otherwise; update existing
   tests only if they encoded the buggy behaviour, and say so.
4. Run the regression test, then `python -m pytest -q`. Both must pass.
5. Return: files changed, a one-paragraph explanation, and the pytest output.

> Environment: on Windows, if `python` is not found, use `py` instead (e.g. `py -m pytest -q`, `py -m guardrails.run`).
