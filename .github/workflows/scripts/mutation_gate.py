"""Mutation score gate for the business-rule functions (Check.ping and Check.get_status).

Run after:  mutmut run "hc.api.models.xǁCheckǁping__mutmut_*" "hc.api.models.xǁCheckǁget_status__mutmut_*"
Usage:      python scripts/mutation_gate.py --min-score 80

Score = killed / (killed + survived + timeout + suspicious + no tests).
Exit code 1 if the score is below the threshold or any mutant was never checked.
"""
import argparse
import subprocess
import sys

TARGETS = ("ǁCheckǁping__", "ǁCheckǁget_status__")
KILLED = {"killed", "timeout"}


def read_results():
    out = subprocess.run(
        ["mutmut", "results", "--all", "true"], capture_output=True, text=True, encoding="utf-8"
    ).stdout
    rows = []
    for line in out.splitlines():
        line = line.strip()
        if ": " not in line:
            continue
        name, status = line.rsplit(": ", 1)
        if any(t in name for t in TARGETS):
            rows.append((name, status.strip()))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-score", type=float, required=True)
    args = parser.parse_args()

    rows = read_results()
    if not rows:
        sys.exit("No mutants found for the target functions. Did mutmut run?")

    counts = {}
    for _, status in rows:
        counts[status] = counts.get(status, 0) + 1
    unchecked = counts.get("not checked", 0)
    skipped = counts.get("skipped", 0)
    total = len(rows) - unchecked - skipped
    killed = sum(counts.get(s, 0) for s in KILLED)
    score = 100.0 * killed / total if total else 0.0

    print("Mutation results:", dict(sorted(counts.items())))
    print(f"Mutants counted: {total}, killed: {killed}, score: {score:.1f}% (minimum {args.min_score}%)")
    for name, status in rows:
        if status == "survived":
            print("  SURVIVED:", name)

    if unchecked:
        sys.exit(f"FAIL: {unchecked} mutants were never checked.")
    if score < args.min_score:
        sys.exit(f"FAIL: mutation score {score:.1f}% is below {args.min_score}%.")
    print("PASS")


if __name__ == "__main__":
    main()
