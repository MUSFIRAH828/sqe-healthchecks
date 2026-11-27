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
| FR6 | Success ping gives 200, sets last_ping, status up, n_pings + 1 | P2 | test_check_ping: test_success_ping_moves_new_check_to_up | Planned (ping API tests) | UC2 planned | Done (U) |
| FR7 | Fail ping or exit status 1-255 sets status down | P2 | test_check_ping: test_fail_ping_moves_up_check_to_down | Planned | UC2 planned | Done (U) |
| FR8 | /start does not change status or last_ping | P2 | test_check_ping: test_start_ping_keeps_status_and_last_ping; test_check_ping_branches (rid handling) | Planned | - | Done (U) |
| FR9 | Unknown code 404; exit status above 255 gives 400; invalid rid 400; check unchanged | P2 | - | Planned | UC2 exception flows planned | Planned |
| FR10 | Each accepted ping is logged | P2 | test_check_ping: test_every_ping_is_logged | Planned | - | Done (U) |
| FR11 | Listing checks shows updated status, last_ping, n_pings | P2 | - | Planned (read back after ping) | UC2 planned | Planned |
| BR1 | Timeout and grace between 60 and 31,536,000 s inclusive | P1 | test_spec_validation: boundaries (59, 60, 61, 31,535,999, 31,536,000, 31,536,001) | test_timeout_boundaries; test_grace_boundaries | - | Done |
| BR2 | Ping ignored when paused AND manual_resume | P3 | test_ping_mcc: test_d1_* (MCC); test_check_ping: paused tests | Planned | - | Done (U) |
| BR3 | Status changes: new to up, up to down, down to up; up to grace to down over time | P2 | test_get_status_paths (8 basis paths); test_check_status; test_check_ping | Planned | - | Done (U) |
| BR4 | Only a read-write key can create checks; key length 32; per-account check limit | P5 | test_api_authorization (all) | test_missing_api_key_is_rejected; test_read_only_key_cannot_create | Role checks planned | Done (U, A) |
| BR5 | Ping code must exist (404); rid must be a valid UUID (400) | P2 | - | Planned | - | Planned |

## Requirements coverage (update at each step)
- Functional requirements with at least one passing test: FR1 to FR8 and FR10 = 9 of 11 = 82%.
- Business rules with at least one passing test: BR1 to BR4 = 4 of 5 = 80%.
- Open: FR9, FR11 and BR5 wait for the ping API tests.
