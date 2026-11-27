"""More unit tests for Check.ping(): start/rid handling, body storage, pruning.

These close the remaining statement and branch gaps of Check.ping().
Decision "len(body) > 100 and settings.S3_BUCKET" is covered with MC/DC pairs:
  - long body + S3 on   -> stored in S3 (True, True)
  - long body + S3 off  -> stored in the database (True, False)
  - short body + S3 on  -> stored in the database (False, True)
"""
from datetime import timedelta as td

import pytest
from django.utils.timezone import now

from hc.api.models import Check, Ping


def send(check, action="success", body=b"", rid=None, ua="unit-test"):
    check.ping("1.2.3.4", "http", "GET", ua, body, action, rid, None)
    check.refresh_from_db()
    return check


def started_check(make_check, rid):
    """An up check that has received a /start ping with the given rid."""
    return make_check(
        status="up",
        last_ping=now() - td(minutes=10),
        last_start=now() - td(minutes=1),
        last_start_rid=rid,
    )


# ---- start and rid handling (statements 525-533) ----------------------------

def test_success_with_matching_rid_records_duration(make_check, new_rid):
    rid = new_rid()
    check = send(started_check(make_check, rid), "success", rid=rid)
    assert check.last_duration is not None
    assert check.last_start is None


def test_success_with_different_rid_keeps_start(make_check, new_rid):
    check = started_check(make_check, new_rid())
    send(check, "success", rid=new_rid())
    assert check.last_duration is None
    assert check.last_start is not None


def test_success_without_rid_clears_start(make_check, new_rid):
    check = send(started_check(make_check, new_rid()), "success", rid=None)
    assert check.last_duration is None
    assert check.last_start is None


def test_fail_with_different_rid_clears_start(make_check, new_rid):
    check = send(started_check(make_check, new_rid()), "fail", rid=new_rid())
    assert check.status == "down"
    assert check.last_start is None


def test_success_without_any_start_has_no_duration(make_check):
    check = send(make_check(status="new"), "success")
    assert check.last_duration is None


# ---- body storage: decision "len(body) > 100 and S3_BUCKET" -------------------

def test_long_body_with_s3_is_uploaded(make_check, settings, monkeypatch):
    settings.S3_BUCKET = "test-bucket"
    calls = []
    monkeypatch.setattr("hc.api.models.put_object", lambda *args: calls.append(args))
    check = make_check(status="new")
    body = b"x" * 101
    send(check, "success", body=body)
    ping = Ping.objects.get(owner=check)
    assert ping.object_size == 101
    assert not ping.body_raw
    assert calls == [(check.code, 1, body)]


def test_long_body_without_s3_is_stored_in_database(make_check, settings):
    settings.S3_BUCKET = None
    check = make_check(status="new")
    send(check, "success", body=b"x" * 101)
    ping = Ping.objects.get(owner=check)
    assert ping.object_size is None
    assert bytes(ping.body_raw) == b"x" * 101


def test_short_body_with_s3_is_stored_in_database(make_check, settings, monkeypatch):
    settings.S3_BUCKET = "test-bucket"
    calls = []
    monkeypatch.setattr("hc.api.models.put_object", lambda *args: calls.append(args))
    check = make_check(status="new")
    send(check, "success", body=b"x" * 100)  # exactly 100 bytes is not "> 100"
    ping = Ping.objects.get(owner=check)
    assert ping.object_size is None
    assert bytes(ping.body_raw) == b"x" * 100
    assert calls == []


# ---- other ping details --------------------------------------------------------

def test_body_with_confirm_word_sets_confirmation_flag(make_check):
    assert send(make_check(), body=b"Please CONFIRM here").has_confirmation_link is True
    assert send(make_check(), body=b"all good").has_confirmation_link is False


def test_user_agent_is_cut_to_200_characters(make_check):
    check = send(make_check(), ua="u" * 250)
    assert len(Ping.objects.get(owner=check).ua) == 200


def test_every_100th_ping_prunes_old_pings(make_check, monkeypatch):
    pruned = []
    monkeypatch.setattr(Check, "prune", lambda self, wait=False: pruned.append(self.code))
    send(make_check(n_pings=98))
    assert pruned == []  # 99th ping
    send(Check.objects.get(n_pings=99))
    assert len(pruned) == 1  # 100th ping
