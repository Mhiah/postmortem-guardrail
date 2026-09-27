# Demo video script (about 3 minutes)

**0:00 Hook (15s).** "Last Black Friday our promo ended six hours early. We wrote a great postmortem. Six months
later, a different team shipped the same timezone bug. Postmortems don't prevent bugs. Guardrails do."

**0:15 What it is (20s).** Show the README table. "Postmortem → Guardrail turns any postmortem into a root-cause fix,
a regression test and a CI rule that blocks the whole bug class, using IBM Bob."

**0:35 The setup (20s).** Show `postmortems/`: two Markdown files and one PDF. Show `.bob/custom_modes.yaml`, the four
modes and their scoped permissions.

**0:55 Bob at work (60s, speed up the recording).** Pick 🛡️ Guardrail Orchestrator. Type the prompt. Show the todo list,
the parallel investigator subagents, a test failing red, then the Fixer and Author running side by side.

**1:55 Verification (25s).** Terminal: `python -m pytest -q` green, `python -m guardrails.run` shows the new rules and
0 violations. Open one Guardrail Report.

**2:20 The guardrail bites (25s).** Add a float shipping fee with `round()`. Run the scanner: GR-2057 fails the build
and names INC-2057. "That bug can never ship again."

**2:45 Ledger + value (15s).** Show the Guardrail Ledger page. "Three incidents closed in N minutes, each with proof.
Every incident, fixed once, forever."
