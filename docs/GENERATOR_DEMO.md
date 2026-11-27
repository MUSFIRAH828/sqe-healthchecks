# Test data generator: how it works and the effect of changing two constraints

Generator: tests/team/generator/generator.py. Input: docs/openapi.yaml. Output: generated_cases.json.
The API tests (test_create_check_api.py, test_ping_api.py) call get_cases(), so they always use the generator's data.

## What it generates (baseline spec: 83 cases)
| Input | Technique | Values |
|---|---|---|
| timeout, grace (integer 60..31,536,000) | EP | valid middle value, below range, above range, text, decimal, null |
| | 3-point BVA | 59, 60, 61 and 31,535,999, 31,536,000, 31,536,001 |
| name (text, max 100) and tags (text, max 500) | EP + BVA | valid text, wrong type; max - 1, max, max + 1 |
| unique (list of allowed words) | EP | each allowed word alone, unknown word, text instead of list |
| exitstatus (integer 0..255, in the URL) | EP + BVA | valid middle, below, above, text; -1, 0, 1 and 254, 255, 256 |
| rid, uuid (UUID text) | EP | one valid value, too short, plain text, one bad character |

## Demo: change two constraints, regenerate, see the effect
Run from the repository root (virtual environment active, app running and seeded for the test run).
1. `python tests/team/generator/generator.py`   (writes generated_cases.json: 83 cases)
2. `git add tests/team/generator/generated_cases.json` and commit it (this is the "before").
3. In docs/openapi.yaml change TWO constraints: `timeout.minimum` from 60 to 120, and `name.maxLength` from 100 to 50.
4. `python tests/team/generator/generator.py` again, then `git diff tests/team/generator/generated_cases.json`.

Effect on the generated boundary values (what the generator produced when this was tried):
| Input | Before | After |
|---|---|---|
| timeout, around the minimum | 59 (invalid), 60, 61 (valid) | 119 (invalid), 120, 121 (valid) |
| timeout, "below minimum" class | 50 (invalid) | 110 (invalid) |
| name, around the maximum | 99, 100 (valid), 101 (invalid) | 49, 50 (valid), 51 (invalid) |
The number of cases stays 83; only the values and their expected results move.

5. Run the API tests against the unchanged application: `python -m pytest tests/team/api -q`.
Result when tried: 3 failed, 72 passed. The failures are
- test_timeout_cases for "EP below minimum 110" and "BVA minimum - 1 = 119": the spec now says these are invalid, but the application still accepts them (its real minimum is 60);
- test_name_cases for "BVA maximum + 1 = 51 characters": the spec says invalid, the application still accepts it (its real maximum is 100).
Meaning: the tests now describe the new spec, so they find that the application does not match it. To make them pass again, either change the application's limits (hc/api/views.py, class Spec) or restore the spec.
6. Restore: `git checkout docs/openapi.yaml`, then regenerate.

## Viva live-task practice
- "The updated spec says grace maximum is 86,400": regenerate, predict that the BVA cases 86,399 / 86,400 / 86,401 replace the old maximum cases; the application still accepts 86,401, so test_grace_cases for "maximum + 1" and "above maximum" fail.
- "Business rule changes: minimum timeout is 120 in the code": unit tests test_timeout_and_grace_boundaries (59/60/61 cases) fail first, then API tests test_timeout_cases; the CI gate fails on tests before it reaches mutation or Sonar.
