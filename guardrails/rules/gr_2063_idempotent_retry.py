"""Guardrail for INC-2063: retried gateway.charge() calls must carry an idempotency_key."""
import ast

RULE_ID = "GR-2063"
INCIDENT = "INC-2063"
SUMMARY = "Retried external calls must pass an idempotency_key to prevent duplicate side-effects on timeout."


def check(tree: ast.AST, source: str, path: str) -> list[tuple[int, str]]:
    violations = []
    for for_node in ast.walk(tree):
        if not isinstance(for_node, ast.For):
            continue
        for node in ast.walk(for_node):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Attribute) and func.attr == "charge"):
                continue
            has_key = any(kw.arg == "idempotency_key" for kw in node.keywords)
            if not has_key:
                violations.append(
                    (node.lineno, "gateway.charge() inside a retry loop must pass idempotency_key")
                )
    return violations
