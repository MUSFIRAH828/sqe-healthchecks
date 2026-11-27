# Static Analysis (SonarQube Cloud)

## 1. Setup
- Tool: SonarQube Cloud (cloud version of SonarQube), connected to GitHub repo
- Reason: Docker and Java were not available on our machine
- Scan date: <fill>
- Commit hash scanned: <fill>

## 2. Metrics (whole project)
| Metric | Value | What it shows (your own words) |
|---|---|---|
| Lines of code | | |
| Cyclomatic complexity | | |
| Cognitive complexity | | |
| Duplication % | | |
| Code smells | | |
| Bugs | | |
| Vulnerabilities | | |
| Security hotspots | | |
| Coverage % | | |
| Technical debt | | |
| Reliability rating | | |
| Security rating | | |
| Maintainability rating | | |

## 3. Metrics (our module only: hc/api/models.py and workflow files)
| Metric | Value | Comment |
|---|---|---|
| | | |

## 4. Cyclomatic complexity of get_status
- Nodes (N): <fill>   Edges (E): <fill>
- V(G) = E - N + 2 = <fill>
- Decisions + 1 = <fill>  (count each if/elif/for/while/except/and/or)

| Source | Value |
|---|---|
| Hand calculation (CFG) | |
| radon (`radon cc -s hc/api/models.py`) | |
| SonarQube (file level) | |

Why numbers differ (if they do): <fill>

## 5. Findings in our module
| # | Finding | Severity | Why it matters | Proposed fix |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

## 6. Link to risk register
<fill: e.g. "get_status has high complexity, so risk is high and we used MC/DC there.">
