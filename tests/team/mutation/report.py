"""Summarise a Cosmic Ray session for the business-rule scope and (optionally) fail below a score.

Usage:
    python tests/team/mutation/report.py session.sqlite                    # print summary and survivors
    python tests/team/mutation/report.py session.sqlite --min-score 90     # exit 1 if score < 90
The score counts only mutants that were really run (killed + survived); mutants filtered out of the
scope are ignored. Score = killed / (killed + survived).
"""
import argparse
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

SKIPPED_TEXT = ("Outside business-rule scope", "Filtered operator")


def load(session):
    db = sqlite3.connect(session)
    rows = db.execute(
        """select ms.module_path, ms.start_pos_row, ms.operator_name, ms.occurrence, wr.test_outcome, wr.diff
           from mutation_specs ms join work_results wr using(job_id)
           where wr.output not in (?, ?) and wr.test_outcome is not null
           order by ms.module_path, ms.start_pos_row, ms.start_pos_col""",
        SKIPPED_TEXT,
    ).fetchall()
    pending = db.execute(
        "select count(*) from work_items wi left join work_results wr using(job_id) where wr.job_id is null"
    ).fetchone()[0]
    return rows, pending


def changed_lines(diff):
    keep = [x.strip() for x in (diff or "").splitlines() if x[:1] in "+-" and x[:3] not in ("+++", "---")]
    return " || ".join(keep)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("session")
    parser.add_argument("--min-score", type=float, default=None)
    args = parser.parse_args()
    rows, pending = load(args.session)
    if pending:
        print(f"WARNING: {pending} mutants have not been run yet")
    killed = sum(1 for r in rows if r[4] == "KILLED")
    survived = [r for r in rows if r[4] == "SURVIVED"]
    other = len(rows) - killed - len(survived)
    total = killed + len(survived)
    score = 100.0 * killed / total if total else 0.0
    print(f"mutants run: {total}  killed: {killed}  survived: {len(survived)}  other (timeout/incompetent): {other}")
    print(f"mutation score: {score:.1f}%")

    per_op = defaultdict(lambda: [0, 0])
    for r in rows:
        per_op[r[2]][0 if r[4] == "KILLED" else 1] += 1
    print("\nper operator (killed / survived):")
    for op, (k, s) in sorted(per_op.items()):
        print(f"  {op:45} {k:4} / {s:3}")

    print("\nsurvivors:")
    cache = {}
    for i, (path, line, op, occ, outcome, diff) in enumerate(survived, 1):
        src = cache.setdefault(path, Path(path).read_text(encoding="utf-8").splitlines())
        print(f"{i:3}. {path}:{line}  {op}  #{occ}")
        print(f"       code: {src[line - 1].strip()[:110]}")
        print(f"       diff: {changed_lines(diff)[:160]}")

    if args.min_score is not None and score < args.min_score:
        print(f"\nFAIL: mutation score {score:.1f}% is below the threshold {args.min_score}%")
        sys.exit(1)


if __name__ == "__main__":
    main()
