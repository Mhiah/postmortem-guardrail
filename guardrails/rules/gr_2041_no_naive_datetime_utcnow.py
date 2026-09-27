"""Guardrail for INC-2041: datetime.utcnow() produces a naive datetime."""
import ast

RULE_ID = "GR-2041"
INCIDENT = "INC-2041"
SUMMARY = "Use datetime.now(timezone.utc) not datetime.utcnow(); utcnow() returns a naive datetime that breaks aware comparisons."


def check(tree: ast.AST, source: str, path: str) -> list[tuple[int, str]]:
    return [
        (node.lineno, "datetime.utcnow() returns a naive datetime; use datetime.now(timezone.utc) instead")
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "utcnow"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "datetime"
        )
    ]
