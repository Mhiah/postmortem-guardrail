# Postmortem → Guardrail

**Every incident fixed once, forever.** Built with IBM Bob 2.0.

Teams write thoughtful postmortems, then the action items rot in a backlog. The same class of bug ships
again six months later in a different file. Postmortem → Guardrail closes that loop: point IBM Bob at a
postmortem (Markdown or PDF) and a team of Bob subagents delivers, with evidence:

1. **Root cause** pinned to exact lines of code.
2. **Regression test** that reproduces the incident with the postmortem's own numbers (fails before, passes after).
3. **Minimal fix.**
4. **Guardrail**: a static-analysis rule that blocks the whole *bug class* codebase-wide, enforced in CI.

Results are published to a plain-English homepage (`docs/index.html`) and the **Guardrail Ledger** (`docs/ledger.html`), a public record of every incident
and the rule that now prevents it.

## How it uses IBM Bob

| Bob feature | Where |
|---|---|
| Custom modes | `.bob/custom_modes.yaml`: Orchestrator, Investigator, Fixer, Author, each with scoped edit permissions |
| Subagents + parallel tasks | The Orchestrator runs one Investigator per incident in parallel, then a Fixer and an Author in parallel |
| Document understanding | Postmortems are read as-is, including a PDF (`postmortems/INC-2063-*.pdf`) |
| Agent mode | Subagents run pytest and the guardrail scanner and iterate until the evidence is green |
| Mode rules | `.bob/rules-<mode>/`: the playbook, report template and per-role rules |

Least privilege by design: the Investigator can only write regression tests, the Author can only write
guardrail rules, and the Orchestrator can only write reports.

## Demo target

`shopfront/` is a small sample e-commerce backend with three real-world bug classes, each with a postmortem:

| Incident | Symptom | Bug class |
|---|---|---|
| INC-2041 | Black Friday promo ended 6 hours early | Timezone-naive datetimes |
| INC-2057 | Invoices off by one cent | Binary floats for money |
| INC-2063 (PDF) | Customers charged twice after timeouts | Retrying non-idempotent calls |

All sample data is synthetic.

## Run it

```bash
pip install -r requirements-dev.txt
python -m pytest -q            # test suite
python -m guardrails.run       # guardrail scanner (CI runs both)
python tools/build_ledger.py   # regenerate the Guardrail Ledger
```

In Bob IDE: open this folder, pick **🛡️ Guardrail Orchestrator**, and ask:
> Close out all three postmortems in postmortems/.

## Results

All three closed in one Bob task: 13/13 todo items, 18 tests passing (up from 9), 0 guardrail violations, every rule confirmed to fire on the pre-fix code. Total cost: 9.32 Bobcoins.

| Incident | Root cause | Guardrail | Minutes |
|---|---|---|---|
| INC-2041 | `shopfront/promotions.py:16` — UTC offset stripped from ISO-8601 expiry | `GR-2041` | 18 |
| INC-2057 | `shopfront/billing.py:15,26` — float rounding + int() truncation | `GR-2057` | 22 |
| INC-2063 | `shopfront/payments.py:13` — charge() retried without idempotency_key | `GR-2063` | 20 |

## Bob sessions

Task session summary screenshots are in [`bob_sessions/`](bob_sessions/), plus the full exported Bob task log ([`guardrail_task_full_log.md`](bob_sessions/guardrail_task_full_log.md)) showing every subtask Bob delegated.

## Repo layout

```
.bob/                 Bob custom modes and per-mode rules
postmortems/          Incident postmortems (Markdown + PDF)
shopfront/            Sample app under repair
guardrails/run.py     Guardrail scanner; rules live in guardrails/rules/
guardrails/reports/   One Guardrail Report per incident, written by Bob
tools/build_ledger.py Builds the Guardrail Ledger page
docs/index.html       Homepage (GitHub Pages); docs/ledger.html = full Guardrail Ledger
bob_sessions/         Bob task summary screenshots (required for submission)
```
