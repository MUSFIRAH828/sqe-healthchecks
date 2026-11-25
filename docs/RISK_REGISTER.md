# Risk register and exit criteria (DRAFT v1) - Healthchecks, Checks module

Scoring: likelihood (L) 1-5 x impact (I) 1-5 = score. Level: High 15-25, Medium 8-14, Low 1-7.
Risk level decides technique and depth: High = complete MCC/MC-DC plus BVA plus mutation plus API repeat/negative tests;
Medium = EP/BVA or decision table plus API tests; Low = one automated check.

## Product risks
| ID | Risk | L | I | Score | Level | Technique and depth | Related requirement / rule |
|---|---|---|---|---|---|---|---|
| P1 | Timeout/grace boundary accepted or rejected wrongly (59, 60, 31,536,000, 31,536,001) | 2 | 4 | 8 | Medium | 3-point BVA and EP on API and unit level | FR3, BR1 |
| P2 | Wrong status after a ping (for example fail does not give down, or down never returns to up) | 3 | 5 | 15 | High | State transition testing, every allowed move plus one disallowed move per state, mutation testing | FR6, FR7, BR3 |
| P3 | Paused check handled wrongly (paused AND manual_resume decision) | 3 | 4 | 12 | Medium | Decision table, MCC then MC/DC | BR2 |
| P4 | Repeated create request makes duplicate checks | 3 | 4 | 12 | Medium | API repeat-request tests, read back after success and rejection | FR5 |
| P5 | Read-only role can create or change checks | 2 | 5 | 10 | Medium | Access matrix, Playwright role checks, API key tests | BR4 |
| P6 | Anyone with a ping URL can ping, flood or fake a status (no login) | 4 | 3 | 12 | Medium | Source review, ZAP passive scan, security observations | FR6 |
| P7 | Ping is slow or fails under concurrent users | 3 | 4 | 12 | Medium | k6 with 1 and 5 users, p95 and failure rate | FR6, FR11 |
| P8 | Check data left inconsistent after a failure during a write | 2 | 5 | 10 | Medium | Failure-and-recovery test, no duplicates after retry | FR1, FR6 |
| P9 | Vulnerable dependency or poor accessibility on the check form | 3 | 3 | 9 | Medium | pip-audit, Lighthouse, axe-core | n/a |

## Project risks
| ID | Risk | L | I | Score | Level | Response |
|---|---|---|---|---|---|---|
| R1 | Very short schedule (3 days) against 120 marks of work | 5 | 5 | 25 | High | Work in order of marks, daily plan, cut scope in the written completion report where needed |
| R2 | One person carries all areas; viva knowledge gap | 4 | 5 | 20 | High | Every file read and explained in own words, viva practice on day 3, other members commit and own their own part |
| R3 | Tool setup problems on Windows (mutmut needs Linux, SonarQube needs Docker or Java) | 4 | 3 | 12 | Medium | Use WSL or GitHub Actions for mutation, Docker for SonarQube, decide on day 1 |

## Exit criteria (measurable)
| ID | Criterion | Type | Tied to |
|---|---|---|---|
| EC1 | 100% statement and branch coverage of the selected business-logic functions (Check.ping, input validation); any uncovered line justified | Functional | P2, P3 |
| EC2 | Every allowed state change and at least one disallowed change from each state tested and passing; 0 open Critical or High defects on status handling | Functional | P2 (highest product risk) |
| EC3 | All boundary tests for timeout and grace pass; repeated create makes 0 duplicates | Functional | P1, P4 |
| EC4 | Ping operation: p95 at most 500 ms and fewer than 1% unexpected failures with 5 users (limits to be justified later) | Performance | P7 |
| EC5 | 4 of 4 role access checks match the access matrix; 0 unresolved High findings in the dependency audit | Security | P5, P9 |

Suspension: environment or database cannot be reset, or the app does not start. Resumption: reset script runs and the smoke test (create check, ping, read back) passes.
