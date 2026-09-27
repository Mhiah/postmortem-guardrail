# Slide outline (7 slides)

1. **Postmortem → Guardrail.** "Every incident fixed once, forever." Built with IBM Bob 2.0. Team name.
2. **The problem.** Postmortem action items rot. The same bug class recurs in a new file. Show the three incident
   headlines with their impact numbers (6 hours of lost promo, 1,870 wrong invoices, 245 double charges).
3. **The idea.** Postmortem in, four things out: root cause, regression test, fix, guardrail in CI.
4. **How Bob does it.** Diagram: Orchestrator → 3 Investigators in parallel → Fixer + Author in parallel → verify →
   Guardrail Ledger. Call out custom modes, subagents, parallel tasks, document understanding (PDF), least privilege.
5. **Live result.** Screenshot of the Guardrail Ledger + one report. Table: incident, root cause, rule, minutes.
6. **The guardrail bites.** Screenshot: a new float-money function fails CI with GR-2057 [INC-2057].
7. **Business value + what's next.** Hours of manual follow-up per incident → minutes; recurrences blocked in CI.
   Next: pull postmortems from Jira/Confluence, support more languages, auto-open PRs.
