"""Report statement and branch coverage of ONE function (the business-logic scope).

Usage (from the repository root, after coverage has run with --branch):
    python -m coverage json -o coverage.json -q
    python scripts/function_coverage.py hc/api/models.py Check.ping

Exit code is 1 if the function is not 100% covered (usable as a CI gate later).
"""
import ast
import json
import sys


def find_function(path, dotted_name):
    tree = ast.parse(open(path, encoding="utf-8").read())
    parts = dotted_name.split(".")
    nodes = tree.body
    found = None
    for part in parts:
        found = next(
            (n for n in nodes if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == part),
            None,
        )
        if found is None:
            sys.exit(f"{dotted_name} not found in {path}")
        nodes = found.body
    return found.lineno, found.end_lineno


def main():
    path, name = sys.argv[1], sys.argv[2]
    lo, hi = find_function(path, name)
    data = json.load(open("coverage.json"))["files"]
    key = next(k for k in data if k.replace("\\", "/").endswith(path))
    f = data[key]
    executed = [x for x in f["executed_lines"] if lo <= x <= hi]
    missing = [x for x in f["missing_lines"] if lo <= x <= hi]
    exec_br = [b for b in f.get("executed_branches", []) if lo <= b[0] <= hi]
    miss_br = [b for b in f.get("missing_branches", []) if lo <= b[0] <= hi]
    stmts = len(executed) + len(missing)
    branches = len(exec_br) + len(miss_br)
    print(f"{name} (lines {lo}-{hi})")
    print(f"  statements: {len(executed)}/{stmts} covered, missing {missing}")
    print(f"  branches:   {len(exec_br)}/{branches} covered, missing {miss_br}")
    sys.exit(0 if not missing and not miss_br else 1)


if __name__ == "__main__":
    main()
