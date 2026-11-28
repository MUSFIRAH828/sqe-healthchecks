# Software Test Plan — Healthchecks

**Course:** SE3002 Software Quality Engineering  
**Project:** Automated Testing of Healthchecks  
**Section:** SE-B  
**Instructor:** Dr. Nigar Azhar Butt  
**Repository:** https://github.com/MUSFIRAH828/sqe-healthchecks  
**Upstream project:** https://github.com/healthchecks/healthchecks  
**Baseline commit:** `c1039ad23395162c5e2f17d324d8ccdaa60a1d14`

## 1. Purpose

This test plan defines the testing activities for the selected Healthchecks workflows: creating a check and sending a ping to an existing check. The goal is to verify expected application behavior, input validation, state changes, permissions, persistence, and the interaction between the two workflows.

## 2. Test objectives

- Verify that a check can be created with valid input.
- Verify that newly created checks have the expected initial values.
- Verify timeout and grace-period validation against the limits implemented by the application.
- Verify that valid ping requests update the associated check.
- Verify success, failure, start, pause, and resume behavior where supported by the selected implementation.
- Verify that invalid identifiers, invalid ping codes, and unauthorized requests are handled correctly.
- Verify that changes are persisted and can be read back.
- Identify defects and provide repeatable evidence of test execution.

## 3. Scope

### 3.1 In-scope workflows

**Workflow 1 — Create Check**

A user with write permission creates a check through the web interface or the API endpoint `POST /api/v3/checks/`. The system validates the supplied fields, stores the check, and returns the created check details, including its ping URL.

**Workflow 2 — Ping Check**

A client sends a request to `/ping/<uuid>` or a supported ping variant such as `/ping/<uuid>/start` or `/ping/<uuid>/fail`. The system processes the ping, updates the relevant check state and timestamps, and records the ping where applicable.

The two workflows share the same Check record: the create workflow creates it, and the ping workflow subsequently updates it.

### 3.2 Out of scope

The project does not claim complete testing of every feature in Healthchecks. Features unrelated to the selected Create Check and Ping Check workflows are outside this test scope unless they are needed to verify a dependency or access-control rule.

## 4. Test approach

The project uses a combination of the following techniques:

| Test level / technique | Purpose |
|---|---|
| Unit testing | Verify selected server-side business logic in isolation. |
| White-box testing | Apply statement, branch, MCC, and MC/DC coverage to selected logic. |
| API testing | Verify endpoint responses, validation, and permissions. |
| Integration testing | Verify that API operations and database persistence work together. |
| End-to-end testing | Exercise user workflows through a browser using Playwright. |
| Mutation testing | Assess whether tests detect deliberate changes to selected business logic. |
| Static analysis | Inspect code quality and security-related findings using SonarQube. |
| Usability/accessibility testing | Evaluate the selected screens and their keyboard/accessibility behavior. |
| Security testing | Verify role restrictions and inspect the local test application with defensive tools. |
| Performance/recovery testing | Measure selected request behavior and verify recovery in a controlled test environment. |

Only tests that have actually been implemented and executed should be reported as completed.

## 5. Test items and basis

The main test items are:

- Check creation through `POST /api/v3/checks/`.
- Check initial status and default values.
- Timeout and grace-period input validation.
- Duplicate-name behavior, according to the application’s implemented rules.
- Ping processing through `/ping/<uuid>`.
- Success, failure, and start ping variants.
- Invalid ping codes and invalid check identifiers.
- Write and read-only API-key behavior.
- Persistence and read-back of the shared Check record.

The current source-code areas identified for test-basis review are `hc/api/models.py`, `hc/api/views.py`, `hc/front/forms.py`, and `hc/accounts/models.py`. Exact behavior and line references should be confirmed against the checked-out baseline before adding or changing tests.

## 6. Test environment

| Item | Project environment |
|---|---|
| Operating system | Windows (local development environment) |
| Language | Python 3.12 |
| Web framework | Django 6.1 (as recorded in the project setup notes) |
| Database | SQLite test database |
| Browser automation | Playwright |
| Unit/API test framework | pytest / Django test utilities, as configured in the repository |
| Static analysis | SonarQube |
| Mutation testing | mutmut 3.8 |
| CI | GitHub Actions |

