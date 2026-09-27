# lablab submission form drafts

**Project title:** Postmortem → Guardrail

**Short description (≤ 255 chars):**
Point IBM Bob at an incident postmortem and a team of Bob subagents finds the root cause, writes a failing regression test, ships the fix, and adds a CI guardrail that blocks the whole bug class forever.

**Long description:**
Postmortems are where engineering teams learn the most, and where that learning most often dies. Action items like
"prevent this class of bug" sit in a backlog while the same mistake ships again in another file.

Postmortem → Guardrail turns a postmortem into enforced code in minutes. Using IBM Bob 2.0 custom modes, an
Orchestrator reads each postmortem (Markdown or PDF) and runs one Investigator subagent per incident in parallel.
Each Investigator pins the root cause to exact lines and proves it with a failing regression test built from the
postmortem's own numbers. The Orchestrator then runs a Fixer and a Guardrail Author in parallel: the Fixer makes the
smallest correct change, and the Author writes an AST-based rule that detects the general bug class anywhere in the
codebase and runs in CI. The Orchestrator verifies the evidence itself, including that each new rule fires on the
original buggy code, and publishes a Guardrail Report per incident to a public Guardrail Ledger.

We demo it on a sample shop backend with three classic, expensive incidents: a Black Friday promo that ended six hours
early (timezone-naive datetimes), invoices off by a cent (floats for money), and customers charged twice after gateway
timeouts (retries without idempotency keys). In our run, Bob closed all three postmortems in an average of 20 minutes each (18, 22 and 20). The test suite grew from 9 to 18 passing tests, and every new guardrail was proven to fire on the original buggy code and stay silent on the fix. When one rule came back too broad, the Orchestrator sent it back to the Author subagent to tighten it before signing off.

Each Bob mode has least-privilege edit access: investigators can only write tests, authors can only write rules.

**IBM Bob usage statement:**
IBM Bob IDE is the engine of the project. We built four custom modes (.bob/custom_modes.yaml) with per-mode rules
(.bob/rules-*). The Orchestrator uses Bob subagents and parallel tasks to investigate, fix and guard several incidents
at once, uses document understanding to read Markdown and PDF postmortems, and runs in agent mode to execute tests and
the guardrail scanner until the evidence is green. Every root cause, test, fix and guardrail in the repo was produced
by Bob; task summaries are in bob_sessions/.

**Tags:** IBM Bob, AI agents, Developer productivity, Reliability, SRE, Debugging, Python

**Demo platform:** Web (GitHub Pages)

**Application URL:** https://<github-user>.github.io/<repo>/
