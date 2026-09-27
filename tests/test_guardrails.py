"""Every guardrail must catch the bug it was written for and pass on clean code."""
import ast

from guardrails.run import load_rules


def fires(rule, source: str) -> bool:
    return bool(rule.check(ast.parse(source), source, "snippet.py"))


def test_example_rule():
    rule = next(r for r in load_rules() if r.RULE_ID == "GR-0000")
    assert fires(rule, "try:\n    x()\nexcept:\n    pass\n")
    assert not fires(rule, "try:\n    x()\nexcept ValueError:\n    pass\n")


def test_gr2041_no_naive_datetime_utcnow():
    rule = next(r for r in load_rules() if r.RULE_ID == "GR-2041")
    # must flag: datetime.utcnow() — the bug pattern from INC-2041
    assert fires(rule, "from datetime import datetime\nnow = datetime.utcnow()\n")
    # must pass: datetime.now(timezone.utc) — the correct replacement
    assert not fires(rule, "from datetime import datetime, timezone\nnow = datetime.now(timezone.utc)\n")


def test_gr2057_no_float_money():
    rule = next(r for r in load_rules() if r.RULE_ID == "GR-2057")

    def fires_shopfront(source: str) -> bool:
        return bool(rule.check(ast.parse(source), source, "shopfront/billing.py"))

    # must flag: float annotation on a dataclass field — the INC-2057 bug pattern
    assert fires_shopfront("from dataclasses import dataclass\n@dataclass\nclass LineItem:\n    unit_price: float\n")
    # must flag: float annotation on a function parameter
    assert fires_shopfront("def calc(price: float) -> int:\n    return int(price * 100)\n")
    # must pass: Decimal annotation — the correct replacement
    assert not fires_shopfront("from decimal import Decimal\n@dataclass\nclass LineItem:\n    unit_price: Decimal\n")
    # must pass: float annotation outside shopfront/ is not flagged
    assert not rule.check(ast.parse("x: float = 1.0\n"), "x: float = 1.0\n", "utils/helpers.py")
    # must pass: float on a non-monetary name (duration/backoff) is not flagged
    assert not fires_shopfront("def retry(backoff: float) -> None:\n    pass\n")
    # must pass: file that imports Decimal is already aware — unit_price: float is intentional (API compat)
    assert not fires_shopfront(
        "from decimal import Decimal\nfrom dataclasses import dataclass\n"
        "@dataclass\nclass LineItem:\n    unit_price: float\n"
    )


def test_gr2063_idempotent_retry():
    rule = next(r for r in load_rules() if r.RULE_ID == "GR-2063")

    # must flag: charge() inside a for loop with no idempotency_key — the INC-2063 bug pattern
    buggy = (
        "for attempt in range(3):\n"
        "    gateway.charge(amount_cents=100, reference='ord-1')\n"
    )
    assert fires(rule, buggy)

    # must pass: charge() inside a for loop WITH idempotency_key — the fix
    fixed = (
        "for attempt in range(3):\n"
        "    gateway.charge(amount_cents=100, reference='ord-1', idempotency_key='k')\n"
    )
    assert not fires(rule, fixed)

    # must pass: charge() outside any loop (single call, no retry risk)
    outside_loop = "gateway.charge(amount_cents=100, reference='ord-1')\n"
    assert not fires(rule, outside_loop)
