# CI quality gate: setup, thresholds and the two pull requests

Workflow: .github/workflows/ci.yml. Jobs: unit (tests and 100% coverage gate), api (tests against the running app),
mutation (Cosmic Ray, score gate), sonar (SonarQube in a service container, gate on bugs, vulnerabilities, coverage),
package (release archive; it runs only when all four pass, so deployment is blocked by any failure).
No continue-on-error and no "|| true" are used.

## Turn the workflow into a real merge block (GitHub, one time)
Repository > Settings > Branches > Add branch protection rule for `master`:
- tick "Require a pull request before merging"
- tick "Require status checks to pass before merging" and select: unit, api, mutation, sonar
- tick "Do not allow bypassing the above settings"

## Thresholds and why
| Gate | Threshold | Reason (evidence) |
|---|---|---|
| Coverage | 100% statements and branches for each listed business-rule function | Required by the assignment; every function reached 100% (see docs/MCC_MCDC.md and coverage output) |
| Mutation score | at least 90% | First run scored 73.9% (weak tests), after the new tests 97.3% with 7 equivalent mutants left, so 90% fails weak tests and passes the current suite (docs/mutation) |
| SonarQube | bugs 0, vulnerabilities 0, coverage at least the value set in tests/team/sonar_gate.py | Fill in from the first real scan (docs/SONARQUBE_RESULTS.md) and write the reason here |

## The two pull requests the assignment asks for
1. Blocked pull request: create a branch `demo/weak-tests`, delete 3 or 4 tests from tests/team/unit/test_check_ping.py
   and tests/team/unit/test_mutation_killers.py, push, open a pull request. The mutation job fails (score below 90%),
   so the pull request cannot be merged. Keep the pull request open as evidence and screenshot the red check.
2. Documented fix through a pull request ("fails before, passes after"): branch `fix/read-only-error-message`.
   Defect: a read-only API key gets 401 "wrong api key" on write endpoints (hc/api/decorators.py, authorize).
   First commit a test that expects 403 "read-only key cannot write" (CI fails), then commit the fix (CI passes).
   Merge it and link the GitHub Issue.
