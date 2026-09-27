"""Run every guardrail rule over the codebase and fail if any rule fires.

Each module in guardrails/rules/ defines:
    RULE_ID: str            e.g. "GR-2041"
    INCIDENT: str           postmortem the rule came from, e.g. "INC-2041"
    SUMMARY: str            one line: the bug class this rule blocks
    def check(tree: ast.AST, source: str, path: str) -> list[tuple[int, str]]
        returns (line number, message) for every violation.

Usage: python -m guardrails.run [paths...]   (defaults to shopfront/)
"""
import ast
import importlib
import pkgutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_rules():
    import guardrails.rules as pkg

    for info in sorted(pkgutil.iter_modules(pkg.__path__), key=lambda i: i.name):
        yield importlib.import_module(f"guardrails.rules.{info.name}")


def scan(paths):
    violations = []
    rules = list(load_rules())
    for base in paths:
        files = [base] if base.is_file() else sorted(base.rglob("*.py"))
        for file in files:
            source = file.read_text()
            tree = ast.parse(source, filename=str(file))
            for rule in rules:
                for line, message in rule.check(tree, source, str(file)):
                    violations.append((rule.RULE_ID, rule.INCIDENT, file.relative_to(ROOT), line, message))
    return rules, violations


def main(argv):
    paths = [Path(p).resolve() for p in argv] or [ROOT / "shopfront"]
    rules, violations = scan(paths)
    print(f"Guardrails loaded: {len(rules)}")
    for rule in rules:
        print(f"  {rule.RULE_ID} ({rule.INCIDENT}): {rule.SUMMARY}")
    for rule_id, incident, file, line, message in violations:
        print(f"{file}:{line}: {rule_id} [{incident}] {message}")
    print(f"{len(violations)} violation(s)")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    sys.exit(main(sys.argv[1:]))
