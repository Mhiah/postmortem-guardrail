"""Every guardrail must catch the bug it was written for and pass on clean code."""
import ast

from guardrails.run import load_rules


def fires(rule, source: str) -> bool:
    return bool(rule.check(ast.parse(source), source, "snippet.py"))


def test_example_rule():
    rule = next(r for r in load_rules() if r.RULE_ID == "GR-0000")
    assert fires(rule, "try:\n    x()\nexcept:\n    pass\n")
    assert not fires(rule, "try:\n    x()\nexcept ValueError:\n    pass\n")
