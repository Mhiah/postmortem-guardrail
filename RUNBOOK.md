# Runbook for the Bob run (mia)

Budget: 40 Bobcoins, no top-ups. Watch usage at https://bob.ibm.com/admin/subscription.

## 0. Setup (10 min)
1. Accept the hackathon Bob invite. Sign in with IBMid using your **registration email**.
2. Select instance **ibm-coding-challenge-uat (us-east)**.
3. Clone the repo and open the folder in Bob IDE. Run `pip install -r requirements-dev.txt`.
4. Check the modes appear in the mode picker (🛡️ 🔎 🔧 🧱). If they don't, reload the window.

## 1. Dry run on one incident (cheap, ~5 coins)
Mode: 🛡️ Guardrail Orchestrator. Prompt:
> Close out postmortems/INC-2041-black-friday-promo-ended-early.md.

Check: `tests/test_inc_2041_*.py` exists, `guardrails/rules/gr_2041_*.py` exists,
`guardrails/reports/INC-2041.md` exists, `python -m pytest -q` and `python -m guardrails.run` are green.
Screenshot the task summary → `bob_sessions/guardrail_task01_inc2041_summary.png`.

## 2. The main run, recorded for the video (~15–20 coins)
Start screen recording, note the clock. Prompt:
> Close out the other two postmortems in postmortems/, INC-2057 and the PDF INC-2063. Run them in parallel.

Screenshot → `bob_sessions/guardrail_task02_inc2057_inc2063_summary.png`.

## 3. Prove the guardrail works (~3 coins, great video moment)
In 🛡️ mode or plain Ask:
> Add a new function to shopfront/billing.py that computes a shipping fee as a float and rounds it with round().
Then run `python -m guardrails.run` in the terminal: GR-2057 should fail the build. Revert the change.

## 4. Publish
```bash
python tools/build_ledger.py
git add -A && git commit -m "Close INC-2041, INC-2057, INC-2063 with Bob" && git push
```
Enable GitHub Pages (Settings → Pages → Deploy from branch → `main` / `/docs`). That URL is the **Application URL**.
Fill in the Results table in README.md from the reports.

## If something goes wrong
- A subagent loops or fails: stop it, and rerun that single incident in its own mode (🔎 then 🔧 then 🧱).
- Coins running low: skip step 3 and demo the guardrail by showing the rule's tests instead.
- Never fake a Bob run. The rules say simulated runs must not be presented as Bob work.
