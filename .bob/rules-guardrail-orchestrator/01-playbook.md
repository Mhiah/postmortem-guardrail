# Guardrail playbook

Goal: for every postmortem, deliver four things: root cause, failing-then-passing regression test,
minimal fix, and a guardrail rule that blocks the whole bug class. Every claim needs command output as evidence.

## Steps
1. Read every postmortem the user names in `postmortems/` (Markdown and PDF). Make a todo list with one
   item per incident. Record the start time.
2. For each incident, **in parallel**, start a `guardrail-investigator` subagent. Give it: the incident id,
   the postmortem path, and the instruction to return the RCA block described in its rules.
3. When an investigator returns a confirmed failing test, start **in parallel**:
   - a `guardrail-fixer` subagent with the RCA and the failing test path;
   - a `guardrail-author` subagent with the RCA and the bug class.
4. Verify yourself, never trust a subagent's summary alone:
   - `python -m pytest -q` passes.
   - `python -m guardrails.run` reports 0 violations.
   - For each new rule, `git stash` the fix (or check out the pre-fix file) and confirm the rule fires on the
     original buggy code. Restore afterwards.
5. Write `guardrails/reports/<INCIDENT>.md` for each incident using the template in `02-report-template.md`,
   including the elapsed time since step 1.
6. Finish with a short table: incident, root cause file:line, test, rule id, minutes taken.

## Rules
- One incident never blocks another: if one subagent fails, finish the others and report the failure.
- Do not widen scope beyond what the postmortem's action items ask.
- Remind the user to screenshot the task summary into `bob_sessions/` when you finish.

> Environment: on Windows, if `python` is not found, use `py` instead (e.g. `py -m pytest -q`, `py -m guardrails.run`).
