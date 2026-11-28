"""Cosmic Ray filter: keep only mutants inside the business-rule functions (everything else is skipped).

Usage:  python tests/team/mutation/scope_filter.py <session.sqlite>
The functions are listed in SCOPE below; their line ranges are read from the source files, so the
filter stays correct when lines move.
"""
import ast
import sys
from pathlib import Path

from cosmic_ray.tools.filters.filter_app import FilterApp
from cosmic_ray.work_item import WorkerOutcome, WorkResult

SCOPE = {
    "hc/api/models.py": ["Check.get_grace_start", "Check.going_down_after", "Check.get_status", "Check.ping"],
    "hc/api/views.py": ["Spec", "create_check"],
    "hc/api/decorators.py": ["authorize", "authorize_read"],
}


def ranges_for(path, names):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    found = []
    for dotted in names:
        nodes = tree.body
        node = None
        for part in dotted.split("."):
            node = next(n for n in nodes if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == part)
            nodes = node.body
        found.append((node.lineno, node.end_lineno))
    return found


class ScopeFilter(FilterApp):
    """Skip every mutant outside the chosen business-rule functions."""

    def description(self):
        return __doc__

    def filter(self, work_db, args):
        allowed = {path: ranges_for(path, names) for path, names in SCOPE.items()}
        kept = skipped = 0
        for item in work_db.pending_work_items:
            mutation = item.mutations[0]
            line = mutation.start_pos[0]
            path = str(mutation.module_path).replace("\\", "/")
            if any(lo <= line <= hi for lo, hi in allowed.get(path, [])):
                kept += 1
                continue
            skipped += 1
            work_db.set_result(
                item.job_id, WorkResult(output="Outside business-rule scope", worker_outcome=WorkerOutcome.SKIPPED)
            )
        print(f"scope filter: {kept} mutants kept, {skipped} skipped")


def main(argv=None):
    return ScopeFilter().main(argv)


if __name__ == "__main__":
    sys.exit(main())
