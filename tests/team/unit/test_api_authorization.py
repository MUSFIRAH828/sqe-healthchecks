"""Unit tests for rule BR4 (permission) and the per-account check limit (hc.api.decorators, hc.api.views).

The API key decides what a caller may do:
  - read-write key: may create checks
  - read-only key: may only read (it is treated as an unknown key on write endpoints)
The API key must be exactly 32 characters; any other length is "missing".
A project owner may not create more checks than the profile's check_limit.
"""
import json

import pytest

from hc.accounts.models import Profile
from hc.api.models import Check

CREATE_URL = "/api/v3/checks/"


@pytest.fixture
def keys(project):
    rw = project.set_api_key()
    ro = project.set_api_key_readonly()
    project.save()
    return {"rw": rw, "ro": ro}


def post(client, body, key=None):
    headers = {"HTTP_X_API_KEY": key} if key is not None else {}
    return client.post(CREATE_URL, json.dumps(body), content_type="application/json", **headers)


def test_keys_are_32_characters(keys):
    assert len(keys["rw"]) == 32
    assert len(keys["ro"]) == 32


# ---- write endpoint: authorize -----------------------------------------------------

def test_read_write_key_can_create_a_check(client, keys, project):
    r = post(client, {"name": "from rw key"}, keys["rw"])
    assert r.status_code == 201
    assert Check.objects.filter(project=project, name="from rw key").count() == 1


def test_read_only_key_cannot_create_a_check(client, keys, project):
    r = post(client, {"name": "from ro key"}, keys["ro"])
    assert r.status_code == 401
    assert r.json()["error"] == "wrong api key"
    assert Check.objects.filter(project=project).count() == 0


def test_missing_key_is_rejected(client, project):
    r = post(client, {"name": "no key"})
    assert r.status_code == 401
    assert r.json()["error"] == "missing api key"


@pytest.mark.parametrize("length", [31, 33])
def test_key_with_wrong_length_counts_as_missing(client, project, length):
    r = post(client, {"name": "bad length"}, "k" * length)
    assert r.status_code == 401
    assert r.json()["error"] == "missing api key"


def test_unknown_key_of_correct_length_is_wrong(client, project):
    r = post(client, {"name": "unknown key"}, "k" * 32)
    assert r.status_code == 401
    assert r.json()["error"] == "wrong api key"


def test_key_can_be_sent_inside_the_json_body(client, keys, project):
    r = post(client, {"name": "key in body", "api_key": keys["rw"]})
    assert r.status_code == 201


def test_body_that_is_not_json_is_rejected(client, keys):
    r = client.post(CREATE_URL, "{broken", content_type="application/json", HTTP_X_API_KEY=keys["rw"])
    assert r.status_code == 400
    assert r.json()["error"] == "could not parse request body"


def test_body_that_is_a_json_list_is_rejected(client, keys):
    r = post(client, ["not", "an", "object"], keys["rw"])
    assert r.status_code == 400
    assert "not an object" in r.json()["error"]


# ---- read endpoint: authorize_read ---------------------------------------------------

@pytest.mark.parametrize("which", ["rw", "ro"])
def test_both_keys_can_list_checks(client, keys, which):
    r = client.get(CREATE_URL, HTTP_X_API_KEY=keys[which])
    assert r.status_code == 200


def test_list_without_key_is_rejected(client, project):
    assert client.get(CREATE_URL).status_code == 401


def test_list_with_unknown_key_is_rejected(client, project):
    r = client.get(CREATE_URL, HTTP_X_API_KEY="k" * 32)
    assert r.status_code == 401
    assert r.json()["error"] == "wrong api key"


# ---- check limit per account ---------------------------------------------------------

@pytest.fixture
def limited(project, keys):
    profile = Profile.objects.for_user(project.owner)
    profile.check_limit = 2
    profile.save()
    return profile


def test_creating_checks_up_to_the_limit_is_allowed(client, keys, limited):
    assert post(client, {"name": "one"}, keys["rw"]).status_code == 201  # 1 used, 1 left
    assert post(client, {"name": "two"}, keys["rw"]).status_code == 201  # 2 used, 0 left


def test_creating_a_check_over_the_limit_is_forbidden(client, keys, limited, project):
    post(client, {"name": "one"}, keys["rw"])
    post(client, {"name": "two"}, keys["rw"])
    r = post(client, {"name": "three"}, keys["rw"])
    assert r.status_code == 403
    assert Check.objects.filter(project=project).count() == 2


def test_repeated_unique_request_at_the_limit_returns_existing_check(client, keys, limited, project):
    body = {"name": "same", "unique": ["name"]}
    post(client, body, keys["rw"])
    post(client, {"name": "other"}, keys["rw"])  # now at the limit
    r = post(client, body, keys["rw"])
    assert r.status_code == 200  # the existing check is returned, no new one needed
    assert Check.objects.filter(project=project).count() == 2


def test_post_with_empty_body_and_valid_key_creates_a_default_check(client, keys, project):
    # Weakness candidate: nothing is required, so an empty request still makes a check.
    r = client.post(CREATE_URL, "", content_type="application/json", HTTP_X_API_KEY=keys["rw"])
    assert r.status_code == 201
    assert Check.objects.filter(project=project).count() == 1


def test_invalid_field_value_is_rejected_with_400_and_nothing_is_stored(client, keys, project):
    r = post(client, {"name": "too fast", "timeout": 59}, keys["rw"])
    assert r.status_code == 400
    assert "timeout" in r.json()["error"]
    assert Check.objects.filter(project=project).count() == 0


def test_unknown_channel_is_rejected_with_400_and_nothing_is_stored(client, keys, project):
    r = post(client, {"name": "bad channel", "channels": "no-such-channel"}, keys["rw"])
    assert r.status_code == 400
    assert Check.objects.filter(project=project, name="bad channel").count() == 0
