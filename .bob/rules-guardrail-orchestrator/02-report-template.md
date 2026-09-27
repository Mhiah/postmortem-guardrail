# Guardrail report template

Write exactly this structure to `guardrails/reports/<INCIDENT>.md`:

```markdown
---
incident: INC-XXXX
title: <postmortem title>
severity: SEV-N
rule_id: GR-XXXX
minutes_to_guardrail: <number>
---

## Root cause
<file:line> <two or three sentences, plain language>

## Bug class
<one sentence naming the general mistake, not this instance>

## Regression test
`tests/test_inc_XXXX_*.py::<test name>`. Failed before the fix with: <assertion excerpt>

## Fix
<what changed and why it is the smallest correct change>

## Guardrail
`GR-XXXX` in `guardrails/rules/<file>.py`: <what it detects>. Fires on the original code at <file:line>.

## Evidence
<pytest and guardrails.run output, trimmed>
```
