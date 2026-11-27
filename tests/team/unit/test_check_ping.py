"""Unit tests for Check.ping() - workflow 2 (ping a check).

Covers FR6, FR7, FR8 and business rules BR2 and BR3.
"""
from django.utils.timezone import now

from hc.api.models import Check, Ping


def test_success_ping_moves_new_check_to_up(make_check, do_ping):
    check = make_check(status="new")
    do_ping(check, "success")
    assert check.status == "up"
    assert check.last_ping is not None
    assert check.n_pings == 1


def test_fail_ping_moves_up_check_to_down(make_check, do_ping):
    check = make_check(status="up")
    do_ping(check, "fail")
    assert check.status == "down"
    assert Ping.objects.get(owner=check).kind == "fail"


def test_success_ping_moves_down_check_back_to_up(make_check, do_ping):
    check = make_check(status="down")
    do_ping(check, "success")
    assert check.status == "up"


def test_start_ping_keeps_status_and_last_ping(make_check, do_ping):
    # An "up" check has always received a ping, so give it a last_ping first.
    before = now()
    check = make_check(status="up", last_ping=before)
    do_ping(check, "start")
    assert check.status == "up"
    assert check.last_ping == before
    assert check.last_start is not None
    assert check.n_pings == 1


def test_log_ping_keeps_status(make_check, do_ping):
    check = make_check(status="down")
    do_ping(check, "log")
    assert check.status == "down"
    assert Ping.objects.get(owner=check).kind == "log"


def test_paused_check_without_manual_resume_returns_to_up(make_check, do_ping):
    check = make_check(status="paused", manual_resume=False)
    do_ping(check, "success")
    assert check.status == "up"


def test_paused_check_with_manual_resume_ignores_ping(make_check, do_ping):
    check = make_check(status="paused", manual_resume=True)
    do_ping(check, "success")
    assert check.status == "paused"
    assert check.last_ping is None
    assert Ping.objects.get(owner=check).kind == "ign"
    assert check.n_pings == 1


def test_every_ping_is_logged(make_check, do_ping):
    check = make_check(status="new")
    do_ping(check, "success")
    do_ping(check, "success")
    assert Ping.objects.filter(owner=check).count() == 2
    assert Check.objects.get(id=check.id).n_pings == 2
