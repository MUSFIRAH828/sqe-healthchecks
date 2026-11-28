# Requirements Traceability Matrix — Healthchecks

**Course:** SE3002 Software Quality Engineering  
**Project:** Automated Testing of Healthchecks  
**Selected workflows:** Create Check and Ping Check

## 1. Purpose

This matrix links the functional requirements recorded in the project scope to planned or existing test cases. It helps identify requirements that have no test coverage and makes test progress traceable.

**Status meanings:**

- **Existing — reported:** The project report already describes relevant test coverage or execution.
- **To implement/verify:** A test ID is proposed for the remaining API, integration, or end-to-end work. It must not be marked passed until executed.
- **Verify mapping:** Confirm the exact test filename and assertion in the repository before final submission.

## 2. Requirements-to-test mapping

| Requirement ID | Requirement (from project scope) | Test ID(s) | Test level | Current mapping status |
|---|---|---|---|---|
| FR1 | A user with write permission can create a check. | TC-API-001, TC-E2E-001 | API, E2E | To implement/verify |
| FR2 | A newly created check has the expected initial status, no last ping, and zero ping count. | TC-API-002, TC-INT-001 | API, Integration | To implement/verify |
| FR3 | Timeout and grace values are validated against the supported range. | TC-API-003, TC-API-004 | API | To implement/verify; boundary logic also appears in the reported business-rule tests |
| FR4 | Default values are applied when optional values are omitted. | TC-API-005 | API | To implement/verify |
| FR5 | Duplicate check-name behavior follows the application's implemented rule. | TC-API-006, TC-INT-002 | API, Integration | To implement/verify |
| FR6 | A successful ping updates the check's status and last-ping information. | TC-UNIT-001, TC-API-007, TC-INT-003 | Unit, API, Integration | Existing unit coverage reported; API/integration to implement/verify |
| FR7 | A failure ping moves the check to the expected down state. | TC-UNIT-002, TC-API-008 | Unit, API | Existing business-rule coverage reported; endpoint test to implement/verify |
| FR8 | A start ping records the start information as required. | TC-API-009, TC-INT-004 | API, Integration | To implement/verify |
| FR9 | Invalid ping codes, invalid identifiers, and invalid state operations are rejected as specified. | TC-UNIT-003, TC-API-010, TC-API-011 | Unit, API | Existing selected business-rule coverage reported; endpoint mapping to verify |
| FR10 | Accepted ping requests are recorded in the ping history/log. | TC-API-012, TC-INT-005 | API, Integration | To implement/verify |
| FR11 | The checks listing/read operation returns the stored check information. | TC-API-013, TC-INT-006 | API, Integration | To implement/verify |

## 3. Test case catalogue

The following IDs are the proposed traceability identifiers. Link each ID to the actual test function/file when it is implemented.

| Test ID | Test description | Expected result |
|---|---|---|
| TC-API-001 | Create a check using a valid write API key and valid input. | Successful creation response and check identifier/ping URL. |
| TC-API-002 | Read a newly created check's initial values. | Initial status, last-ping value, and ping count match the documented application behavior. |
| TC-API-003 | Submit timeout/grace values below the minimum. | Validation rejects the invalid value. |
| TC-API-004 | Submit minimum, maximum, and above-maximum timeout/grace values. | Boundary values are accepted/rejected according to the implemented inclusive limits. |
| TC-API-005 | Omit optional fields during check creation. | Application applies its documented defaults. |
| TC-API-006 | Submit a check name that duplicates an existing name in the relevant scope. | Application follows its implemented duplicate-name behavior. |
| TC-API-007 | Send a successful ping to a valid check. | Check is updated according to the success-ping rule. |
| TC-API-008 | Send a failure ping to a valid check. | Check enters the expected failure/down state. |
| TC-API-009 | Send a start ping to a valid check. | Start information is recorded as implemented. |
| TC-API-010 | Send a request with an invalid check identifier. | Application returns the documented invalid-identifier response. |
| TC-API-011 | Send an unsupported ping code or invalid state operation. | Application rejects the request without an unintended state change. |
| TC-API-012 | Send an accepted ping and inspect its history/log. | The accepted ping is recorded. |
| TC-API-013 | Read the checks list after creation and ping update. | Stored check information is returned consistently. |
| TC-INT-001 | Create a check, then read the persisted database record. | The same check and its initial values are present. |
| TC-INT-002 | Repeat check creation using a duplicate name. | No unintended duplicate is created; actual application rule is respected. |
| TC-INT-003 | Create a check, ping it, then read the same record. | The shared Check record reflects the ping update. |
| TC-INT-004 | Create a check and send a start ping. | Start-related data is persisted as implemented. |
| TC-INT-005 | Send a valid ping and inspect the associated ping history. | The expected ping record exists. |
| TC-INT-006 | Read the check after a successful and a rejected operation. | Persisted state matches the expected outcome; rejected operation does not cause an unintended update. |
| TC-E2E-001 | Create a check through the browser interface. | User sees successful creation and the check appears in the interface. |

## 4. Coverage tracking

Update this table after executing the corresponding tests.

| Requirement | Linked test IDs | Executed? | Result | Evidence / issue |
|---|---|---|---|---|
| FR1 | TC-API-001, TC-E2E-001 | Not recorded here | Not recorded | Add run/PR reference |
| FR2 | TC-API-002, TC-INT-001 | Not recorded here | Not recorded | Add run/PR reference |
| FR3 | TC-API-003, TC-API-004 | Not recorded here | Not recorded | Add run/PR reference |
| FR4 | TC-API-005 | Not recorded here | Not recorded | Add run/PR reference |
| FR5 | TC-API-006, TC-INT-002 | Not recorded here | Not recorded | Add run/PR reference |
| FR6 | TC-UNIT-001, TC-API-007, TC-INT-003 | Unit coverage reported; API/integration not recorded | Partial evidence | Add exact test references |
| FR7 | TC-UNIT-002, TC-API-008 | Unit coverage reported; API not recorded | Partial evidence | Add exact test references |
| FR8 | TC-API-009, TC-INT-004 | Not recorded here | Not recorded | Add run/PR reference |
| FR9 | TC-UNIT-003, TC-API-010, TC-API-011 | Unit coverage reported; API not recorded | Partial evidence | Add exact test references |
| FR10 | TC-API-012, TC-INT-005 | Not recorded here | Not recorded | Add run/PR reference |
| FR11 | TC-API-013, TC-INT-006 | Not recorded here | Not recorded | Add run/PR reference |

## 5. Traceability maintenance

- Every functional requirement should map to at least one test case.
- Every executed test should have a recorded result and evidence reference.
- Failed tests should link to a GitHub issue where a defect is confirmed.
- If a requirement changes, review its linked test cases.
- Remove or rename proposed test IDs if the final implementation uses different IDs.
- Do not mark proposed tests as passed until their execution output has been reviewed.
