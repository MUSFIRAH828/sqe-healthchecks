"""Multiple Condition Coverage (MCC) tests for the three compound decisions in Check.ping().

D1: status == "paused"  and  manual_resume          (BR2, ignore the ping)
D2: action == "fail"    or   rid is None            (clear the "running" mark)
D3: len(body) > 100     and  settings.S3_BUCKET     (store body in object storage)

Each test is one row of the tables in docs/MCC_MCDC.md. Test names end with the
condition values, for example "_T_F" means first condition True, second False.
"""
from datetime import timedelta as td

from django.utils.timezone import now

from hc.api.models import Ping


def send(check, action="success", body=b"", rid=None):
    check.ping("1.2.3.4", "http", "GET", "unit-test", body, action, rid, None)
    check.refresh_from_db()
    return check


# ---- D1: paused AND manual_resume -------------------------------------------------

def test_d1_paused_T_manual_T_ping_is_ignored(make_check):
    check = send(make_check(status="paused", manual_resume=True))
    assert Ping.objects.get(owner=check).kind == "ign"
    assert check.status == "paused"


def test_d1_paused_T_manual_F_ping_is_processed(make_check):
    check = send(make_check(status="paused", manual_resume=False))
    assert Ping.objects.get(owner=check).kind is None
    assert check.status == "up"


def test_d1_paused_F_manual_T_ping_is_processed(make_check):
    check = send(make_check(status="new", manual_resume=True))
    assert Ping.objects.get(owner=check).kind is None
    assert check.status == "up"


def test_d1_paused_F_manual_F_ping_is_processed(make_check):
    check = send(make_check(status="new", manual_resume=False))
    assert Ping.objects.get(owner=check).kind is None
    assert check.status == "up"


# ---- D2: action == "fail" OR rid is None (start mark exists, rid differs) ----------

def running_check(make_check, new_rid):
    """A check with a start mark whose rid will NOT match the incoming ping."""
    return make_check(
        status="up",
        last_ping=now() - td(minutes=10),
        last_start=now() - td(minutes=1),
        last_start_rid=new_rid(),
    )


def test_d2_fail_T_ridnone_T_start_mark_cleared(make_check, new_rid):
    check = send(running_check(make_check, new_rid), "fail", rid=None)
    assert check.last_start is None


def test_d2_fail_T_ridnone_F_start_mark_cleared(make_check, new_rid):
    check = send(running_check(make_check, new_rid), "fail", rid=new_rid())
    assert check.last_start is None


def test_d2_fail_F_ridnone_T_start_mark_cleared(make_check, new_rid):
    check = send(running_check(make_check, new_rid), "success", rid=None)
    assert check.last_start is None


def test_d2_fail_F_ridnone_F_start_mark_kept(make_check, new_rid):
    check = send(running_check(make_check, new_rid), "success", rid=new_rid())
    assert check.last_start is not None


# ---- D3: len(body) > 100 AND S3 configured -----------------------------------------

def test_d3_long_T_s3_T_body_goes_to_object_storage(make_check, settings, monkeypatch):
    settings.S3_BUCKET = "test-bucket"
    monkeypatch.setattr("hc.api.models.put_object", lambda *args: None)
    check = send(make_check(), body=b"x" * 101)
    assert Ping.objects.get(owner=check).object_size == 101


def test_d3_long_T_s3_F_body_stays_in_database(make_check, settings):
    settings.S3_BUCKET = None
    check = send(make_check(), body=b"x" * 101)
    assert Ping.objects.get(owner=check).object_size is None


def test_d3_long_F_s3_T_body_stays_in_database(make_check, settings, monkeypatch):
    settings.S3_BUCKET = "test-bucket"
    monkeypatch.setattr("hc.api.models.put_object", lambda *args: None)
    check = send(make_check(), body=b"x" * 100)
    assert Ping.objects.get(owner=check).object_size is None


def test_d3_long_F_s3_F_body_stays_in_database(make_check, settings):
    settings.S3_BUCKET = None
    check = send(make_check(), body=b"x" * 100)
    assert Ping.objects.get(owner=check).object_size is None
