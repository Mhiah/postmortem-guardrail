"""Example rule: shows the shape every guardrail follows."""
import ast

RULE_ID = "GR-0000"
INCIDENT = "example"
SUMMARY = "No bare `except:`; it swallows KeyboardInterrupt and hides the real error."


def check(tree: ast.AST, source: str, path: str) -> list[tuple[int, str]]:
    return [
        (node.lineno, "bare `except:`; catch a specific exception")
        for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler) and node.type is None
    ]
