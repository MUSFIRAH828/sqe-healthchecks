"""API tests for workflow 1 (create a check): POST /api/v3/checks/.

Input values come from the test data generator (tests/team/generator), which reads docs/openapi.yaml.
Covers FR1 to FR5, BR1 (boundaries) and BR4 (permission).
Every test reads the shared records back after the request (success and rejection).
"""
import pytest

from tests.team.generator.generator import get_cases

OP = "post /api/v3/checks/"


def case_id(c):
    return f'{c["technique"]}-{c["group"]}-{str(c["value"])[:14]}'


def check_create(api, body, param, case):
    """Send the request and verify the outcome and the shared records for one generated case."""
    before = len(api.list_checks())
    r = api.create(body)
    after = api.list_checks()
    if case["valid"]:
        assert r.status_code in (200, 201), r.text
        if param in ("timeout", "grace", "name", "tags"):
            assert api.get_check(r.json()["uuid"]).json()[param] == case["value"]
        assert len(after) == before + 1
    else:
        assert r.status_code == 400, r.text
        assert param in r.json()["error"]
        assert len(after) == before  # nothing was stored


@pytest.mark.parametrize("case", get_cases(OP, "timeout"), ids=case_id)
def test_timeout_cases(api, unique_name, case):
    body = {"name": unique_name("gen-timeout"), "timeout": case["value"], "grace": 3600}
    check_create(api, body, "timeout", case)


@pytest.mark.parametrize("case", get_cases(OP, "grace"), ids=case_id)
def test_grace_cases(api, unique_name, case):
    body = {"name": unique_name("gen-grace"), "timeout": 3600, "grace": case["value"]}
    check_create(api, body, "grace", case)


@pytest.mark.parametrize("case", get_cases(OP, "name"), ids=case_id)
def test_name_cases(api, case):
    check_create(api, {"name": case["value"]}, "name", case)


@pytest.mark.parametrize("case", get_cases(OP, "tags"), ids=case_id)
def test_tags_cases(api, unique_name, case):
    check_create(api, {"name": unique_name("gen-tags"), "tags": case["value"]}, "tags", case)


@pytest.mark.parametrize("case", get_cases(OP, "unique"), ids=case_id)
def test_unique_cases(api, unique_name, case):
    check_create(api, {"name": unique_name("gen-unique"), "unique": case["value"]}, "unique", case)


# ---- other requirements ---------------------------------------------------------

def test_create_check_returns_201_and_check_can_be_read_back(api, unique_name):
    name = unique_name()
    r = api.create({"name": name, "timeout": 3600, "grace": 300})
    assert r.status_code == 201
    body = r.json()
    assert body["ping_url"].endswith(body["uuid"])
    stored = api.get_check(body["uuid"]).json()
    assert stored["name"] == name
    assert stored["timeout"] == 3600
    assert stored["grace"] == 300


def test_new_check_starts_in_new_status_with_no_pings(api, unique_name):
    body = api.create({"name": unique_name(), "timeout": 3600}).json()
    stored = api.get_check(body["uuid"]).json()
    assert stored["status"] == "new"
    assert stored["last_ping"] is None
    assert stored["n_pings"] == 0


def test_omitted_timeout_and_grace_use_defaults(api, unique_name):
    body = api.create({"name": unique_name()}).json()
    stored = api.get_check(body["uuid"]).json()
    assert stored["timeout"] == 86400  # 1 day
    assert stored["grace"] == 3600  # 1 hour


def test_missing_api_key_is_rejected(api, unique_name):
    before = len(api.list_checks())
    r = api.create({"name": unique_name()}, key=None)
    assert r.status_code == 401
    assert len(api.list_checks()) == before


def test_read_only_key_cannot_create(api, unique_name):
    before = len(api.list_checks())
    r = api.create({"name": unique_name()}, key="ro")
    assert r.status_code == 401
    assert len(api.list_checks()) == before


def test_repeated_create_with_unique_name_makes_no_duplicate(api, unique_name):
    body = {"name": unique_name("repeat"), "timeout": 3600, "unique": ["name"]}
    before = len(api.list_checks())
    first = api.create(body)
    second = api.create(body)
    assert first.status_code == 201
    assert second.status_code == 200  # existing check returned
    assert first.json()["uuid"] == second.json()["uuid"]
    assert len(api.list_checks()) == before + 1
