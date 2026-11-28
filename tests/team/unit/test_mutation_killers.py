"""Tests added after the first mutation run (docs/MUTATION_REPORT.md) to kill surviving mutants.

Each group says which survivors it targets. Survivors that cannot be killed are listed as equivalent
mutants in the report.
"""
import json

import pytest
from pydantic import ValidationError

from hc.accounts.models import Project
from hc.api.models import Check, Flip, Ping
from hc.api.views import Spec, legacy_timezones

CREATE_URL = "/api/v3/checks/"


def validate(data):
    return Spec.model_validate(data, strict=True)


# ---- Group 1: limits of the text fields in Spec (weak boundary tests) -----------------------

FIELD_LIMITS = {
    "desc": 10000,
    "failure_kw": 200,
    "start_kw": 200,
    "subject": 200,
    "subject_fail": 200,
    "success_kw": 200,
    "tags": 500,
    "slug": 100,
    "name": 100,
}


@pytest.mark.parametrize("field,limit", FIELD_LIMITS.items())
@pytest.mark.parametrize("offset,valid", [(-1, True), (0, True), (1, False)])
def test_text_field_length_limits(field, limit, offset, valid):
    value = "a" * (limit + offset)
    if valid:
        assert validate({field: value}).model_dump()[field] == value
    else:
        with pytest.raises(ValidationError):
            validate({field: value})


def cron_of_length(n):
    """A valid cron expression that is exactly n characters long (repeated minute values)."""
    minute = "1" + ",1" * ((n - 9) // 2)
    if (n - 9) % 2:
        minute = "11" + ",1" * ((n - 10) // 2)
    return minute + " * * * *"


@pytest.mark.parametrize("n,valid", [(99, True), (100, True), (101, False)])
def test_schedule_length_limit(n, valid):
    value = cron_of_length(n)
    assert len(value) == n
    if valid:
        assert validate({"schedule": value}).schedule == value
    else:
        with pytest.raises(ValidationError):
            validate({"schedule": value})


# ---- Group 2: the "unique" list (the word "grace" was never used) ----------------------------

@pytest.mark.parametrize("word", ["name", "slug", "tags", "timeout", "grace"])
def test_every_allowed_unique_word_is_accepted(word):
    assert validate({"unique": [word]}).unique == [word]


# ---- Group 3: timezone and schedule validators (never tested before) ---------------------------

def test_canonical_timezone_is_accepted_unchanged():
    assert validate({"tz": "Europe/Paris"}).tz == "Europe/Paris"


def test_legacy_timezone_is_replaced_by_the_current_name():
    old, new = next(iter(legacy_timezones.items()))
    assert validate({"tz": old}).tz == new


def test_unknown_timezone_is_rejected():
    with pytest.raises(ValidationError):
        validate({"tz": "Mars/Base"})


@pytest.mark.parametrize("expr", ["* * * * *", "0 0 29 2 *", "*/10 8-18 * * 1-5"])
def test_valid_cron_expressions_are_accepted(expr):
    assert validate({"schedule": expr}).schedule == expr


@pytest.mark.parametrize("expr", ["61 * * * *", "0 0 30 2 *"])
def test_invalid_or_impossible_cron_is_rejected(expr):
    with pytest.raises(ValidationError):
        validate({"schedule": expr})


@pytest.mark.parametrize("expr", ["hourly", "Mon *-*-* 09:00:00", "2000-01-02"])
def test_valid_oncalendar_expressions_are_accepted(expr):
    assert validate({"schedule": expr}).schedule == expr


@pytest.mark.parametrize("expr", ["not a schedule", "2000-01-01"])
def test_invalid_or_past_oncalendar_is_rejected(expr):
    with pytest.raises(ValidationError):
        validate({"schedule": expr})


# ---- Group 4: Check.get_grace_start for oncalendar checks that are not up ----------------------

def test_oncalendar_check_that_is_not_up_has_no_grace_start(make_check):
    assert make_check(status="new", kind="oncalendar", schedule="hourly").get_grace_start() is None


def test_cron_check_that_is_not_up_has_no_grace_start(make_check):
    assert make_check(status="new", kind="cron", schedule="* * * * *").get_grace_start() is None


# ---- Group 5: what Check.ping records (Flip reason and Ping kind) -------------------------------

def ping(check, action):
    check.ping("1.2.3.4", "http", "GET", "ua", b"", action, None, None)
    check.refresh_from_db()


def test_start_ping_is_logged_with_kind_start(make_check):
    check = make_check(status="new")
    ping(check, "start")
    assert Ping.objects.get(owner=check).kind == "start"


def test_failure_that_takes_check_down_records_a_flip_with_reason_fail(make_check):
    check = make_check(status="up")
    ping(check, "fail")
    flip = Flip.objects.get(owner=check)
    assert (flip.old_status, flip.new_status, flip.reason) == ("up", "down", "fail")


def test_recovery_records_a_flip_with_an_empty_reason(make_check):
    check = make_check(status="down")
    ping(check, "success")
    flip = Flip.objects.get(owner=check)
    assert (flip.old_status, flip.new_status, flip.reason) == ("down", "up", "")


def test_ping_that_keeps_the_status_records_no_flip(make_check):
    check = make_check(status="up")
    ping(check, "success")
    assert Flip.objects.filter(owner=check).count() == 0


# ---- Group 6: API key handling (read-only flag) and strict input validation ---------------------

@pytest.fixture
def keys(project):
    rw = project.set_api_key()
    ro = project.set_api_key_readonly()
    project.save()
    project.checks_made = Check.objects.create(project=project, name="listed check")
    return {"rw": rw, "ro": ro}


def test_create_response_shows_ping_url_and_uuid(client, keys):
    r = client.post(CREATE_URL, json.dumps({"name": "x"}), content_type="application/json", HTTP_X_API_KEY=keys["rw"])
    assert r.status_code == 201
    assert "ping_url" in r.json() and "uuid" in r.json()


def test_read_write_key_sees_ping_url_and_uuid_when_listing(client, keys):
    listed = client.get(CREATE_URL, HTTP_X_API_KEY=keys["rw"]).json()["checks"][0]
    assert "ping_url" in listed and "uuid" in listed


def test_read_only_key_does_not_see_ping_url_or_uuid_when_listing(client, keys):
    listed = client.get(CREATE_URL, HTTP_X_API_KEY=keys["ro"]).json()["checks"][0]
    assert "ping_url" not in listed and "uuid" not in listed


def test_legacy_plain_text_read_only_key_is_still_read_only(client, project):
    legacy_key = "l" * 32
    project.api_key_readonly = legacy_key
    project.save()
    Check.objects.create(project=project, name="legacy listed")
    listed = client.get(CREATE_URL, HTTP_X_API_KEY=legacy_key).json()["checks"][0]
    assert "ping_url" not in listed and "uuid" not in listed


def test_api_rejects_a_timeout_sent_as_text(client, keys, project):
    r = client.post(
        CREATE_URL, json.dumps({"name": "text timeout", "timeout": "3600"}),
        content_type="application/json", HTTP_X_API_KEY=keys["rw"],
    )
    assert r.status_code == 400
    assert not Check.objects.filter(project=project, name="text timeout").exists()
