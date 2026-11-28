# Project checklist (status on 28 Nov 2026). Update it every day; it feeds the weekly progress report.

Legend: DONE = exists and was run; WRITTEN = files exist but must be run/pushed by a team member; TODO = not started.

| # | Component (marks) | Status | What exists | What is left |
|---|---|---|---|---|
| 1 | System and scope (5) | DONE | Fork, baseline commit, SETUP.md, seed/reset, TEST_BASIS.md | Register description in the Google Sheet (check), screenshots |
| 2 | Static analysis (5) | WRITTEN | sonar-project.properties, run_sonar.ps1, CFG (hand calc 8), SONARQUBE_RESULTS template | Alisha runs SonarQube, fills numbers, compares with hand CC |
| 3 | Test plan, estimates, traceability (7) | DONE (draft) | TEST_PLAN.md, TRACEABILITY.md | Actual hours column, update after each step |
| 4 | Risk register, exit criteria (5) | DONE (draft) | RISK_REGISTER.md | Final scores check, 5x5 matrix picture |
| 5 | White-box unit tests (16) | DONE | 167 unit tests, 11 functions at 100% statement and branch, CFG, MCC and MC/DC | Run all, screenshots, explain in viva |
| 6 | API and integration tests (10) | DONE | 75 API tests, EP/BVA from generator, read-back, repeats | Alisha runs and explains; API weakness list |
| 7 | Test data generator (7) | DONE | generator.py, openapi.yaml, GENERATOR_DEMO.md | Run the constraint-change demo yourself for evidence |
| 8 | Use case specification (3) | TODO | - | Ayesha: USE_CASES.md (UC1, UC2, 2 alternative and 2 exception flows each) |
| 9 | Use case automation, Playwright (6) | TODO | - | Playwright tests for every flow, assert result and postcondition |
| 10 | Mutation and CI gate (8) | WRITTEN | Cosmic Ray config, 3 custom operators, 264 mutants, 73.9% to 97.3%, 69 survivors analysed, ci.yml, gate scripts | Push, run CI, collect logs, blocked PR, fix PR, branch protection |
| 11 | Usability and accessibility (5) | TODO | - | Playwright task and keyboard tests, Lighthouse, axe-core, fix one screen, before and after |
| 12 | Defensive security (6) | TODO | Access matrix template given to Ayesha | 4 Playwright role checks, ZAP passive scan, pip-audit |
| 13 | Performance and recovery (5) | TODO | - | k6 (1 and 5 users, 2 runs each, 60 s), recovery test |
| 14 | Defects and RCA (7) | TODO | Weaknesses noticed (see below) | GitHub Issues, 5 Whys and fishbone for 2 defects, Pareto |
| 15 | Monitoring and completion report (5) | TODO | - | Weekly progress, GQM metrics, completion report, release or hold |
| 16 | Viva, live task, AI-use record (20) | IN PROGRESS | AI_USE_RECORD.md (fill the last column truthfully) | Practice: rerun a test and explain assertions; live rule change |

## Weaknesses found so far (turn each into a GitHub Issue)
1. A read-only API key gets 401 "wrong api key" on write endpoints; 403 with a clear message is expected.
2. POST /api/v3/checks/ with an empty body creates a check (nothing is required).
3. HEAD requests to a ping URL count as pings.
4. /ping/<code>/00 is treated as exit status 0.
5. resume sets the status to "new" and clears last_ping (not "up"); users may not expect this.
6. The ping URL needs no login: anyone with the link can ping or flood a check.
