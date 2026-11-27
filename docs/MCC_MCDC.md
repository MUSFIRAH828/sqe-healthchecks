# MCC and MC/DC for the critical module `Check.ping()` (hc/api/models.py)

Why this module is critical: it changes the shared Check record (status, last_ping, n_pings) and carries the
highest product risks P2 (wrong status after a ping) and P3 (paused handling) in docs/RISK_REGISTER.md.
Cyclomatic complexity (hand count, radon agrees): **17** = 1 + 13 decisions/ternaries + 3 "and"/"or" operators.
SonarQube value: (fill in after step 16): ____

`ping()` has three compound decisions (two conditions each). All other decisions have one condition.
Python stops early at "and"/"or", so the code never evaluates the second condition in some rows; the rows
are still listed because MCC counts every combination of condition values.

## MCC tables (all 4 combinations, all executed by tests in tests/team/unit/test_ping_mcc.py)

### D1: `status == "paused" and manual_resume` (outcome T = the ping is ignored)
| # | paused (A) | manual_resume (B) | Outcome | Test |
|---|---|---|---|---|
| 1 | T | T | T (kind "ign") | test_d1_paused_T_manual_T_ping_is_ignored |
| 2 | T | F | F | test_d1_paused_T_manual_F_ping_is_processed |
| 3 | F | T | F | test_d1_paused_F_manual_T_ping_is_processed |
| 4 | F | F | F | test_d1_paused_F_manual_F_ping_is_processed |

### D2: `action == "fail" or rid is None` (outcome T = the "running" mark is cleared; reached only when a start mark exists and its rid differs)
| # | fail (C1) | rid is None (C2) | Outcome | Test |
|---|---|---|---|---|
| 1 | T | T | T | test_d2_fail_T_ridnone_T_start_mark_cleared |
| 2 | T | F | T | test_d2_fail_T_ridnone_F_start_mark_cleared |
| 3 | F | T | T | test_d2_fail_F_ridnone_T_start_mark_cleared |
| 4 | F | F | F | test_d2_fail_F_ridnone_F_start_mark_kept |

### D3: `len(body) > 100 and settings.S3_BUCKET` (outcome T = the body goes to object storage)
| # | long body (P) | S3 set (Q) | Outcome | Test |
|---|---|---|---|---|
| 1 | T | T | T | test_d3_long_T_s3_T_body_goes_to_object_storage |
| 2 | T | F | F | test_d3_long_T_s3_F_body_stays_in_database |
| 3 | F | T | F | test_d3_long_F_s3_T_body_stays_in_database |
| 4 | F | F | F | test_d3_long_F_s3_F_body_stays_in_database |

## MC/DC pairs taken from the MCC tables
MC/DC needs each condition to change the outcome on its own, with the other condition held fixed.
For n = 2 conditions the smallest set is n + 1 = 3 rows (instead of 4).

| Decision | Condition | Independence pair (rows) | What changes |
|---|---|---|---|
| D1 (A and B) | A paused | rows 1 and 3 (B = T) | outcome T to F |
| D1 | B manual_resume | rows 1 and 2 (A = T) | outcome T to F |
| D2 (C1 or C2) | C1 fail | rows 2 and 4 (C2 = F) | outcome T to F |
| D2 | C2 rid is None | rows 3 and 4 (C1 = F) | outcome T to F |
| D3 (P and Q) | P long body | rows 1 and 3 (Q = T) | outcome T to F |
| D3 | Q S3 set | rows 1 and 2 (P = T) | outcome T to F |

Minimal MC/DC test sets: D1 rows 1, 2, 3. D2 rows 2, 3, 4. D3 rows 1, 2, 3 (row 4 only adds MCC completeness).
All of these rows already exist as automated tests, so the MC/DC set is a subset of the MCC set.