Record the exact installed versions used for each final execution in the completion report. If the actual environment differs from this table, update the table to match the environment used for the submitted evidence.

## 7. Test data

Testing uses local synthetic data only. The project setup notes identify `scripts/seed_test_data.py` as the seed script and a test project named `SQE Project`.

Test data should include:

- A member/write API key.
- A read-only API key.
- A newly created check.
- Checks in relevant states for ping/state-transition tests.
- Valid timeout and grace values.
- Values below and above supported boundaries.
- Valid and invalid check identifiers.
- Valid and invalid ping variants/codes.

Do not include real user credentials, production monitoring data, or private service URLs in test fixtures or screenshots.

## 8. Roles and responsibilities

The project has three team members:

| Team member | Roll number | Responsibility |
|---|---|---|
| Musfirah Hamid | 24i3096 | Confirm and enter the tasks personally implemented and committed by this member. |
| Alisha Iqbal | 24i3147 | Confirm and enter the tasks personally implemented and committed by this member. |
| Ayesha Anjum | 24i3171 | Confirm and enter the tasks personally implemented and committed by this member. |

Each member is responsible for reviewing their assigned tests, committing their own contributions, and being able to explain the implementation and results during the viva. Final task ownership must reflect the actual Git history; do not assign work retrospectively if the member did not perform it.

## 9. Test schedule

The exact calendar dates and durations must be completed from the team's actual plan and GitHub history. Do not treat the suggested sequence below as evidence that an activity has already happened.

| Activity | Planned order | Planned duration |
|---|---:|---|
| Test planning and traceability | 1 | To be agreed by team |
| Risk analysis and exit criteria | 2 | To be agreed by team |
| API and integration testing | 3 | To be agreed by team |
| Automated test-data generation | 4 | To be agreed by team |
| Use-case specification | 5 | To be agreed by team |
| Browser automation | 6 | To be agreed by team |
| Mutation testing and CI completion | 7 | To be agreed by team |
| Usability and accessibility | 8 | To be agreed by team |
| Defensive security | 9 | To be agreed by team |
| Performance and recovery | 10 | To be agreed by team |
| Defect analysis and reporting | 11 | To be agreed by team |
| Monitoring and completion report | 12 | To be agreed by team |

## 10. Entry criteria

Testing of a feature may begin when:

- The relevant application code is available in the project repository.
- The local test environment can be configured using the project's setup instructions.
- Required database migrations have been applied.
- Required synthetic test data is available.
- The test case and its expected result have been reviewed.
- Required test tools and dependencies are installed.

## 11. Exit criteria

The project may be considered ready for final review when:

- All planned test cases have an execution status recorded.
- Critical workflow and business-rule tests have passed, or remaining failures are documented and assessed.
- Required coverage, mutation, API, browser, security, and performance evidence has been collected.
- Every requirement in the traceability matrix is linked to one or more test cases, with untested requirements clearly identified.
- Open defects and residual risks are documented.
- The final report accurately distinguishes completed, failed, blocked, and not-executed tests.

The numeric thresholds required by the assignment should be stated in the risk/exit-criteria document and verified against actual test results.

## 12. Suspension and resumption criteria

**Suspend testing when:**

- The application cannot start or the test database is unavailable.
- A test environment failure makes results unreliable.
- A blocking defect prevents execution of dependent test cases.
- Required test data or credentials are unavailable.
- A test risks modifying data outside the local synthetic environment.

**Resume testing when:**

- The environment or dependency has been restored.
- Required data and credentials have been checked.
- The blocking defect has been fixed or a documented workaround has been approved.
- A basic smoke test confirms that the environment is usable.

## 13. Test evidence and reporting

For each test execution, record:

- Test ID and requirement ID.
- Build/commit identifier.
- Environment and tool versions.
- Input data.
- Expected result and actual result.
- Pass, fail, blocked, or not-run status.
- Defect/issue link, if applicable.
- Relevant terminal output, CI run, or screenshot.

Do not report a test as passed unless it was executed and its result was checked.
