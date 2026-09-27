# Guardrail author rules

1. Read `guardrails/run.py` and the example `guardrails/rules/gr_0000_no_bare_except.py`. Follow that shape:
   `RULE_ID`, `INCIDENT`, `SUMMARY`, `check(tree, source, path)`.
2. Name the file `guardrails/rules/gr_<number>_<slug>.py` and use `RULE_ID = "GR-<number>"` matching the incident.
3. Target the **bug class**, not the one line. Examples:
   - timezone bugs: `datetime.utcnow()`, `datetime.now()` without `tz`, `strptime` results compared without tzinfo,
     slicing offsets off ISO timestamps.
   - money bugs: `float` annotations or `round()` / `int(x * 100)` in billing or payment modules.
   - retry bugs: a retry loop around an external call that passes no `idempotency_key`.
4. Add tests to `tests/test_guardrails.py`: at least one snippet the rule must flag (taken from the original
   buggy code) and one it must allow (the fixed pattern).
5. Keep false positives low: the rule must report 0 violations on the fixed codebase.
6. Run `python -m pytest -q tests/test_guardrails.py` and return the rule path, what it detects, and the output.

> Environment: on Windows, if `python` is not found, use `py` instead (e.g. `py -m pytest -q`, `py -m guardrails.run`).
