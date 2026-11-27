"""Unit tests for status calculation: Check.get_status(), going_down_after(), get_grace_start().

Covers rule BR3 (state change over time): up -> grace -> down, with boundary values
just below, at and just above each threshold. Time is frozen with time-machine.
"""
from datetime import datetime, timedelta as td, timezone

import pytest
import time_machine

NOW = datetime(2026, 11, 27, 10, 0, 0, tzinfo=timezone.utc)
TIMEOUT = td(hours=1)  # make_check default
GRACE = td(minutes=5)  # make_check default


@pytest.fixture(autouse=True)
def frozen_time():
    with time_machine.travel(NOW, tick=False):
        yield


# ---- simple checks: up -> grace -> down --------------------------------------

@pytest.mark.parametrize(
    "seconds_after_ping,expected",
    [
        (3599, "up"),  # just below end of timeout
        (3600, "grace"),  # exactly at end of timeout
        (3601, "grace"),
        (3899, "grace"),  # just below end of grace
        (3900, "down"),  # exactly at end of grace
        (3901, "down"),
    ],
)
def test_up_check_changes_with_time(make_check, seconds_after_ping, expected):
    check = make_check(status="up", last_ping=NOW - td(seconds=seconds_after_ping))
    assert check.get_status() == expected


@pytest.mark.parametrize("status", ["new", "paused", "down"])
def test_new_paused_and_down_checks_keep_their_status(make_check, status):
    assert make_check(status=status).get_status() == status


# ---- running (start ping) ------------------------------------------------------

def test_started_check_is_down_when_grace_after_start_has_passed(make_check):
    check = make_check(status="up", last_ping=NOW, last_start=NOW - GRACE)
    assert check.get_status() == "down"


def test_started_check_shows_started_when_asked(make_check):
    check = make_check(status="up", last_ping=NOW, last_start=NOW - GRACE + td(seconds=1))
    assert check.get_status(with_started=True) == "started"


def test_started_check_is_up_when_started_is_not_asked(make_check):
    check = make_check(status="up", last_ping=NOW, last_start=NOW - GRACE + td(seconds=1))
    assert check.get_status() == "up"


# ---- going_down_after and get_grace_start --------------------------------------

def test_going_down_after_is_last_ping_plus_timeout_plus_grace(make_check):
    check = make_check(status="up", last_ping=NOW)
    assert check.going_down_after() == NOW + TIMEOUT + GRACE


@pytest.mark.parametrize("status", ["new", "paused", "down"])
def test_going_down_after_is_none_without_a_start(make_check, status):
    assert make_check(status=status).going_down_after() is None


def test_new_check_that_is_running_goes_down_after_start_plus_grace(make_check):
    check = make_check(status="new", last_start=NOW)
    assert check.going_down_after() == NOW + GRACE


def test_down_check_ignores_start_time(make_check):
    check = make_check(status="down", last_start=NOW)
    assert check.get_grace_start() is None


def test_grace_start_can_ignore_start_time(make_check):
    check = make_check(status="up", last_ping=NOW, last_start=NOW - td(minutes=1))
    assert check.get_grace_start(with_started=False) == NOW + TIMEOUT
    assert check.get_grace_start() == NOW - td(minutes=1)


# ---- other schedule kinds (cron, oncalendar) ------------------------------------

def test_cron_check_expects_next_ping_from_schedule(make_check):
    check = make_check(status="up", kind="cron", schedule="*/10 * * * *", last_ping=NOW)
    assert check.get_grace_start() == NOW + td(minutes=10)
    assert check.get_status() == "up"


def test_oncalendar_check_expects_next_ping_from_schedule(make_check):
    check = make_check(status="up", kind="oncalendar", schedule="hourly", last_ping=NOW)
    assert check.get_grace_start() == NOW + td(hours=1)


def test_oncalendar_check_with_no_future_time_stays_up_forever(make_check):
    check = make_check(status="up", kind="oncalendar", schedule="2000-01-01", last_ping=NOW)
    assert check.get_grace_start() is None
    assert check.get_status() == "up"
