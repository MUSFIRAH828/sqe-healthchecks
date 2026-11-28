# Evidence guide: what to capture, where, and how

Save every file under docs/evidence/<module>/ and note the file name in the report. Take screenshots AND keep the raw output file;
a screenshot alone is not enough. Capture evidence when you do the work, not at the end. Put the date in the file name.
Keep our folder layout (tests/team/...): the assignment says to keep our own tests in a separate folder such as tests/team/.

| Module | Capture | Where and how |
|---|---|---|
| 1 System and scope | Upstream repository page, our fork page, baseline commit hash | Browser: github.com/healthchecks/healthchecks and github.com/MUSFIRAH828/sqe-healthchecks. PowerShell: `git log -1 --format="%H %ci %s" c1039ad2` |
| | App dashboard, create-check form, created check, ping and its "Up" status | Browser http://localhost:8000 (server running): Add Check, fill, save; open the ping URL in a new tab; refresh the dashboard |
| | Two roles, different permissions | Log in as owner@, member@ and viewer@example.com (password in tests/team/seed_output.json); screenshot each dashboard |
| 2 SonarQube | Project overview, Measures (complexity, coverage, duplication), Issues | Alisha: http://localhost:9000 > project sqe-healthchecks. Also save docs/SONARQUBE_RESULTS.md |
| | CFG and hand calculation | docs/cfg_get_status.png and docs/CFG_get_status.md |
| 3 Unit tests | Test run | `python -m pytest tests/team/unit -v > docs/evidence/unit/pytest_output.txt` and a screenshot of the summary line (167 passed) |
| | Coverage per function | `python -m coverage run -m pytest tests/team/unit -q`, `python -m coverage json -o coverage.json -q`, then each `python scripts/function_coverage.py hc/api/models.py Check.ping` (and the other 10); screenshot or redirect to a file |
| | Coverage report page | `python -m coverage html`, open htmlcov\index.html, open hc_api_models_py.html, screenshot the ping() lines in green |
| | MCC and MC/DC | docs/MCC_MCDC.md and the test names in tests/team/unit/test_ping_mcc.py |
| 4 API tests | Run output with test ids | Server running; `python -m pytest tests/team/api -v > docs/evidence/api/api_tests.txt` |
| | Invalid request and rejection, read-back | Same output (ids such as BVA-minimum - 1-59); show the code in test_create_check_api.py check_create() |
| 5 Generator | Spec, script, generated data, before and after | `python tests/team/generator/generator.py` (screenshot summary), commit generated_cases.json, then follow docs/GENERATOR_DEMO.md (edit spec, regenerate, `git diff`, rerun API tests) |
| 6 Mutation | Tool run, score, survivors | GitHub Actions tab > latest run > job "mutation" (log screenshot); Summary > Artifacts > mutation (download mutation_report.txt) |
| 7 CI | Green run, red run, blocked PR, fix PR | GitHub > Actions tab (list of runs); a pull request page showing "Merging is blocked" and the red check; the fix PR with the failing commit and the passing commit |
| 8 Use cases / Playwright | Playwright HTML report, flow results | Later: `pytest tests/team/e2e --headed` and the HTML report; use cases in docs/USE_CASES.md (Ayesha) |
| 9 Lighthouse | Accessibility, Best Practices, SEO scores of the dashboard and check form | Chrome: log in, press F12, tab Lighthouse, tick the three categories, Analyze page load. Save the report (three dots, Save as HTML). Do it again after the fix |
| | axe-core | Later with @axe-core/playwright; interim: axe DevTools browser extension, Scan all of my page |
| 10 Security | ZAP passive scan | Install OWASP ZAP, Manual Explore with the browser it opens, run both workflows (Playwright tests later), then Alerts tab; Report > Generate HTML report |
| | Session cookie and role evidence | Chrome F12 > Application > Cookies > localhost (sessionid: HttpOnly, SameSite); access matrix docs/ACCESS_MATRIX.md (Ayesha) |
| | Dependency audit | `pip install pip-audit`, then `pip-audit -r requirements.txt > docs/evidence/security/pip_audit.txt`; list package names and versions checked |
| 11 Performance | k6 runs (1 user x2, 5 users x2) | Later: install k6 (Windows installer), `k6 run --summary-export=run1.json script.js`; keep raw output and environment details (CPU, RAM, Python version) |
| 12 Recovery | Failure, retry, final state | Later: test output and the database read-back |
| 13 Defects | Issues list, 2 RCAs, Pareto | GitHub > Issues tab (labels: severity, priority); RCA documents; Pareto chart from the defect categories |
| 14 Management | Plan, estimates, risks, weekly reports, completion report | docs/TEST_PLAN.md, RISK_REGISTER.md, TRACEABILITY.md, weekly_report_N.md, COMPLETION_REPORT.md |
