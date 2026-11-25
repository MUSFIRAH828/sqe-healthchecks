# Test basis (DRAFT v1) - Healthchecks, Checks module

Baseline: c1039ad23395162c5e2f17d324d8ccdaa60a1d14. Source of expected behaviour: the code
(hc/api/models.py, hc/api/views.py, hc/front/forms.py, hc/accounts/models.py) and a manual
probe of the running API on the baseline. Items marked [verify] were read from code but not yet tested.

## Workflows
| | Workflow 1: Create check | Workflow 2: Ping check |
|---|---|---|
| Start | Project exists, user has write access | Check exists (any status) |
| Action | POST /api/v3/checks/ (or "Add Check" in UI) with name, timeout, grace | GET/POST /ping/<uuid>[/start or /fail or /<exit status>] |
| Expected | 201, check stored with status "new", ping_url returned | 200 "OK", status and last_ping updated, ping logged |

Shared record: the Check row (status, last_ping, n_pings, timeout, grace). Workflow 1 creates it, workflow 2 changes it.

## Functional requirements
Workflow 1 (create)
- FR1 A user with write access can create a check with name, timeout and grace; response is 201 with uuid and ping_url.
- FR2 A new check has status "new", no last_ping and n_pings = 0.
- FR3 Timeout and grace are validated (BR1); an invalid value gives 400 with an error message and nothing is stored.
- FR4 If timeout and grace are omitted, defaults apply (1 day and 1 hour, DEFAULT_TIMEOUT / DEFAULT_GRACE).
- FR5 Repeating a create request with "unique": ["name"] returns the existing check (200); no duplicate is created.
Workflow 2 (ping)
- FR6 A success ping returns 200 "OK", sets last_ping, sets status "up" and increases n_pings by 1.
- FR7 A fail ping (/fail, or exit status 1 to 255) sets status "down".
- FR8 /start records that a run started and does not change status or last_ping.
- FR9 Unknown code gives 404, exit status above 255 gives 400, invalid rid gives 400; the check is unchanged.
- FR10 Each accepted ping is written to the ping log (kind, time) [verify].
Cross-workflow
- FR11 GET /api/v3/checks/ shows the updated status, last_ping and n_pings after a ping.

## Business rules
- BR1 (boundary) timeout and grace are each between 60 and 31,536,000 seconds inclusive.
  Probed: 59 gives 400 "too small", 60 gives 201, 31,536,000 gives 201, 31,536,001 gives 400 "too large".
- BR2 (decision, two conditions) a ping is ignored when status is "paused" AND manual_resume is true [verify].
  If manual_resume is false, a ping on a paused check returns it to "up" (probed).
- BR3 (state change) allowed: new -> up (success ping), up -> down (fail ping), down -> up (success ping),
  up -> paused (pause), paused -> up (resume or ping). Disallowed: resume on a check that is not paused gives 409 (probed);
  a ping with exit status above 255 gives 400 and leaves the status as it was (probed).
- BR4 (permission) only roles with write access can create checks; read-only access cannot.
  Probed: a missing or read-only API key on create gives 401.
- BR5 (input validity) the ping code must exist (404) and rid must be a valid UUID (400).

## Roles
| Role | Create check | Ping | Read checks |
|---|---|---|---|
| Member (role w, write API key) | yes | yes | yes |
| Read-only (role r, read-only API key) | no (401) | yes (the ping URL needs no login) | yes (200) |
Seeded accounts: owner@, member@, viewer@example.com (see docs/SETUP.md).

## Things already noticed (candidates for the weakness report)
- Creating with an empty JSON body succeeds (201) and uses defaults.
- A read-only key gets 401 on create; 403 would normally be expected for "known user, not allowed".
- Anyone with the ping URL can ping; no authentication is needed.
