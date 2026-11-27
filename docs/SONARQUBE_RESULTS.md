# SonarQube results (fill in after running scripts/run_sonar.ps1)

Scanner date: ____   SonarQube version: ____   Scope: hc/api (upstream tests and migrations excluded)
Screenshot file names: ____

| Metric | Value | What it shows | What it means for our risks |
|---|---|---|---|
| Lines of code (ncloc) | | Size of the analysed code | Bigger code, more places for defects |
| Cyclomatic complexity | | Number of independent paths, summed over the code | Higher complexity needs more tests (risk P2, P3) |
| Cognitive complexity | | How hard the code is to read and follow | Hard-to-read functions hide mistakes |
| Duplicated lines (%) | | Copy-pasted code | Fixes must be repeated in every copy |
| Code smells | | Maintainability problems (not bugs) | Cost of change; link to technical debt |
| Technical debt | | Estimated time to fix all code smells | Effort figure for the maintainability rating |
| Bugs | | Code likely to be wrong | Direct input to defect list |
| Vulnerabilities | | Security weaknesses in code | Link to security risks (P6) |
| Security hotspots | | Code that needs a manual security review | Review list, not yet confirmed problems |
| Coverage (%) | | Share of lines/branches run by our tests | Our scope is chosen functions, so overall figure is low by design |
| Reliability / Security / Maintainability rating | | A (best) to E (worst) | Summary of the three areas |

## Hand-calculated complexity versus SonarQube
| Function | Hand (CFG, docs/CFG_get_status.md) | radon | SonarQube |
|---|---|---|---|
| Check.get_status | 8 | 8 | ____ |
| Check.ping | 17 | 17 | ____ |
Where to look: SonarQube > the project > Measures > Complexity > hc/api/models.py (a file figure: the sum over all its functions),
and Issues > rule "Cognitive Complexity of functions should not be too high" (python:S3776) for a per-function figure.
If numbers differ, write why (for example, the tools count `and`/`or`, comprehensions or `assert` differently).

## Findings worth following up
(List each bug, vulnerability or hotspot you decide is real: file, line, impact, proposed fix, GitHub Issue number.)
