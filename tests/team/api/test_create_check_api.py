"""API tests for workflow 1 (create a check): POST /api/v3/checks/.

Covers FR1 to FR5, BR1 (boundaries) and BR4 (permission).
Every test reads the shared records back after the request (success and rejection).
"""
import pytest

TIMEOUT_CASES = [
    # (value, expected status code)   3-point BVA on both limits: below, at, above
    (59, 400),
    (60, 201),
    (61, 201),
    (31_535_999, 201),
    (31_536_000, 201),
    (31_536_001, 400),
]


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


@pytest.mark.parametrize("timeout,expected", TIMEOUT_CASES)
def test_timeout_boundaries(api, unique_name, timeout, expected):
    before = len(api.list_checks())
    r = api.create({"name": unique_name("bva-timeout"), "timeout": timeout, "grace": 3600})
    assert r.status_code == expected
    after = api.list_checks()
    if expected == 201:
        assert api.get_check(r.json()["uuid"]).json()["timeout"] == timeout
        assert len(after) == before + 1
    else:
        assert "timeout" in r.json()["error"]
        assert len(after) == before  # nothing was stored


@pytest.mark.parametrize("grace,expected", TIMEOUT_CASES)
def test_grace_boundaries(api, unique_name, grace, expected):
    before = len(api.list_checks())
    r = api.create({"name": unique_name("bva-grace"), "timeout": 3600, "grace": grace})
    assert r.status_code == expected
    after = api.list_checks()
    if expected == 201:
        assert api.get_check(r.json()["uuid"]).json()["grace"] == grace
        assert len(after) == before + 1
    else:
        assert "grace" in r.json()["error"]
        assert len(after) == before


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
def test_name_length_boundary(api, unique_name):
    valid_name = "a" * 100
    invalid_name = "b" * 101

    valid_response = api.create({
        "name": valid_name,
        "timeout": 3600,
    })
    invalid_response = api.create({
        "name": invalid_name,
        "timeout": 3600,
    })

    assert valid_response.status_code == 201
    assert invalid_response.status_code == 400
