# Traceability matrix (DRAFT v1) - requirements and business rules to tests

Status: Done = automated test exists and passes; Planned = not written yet. Update this file when tests are added.
Files: U = tests/team/unit, A = tests/team/api, E = tests/team/e2e (browser, planned).

| ID | Requirement or rule | Risk | Unit tests (U) | API tests (A) | Browser (E) | Status |
|---|---|---|---|---|---|---|
| FR1 | Create check with name, timeout, grace gives 201 | - | test_api_authorization: test_read_write_key_can_create_a_check | test_create_check_returns_201_and_check_can_be_read_back | UC1 planned | Done (U, A) |
| FR2 | New check starts as "new", no last_ping, 0 pings | P2 | - | test_new_check_starts_in_new_status_with_no_pings | UC1 planned | Done (A) |
| FR3 | Timeout and grace validated; invalid gives 400, nothing stored | P1 | test_spec_validation: test_timeout_and_grace_boundaries; test_api_authorization: test_invalid_field_value_is_rejected... | test_timeout_boundaries; test_grace_boundaries | UC1 exception flow planned | Done (U, A) |
| FR4 | Omitted timeout and grace use defaults (1 day, 1 hour) | - | test_spec_validation: test_empty_body_is_valid_and_leaves_defaults_unset | test_omitted_timeout_and_grace_use_defaults | - | Done (U, A) |
| FR5 | Repeated create with "unique" makes no duplicate | P4 | test_api_authorization: test_repeated_unique_request_at_the_limit_returns_existing_check | test_repeated_create_with_unique_name_makes_no_duplicate | - | Done (U, A) |
| FR6 | Success ping gives 200, sets last_ping, status up, n_pings + 1 | P2 | test_check_ping: test_success_ping_moves_new_check_to_up | test_success_ping_sets_up_and_last_ping | UC2 planned | Done (U, A) |
| FR7 | Fail ping or exit status 1-255 sets status down | P2 | test_check_ping: test_fail_ping_moves_up_check_to_down | test_fail_ping_sets_down; test_exit_status_cases | UC2 planned | Done (U, A) |
| FR8 | /start does not change status or last_ping | P2 | test_check_ping: test_start_ping_keeps_status_and_last_ping; test_check_ping_branches (rid handling) | test_start_ping_keeps_status_new_and_counts_one_ping | - | Done (U, A) |
| FR9 | Unknown code 404; exit status above 255 gives 400; invalid rid 400; check unchanged | P2 | test_check_ping_branches (rid handling) | test_exit_status_cases; test_rid_cases; test_unknown_check_code_gives_404_and_changes_nothing | UC2 exception flows planned | Done (U, A) |
| FR10 | Each accepted ping is logged | P2 | test_check_ping: test_every_ping_is_logged | test_repeated_pings_are_each_counted_and_make_no_duplicate_check | - | Done (U, A) |
| FR11 | Listing checks shows updated status, last_ping, n_pings | P2 | - | test_ping_is_visible_to_the_read_only_key_after_create; every ping test reads the check back | UC2 planned | Done (A) |
| BR1 | Timeout and grace between 60 and 31,536,000 s inclusive | P1 | test_spec_validation: boundaries (59, 60, 61, 31,535,999, 31,536,000, 31,536,001) | test_timeout_boundaries; test_grace_boundaries | - | Done |
| BR2 | Ping ignored when paused AND manual_resume | P3 | test_ping_mcc: test_d1_* (MCC); test_check_ping: paused tests | test_pause_then_ping_returns_check_to_up | - | Done (U, A) |
| BR3 | Status changes: new to up, up to down, down to up; up to grace to down over time | P2 | test_get_status_paths (8 basis paths); test_check_status; test_check_ping | test_status_moves_new_up_down_up; test_resume_of_paused_check_gives_new_and_clears_last_ping; test_resume_of_a_check_that_is_not_paused_is_rejected | - | Done (U, A) |
| BR4 | Only a read-write key can create checks; key length 32; per-account check limit | P5 | test_api_authorization (all) | test_missing_api_key_is_rejected; test_read_only_key_cannot_create | Role checks planned | Done (U, A) |
| BR5 | Ping code must exist (404); rid must be a valid UUID (400) | P2 | - | test_unknown_check_code_gives_404_and_changes_nothing; test_rid_cases | - | Done (A) |

## Requirements coverage (update at each step)
- Functional requirements with at least one passing test: FR1 to FR11 = 11 of 11 = 100% (unit and API; browser tests still planned).
- Business rules with at least one passing test: BR1 to BR5 = 5 of 5 = 100%.
- Not yet covered: the browser (E) column, filled when the Playwright use case tests exist.
