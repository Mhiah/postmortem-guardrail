# Investigator rules

1. Read the postmortem (PDF or Markdown). Extract: symptom, concrete example values, and action items.
2. Search `shopfront/` for the code path. Name the exact file and line numbers.
3. Write `tests/test_inc_<number>_<slug>.py` that reproduces the incident with the postmortem's own
   example values. Use only pytest and the standard library.
4. Run it. It **must fail** on the current code. If it passes, your root cause is wrong: keep looking.
5. Do not change application code.

Return this block to the orchestrator:

```
INCIDENT: INC-XXXX
ROOT_CAUSE: <file>:<lines> <one sentence>
BUG_CLASS: <general mistake>
TEST: <path>::<name>
FAILURE: <assertion error excerpt>
```

> Environment: on Windows, if `python` is not found, use `py` instead (e.g. `py -m pytest -q`, `py -m guardrails.run`).
