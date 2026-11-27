"""API tests for workflow 2 (ping a check): GET/POST /ping/<uuid>[/start|/fail|/<exit status>].

Input values come from the test data generator (docs/openapi.yaml). After every request the
check is read back through the API (status, n_pings, last_ping).
Covers FR6 to FR11, BR2, BR3 and BR5.
"""
import uuid

import pytest

from tests.team.generator.generator import get_cases


def case_id(c):
    return f'{c["technique"]}-{c["group"]}-{str(c["value"])[:14]}'


# ---- FR6, FR7, FR8: what each kind of ping does ---------------------------------

def test_success_ping_sets_up_and_last_ping(api, new_check):
    r = api.ping(new_check)
    assert r.status_code == 200 and r.text == "OK"
    status, n_pings, last_ping = api.state(new_check)
    assert (status, n_pings) == ("up", 1)
    assert last_ping is not None


def test_fail_ping_sets_down(api, new_check):
    api.ping(new_check)  # up first
    assert api.ping(new_check, "/fail").status_code == 200
    assert api.state(new_check)[:2] == ("down", 2)


def test_start_ping_keeps_status_new_and_counts_one_ping(api, new_check):
    assert api.ping(new_check, "/start").status_code == 200
    status, n_pings, last_ping = api.state(new_check)
    assert (status, n_pings, last_ping) == ("new", 1, None)


# ---- FR9: exit status (generated: EP and 3-point BVA on 0..255) -------------------

@pytest.mark.parametrize("case", get_cases("get /ping/{uuid}/{exitstatus}", "exitstatus"), ids=case_id)
def test_exit_status_cases(api, new_check, case):
    r = api.ping(new_check, f"/{case['value']}")
    status, n_pings, _ = api.state(new_check)
    if case["valid"]:
        assert r.status_code == 200
        assert status == ("up" if case["value"] == 0 else "down")
        assert n_pings == 1
    else:
        assert r.status_code in (400, 404)  # above 255 gives 400; -1 and text give 404
        assert (status, n_pings) == ("new", 0)  # the check is unchanged


# ---- FR9, BR5: rid (generated) and the check code ----------------------------------

@pytest.mark.parametrize("case", get_cases("get /ping/{uuid}", "rid"), ids=case_id)
def test_rid_cases(api, new_check, case):
    r = api.ping(new_check, f"?rid={case['value']}")
    n_pings = api.state(new_check)[1]
    if case["valid"]:
        assert r.status_code == 200 and n_pings == 1
    else:
        assert r.status_code == 400 and n_pings == 0


@pytest.mark.parametrize("code", [str(uuid.uuid4()), "not-a-uuid"], ids=["unknown-uuid", "malformed-uuid"])
def test_unknown_check_code_gives_404_and_changes_nothing(api, new_check, code):
    before = len(api.list_checks())
    assert api.ping(code).status_code == 404
    assert api.state(new_check)[1] == 0
    assert len(api.list_checks()) == before


# ---- FR10, FR11: repeated and alternative requests ------------------------------------

def test_repeated_pings_are_each_counted_and_make_no_duplicate_check(api, new_check):
    before = len(api.list_checks())
    api.ping(new_check)
    api.ping(new_check)
    assert api.state(new_check)[:2] == ("up", 2)
    assert len(api.list_checks()) == before


def test_post_ping_with_body_is_accepted(api, new_check):
    assert api.ping(new_check, method="POST", data="job finished").status_code == 200
    assert api.state(new_check)[:2] == ("up", 1)


def test_ping_is_visible_to_the_read_only_key_after_create(api, unique_name):
    name = unique_name("cross")
    created = api.create({"name": name, "timeout": 3600}).json()  # workflow 1
    api.ping(created["uuid"])  # workflow 2
    listed = [c for c in api.list_checks("ro") if c["name"] == name]  # read back, other role
    assert len(listed) == 1
    assert listed[0]["status"] == "up"
    assert listed[0]["n_pings"] == 1
    # Security control: a read-only key must not reveal the ping address of a check.
    assert "uuid" not in listed[0]
    assert "ping_url" not in listed[0]


# ---- BR3, BR2: state transitions ---------------------------------------------------------

def test_status_moves_new_up_down_up(api, new_check):
    assert api.state(new_check)[0] == "new"
    api.ping(new_check)
    assert api.state(new_check)[0] == "up"
    api.ping(new_check, "/fail")
    assert api.state(new_check)[0] == "down"
    api.ping(new_check)
    assert api.state(new_check)[0] == "up"


def test_pause_then_ping_returns_check_to_up(api, new_check):
    api.ping(new_check)
    assert api.post_action(new_check, "pause").status_code == 200
    assert api.state(new_check)[0] == "paused"
    api.ping(new_check)  # manual_resume is off by default
    assert api.state(new_check)[0] == "up"


def test_resume_of_paused_check_gives_new_and_clears_last_ping(api, new_check):
    api.ping(new_check)
    api.post_action(new_check, "pause")
    assert api.post_action(new_check, "resume").status_code == 200
    status, _, last_ping = api.state(new_check)
    assert (status, last_ping) == ("new", None)


def test_resume_of_a_check_that_is_not_paused_is_rejected(api, new_check):
    api.ping(new_check)
    assert api.post_action(new_check, "resume").status_code == 409
    assert api.state(new_check)[0] == "up"  # unchanged


def test_read_only_key_cannot_pause(api, new_check):
    api.ping(new_check)
    assert api.post_action(new_check, "pause", key="ro").status_code == 401
    assert api.state(new_check)[0] == "up"


def test_pause_of_unknown_check_gives_404(api):
    assert api.post_action(str(uuid.uuid4()), "pause").status_code == 404
