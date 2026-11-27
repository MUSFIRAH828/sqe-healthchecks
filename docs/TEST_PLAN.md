# Test plan (DRAFT v1) - Healthchecks, Checks module
Keep this file updated; record changes in the "Revision log" at the end.

## 1. Scope
In scope: Workflow 1 (create a check) and Workflow 2 (ping a check) in the Checks module, through the browser, the HTTP API and the server-side code.
Out of scope: notification integrations (email, Slack and so on), billing, the Check pause UI beyond what rule BR3 needs, SMTP.
Basis: docs/TEST_BASIS.md. Risks: docs/RISK_REGISTER.md.

## 2. Approach by risk level
| Level | Risks | Technique and depth |
|---|---|---|
| High | P2, R1, R2 | State transition tests (every allowed change, one disallowed change per state), complete MCC then MC/DC on Check.ping, mutation testing, API repeat and negative tests |
| Medium | P1, P3 to P9 | EP and 3-point BVA with generated data, decision tables, API tests with read-back, role checks, k6, pip-audit, Lighthouse and axe-core |
| Low | none yet | One automated check |

## 3. Test levels
Unit (pytest + coverage.py): server-side business logic; API and integration (pytest + Requests, data from the generator); browser end to end (Playwright, use case tests); static analysis (SonarQube); mutation (Cosmic Ray or mutmut under Linux/WSL or CI); usability and accessibility (Lighthouse, axe-core); security (ZAP passive, pip-audit, Playwright role checks); performance (k6) and recovery.

## 4. Roles
| Person | Area |
|---|---|
| Member 1 | Area 1: static analysis, white box, mutation, CI |
| Member 2 | Area 2: API testing and data generation |
| Member 3 | Area 3: use cases, usability, accessibility, security, performance |
Test management is shared. (Fill in names and roll numbers. Each member commits from their own account.)

## 5. Environment and test data
Windows 11 laptop, Python 3.13, Django 6.1.3, SQLite, Chromium for Playwright; Linux (WSL or GitHub Actions) for mutation. Install, seed and reset: docs/SETUP.md. Data: synthetic users owner/member/viewer and 5 checks from scripts/seed_test_data.py; API test inputs come from the generator.

## 6. Entry, exit, suspension, resumption
- Entry: app starts, reset script works, smoke test passes (create check, ping, read back).
- Exit: EC1 to EC5 in docs/RISK_REGISTER.md.
- Suspension: app does not start or the database cannot be reset. Resumption: reset script runs and the smoke test passes.

## 7. Schedule (3 working days)
Day 1: planning documents, unit tests, OpenAPI spec and generator, SonarQube. Day 2: API tests, mutation, CI, Playwright. Day 3: accessibility, security, performance, recovery, defects, reports, PDF, viva practice.

## 8. Three-point estimate (hours): E = (O + 4M + P) / 6
| Area | O | M | P | E | Actual |
|---|---|---|---|---|---|
| Test basis, risk register, plan | 2 | 3 | 5 | 3.17 | |
| Static analysis and CFG | 2 | 3 | 5 | 3.17 | |
| Unit tests, MCC, MC/DC | 5 | 8 | 12 | 8.17 | |
| API tests, OpenAPI, generator | 6 | 9 | 14 | 9.33 | |
| Mutation and CI | 4 | 6 | 10 | 6.33 | |
| Use cases and Playwright | 4 | 6 | 9 | 6.17 | |
| Usability and accessibility | 2 | 3 | 5 | 3.17 | |
| Security | 2 | 3 | 5 | 3.17 | |
| Performance and recovery | 3 | 4 | 7 | 4.33 | |
| Defects, RCA, reports, PDF | 4 | 6 | 9 | 6.17 | |
| Viva practice | 3 | 4 | 6 | 4.17 | |
| Total | | | | 57.35 | |
The total is far more than 3 days of one person's time, which is why work follows the order of marks (see R1).

## 9. Risks
See docs/RISK_REGISTER.md (product risks P1 to P9, project risks R1 to R3).

## Revision log
- v1: first draft.
