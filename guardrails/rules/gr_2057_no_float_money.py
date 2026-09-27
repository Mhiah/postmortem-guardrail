"""Guardrail for INC-2057: float used for monetary arithmetic causes cent-level rounding errors."""
import ast
import re

RULE_ID = "GR-2057"
INCIDENT = "INC-2057"
SUMMARY = "Do not use float for monetary values; use decimal.Decimal to avoid cent-level rounding errors."

_MONEY_PATTERN = re.compile(r"price|total|amount|cost|fee|subtotal|discount", re.IGNORECASE)


def _is_money_name(name: str) -> bool:
    return bool(_MONEY_PATTERN.search(name))


def check(tree: ast.AST, source: str, path: str) -> list[tuple[int, str]]:
    if "shopfront" not in path:
        return []
    # If the file already imports Decimal, the author is aware of the requirement.
    imports_decimal = any(
        isinstance(node, ast.ImportFrom)
        and node.module == "decimal"
        and any(alias.name == "Decimal" for alias in node.names)
        for node in ast.walk(tree)
    )
    if imports_decimal:
        return []
    violations = []
    for node in ast.walk(tree):
        # function parameter annotation: def foo(price: float)
        if (
            isinstance(node, ast.arg)
            and isinstance(node.annotation, ast.Name)
            and node.annotation.id == "float"
            and _is_money_name(node.arg)
        ):
            violations.append(
                (node.annotation.lineno, f"float annotation on monetary parameter '{node.arg}'; use decimal.Decimal")
            )
        # variable annotation: unit_price: float = ...
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.annotation, ast.Name)
            and node.annotation.id == "float"
            and isinstance(node.target, ast.Name)
            and _is_money_name(node.target.id)
        ):
            violations.append(
                (node.annotation.lineno, f"float annotation on monetary field '{node.target.id}'; use decimal.Decimal")
            )
    return violations
