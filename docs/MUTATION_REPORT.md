# Mutation testing report (DRAFT: numbers from a sandbox run, replace with the GitHub Actions run)

Tool: Cosmic Ray 8.9 (Python). Run on Linux only (GitHub Actions job "mutation"; the author's Windows laptop has no WSL).
Module under test (business rules): Check.get_grace_start, Check.going_down_after, Check.get_status, Check.ping (hc/api/models.py),
Spec and create_check (hc/api/views.py), authorize and authorize_read (hc/api/decorators.py).
Tests that must kill mutants: tests/team/unit (the API tests need a server and are not used here).
Config: tests/team/mutation/cosmic-ray.toml. Scope filter: tests/team/mutation/scope_filter.py. Report/gate: tests/team/mutation/report.py.

## How to run (Linux, WSL or CI)
```
pip install cosmic-ray ./tests/team/mutation/operators
cosmic-ray init tests/team/mutation/cosmic-ray.toml session.sqlite
cr-filter-operators session.sqlite tests/team/mutation/cosmic-ray.toml
python tests/team/mutation/scope_filter.py session.sqlite
cosmic-ray baseline tests/team/mutation/cosmic-ray.toml
cosmic-ray exec tests/team/mutation/cosmic-ray.toml session.sqlite
python tests/team/mutation/report.py session.sqlite --min-score 90
```

## Result
| Run | Mutants run | Killed | Survived | Score |
|---|---|---|---|---|
| 1: tests before this analysis (108 unit tests) | 264 | 195 | 69 | 73.9% |
| 2: after adding the tests in test_mutation_killers.py (167 unit tests) | 264 | 257 | 7 | 97.3% |
All 7 remaining survivors are equivalent mutants, so every killable mutant is killed (257 of 257 = 100% of the killable ones).
Raw output: docs/mutation/run1_before_new_tests.txt, run2_after_new_tests.txt. Full table of the 69 survivors: docs/mutation/survivor_analysis.md.
Note: cr-report prints a score over all 4,162 generated mutants, because the 3,898 mutants outside the scope are marked "skipped" and
counted as complete. That figure (1.66% surviving) is not the score; the score above uses only mutants that really ran.

## Custom operators (written for the business rules, tests/team/mutation/operators)
| Operator | Rule | What it does | Mutants (run 1: killed / survived) |
|---|---|---|---|
| hc/HcStatusSwap | BR3 state change | Replaces a status word ("up", "down", "new", "grace", "paused", "started") with a wrong one | 33 / 2 |
| hc/HcActionSwap | BR2, BR3 ping kind | Replaces a ping kind ("success", "fail", "start", "log", "ign") with another kind | 14 / 6 |
| hc/HcLimitShift | BR1 boundary | Moves a limit (60, 100, 200, 500, 31,536,000) by +1 or -1 | 19 / 15 |
After the new tests all 89 custom mutants are killed (run 2).

## Survivor analysis (summary of all 69; details in survivor_analysis.md)
| Category | Count | Meaning | Action |
|---|---|---|---|
| Missing test | 51 | No test reached the code (text field limits, timezone and schedule validators, oncalendar not up) | New tests added, all killed |
| Weak assertion | 11 | A test ran the code but did not check the result (flip reason, ping kind, read-only flag, strict validation through the API) | Assertions added, all killed |
| Equivalent | 7 | No test can tell the mutant from the original (dead assignment of request.readonly, any float fails strict validation, date anchor 2000-01-01 of the schedule check) | Kept, explained |

Examples (full list in survivor_analysis.md):
1. models.py:537 `reason = "fail" if action == "fail" else ""` mutated to `reason = "success" ...`: the reason saved in the Flip record was never asserted (weak assertion). Killed by test_failure_that_takes_check_down_records_a_flip_with_reason_fail.
2. models.py:550 the ping kind list lost "start": no test read the kind of a /start ping. Killed by test_start_ping_is_logged_with_kind_start.
3. decorators.py:88 `or` changed to `and` in the read-only test: tests only looked at the status code. Killed by test_read_only_key_does_not_see_ping_url_or_uuid_when_listing.
4. views.py:79 tags limit 500 changed to 501: only the invalid side (501) was tested. Killed by test_text_field_length_limits (499, 500, 501).
5. views.py:82 the word "grace" removed from the unique list: never used. Killed by test_every_allowed_unique_word_is_accepted.
6. views.py:92 `data[k] = 0.0` changed to `1.0`: equivalent, any float fails strict type validation.

## Pipeline evidence still to collect
Mutation job log and artifact (mutation_report.txt) from GitHub Actions; the blocked pull request (see docs/CI_SETUP.md).
