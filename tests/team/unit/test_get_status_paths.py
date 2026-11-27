"""Basis-path tests for Check.get_status() - one test per independent path of its CFG.

Cyclomatic complexity V(G) = 8, so there are 8 independent paths (see docs/CFG_get_status.md).
Node numbers N1..N14 refer to that document.
"""
from datetime import datetime, timedelta as td, timezone

import pytest
import time_machine

NOW = datetime(2026, 11, 27, 10, 0, 0, tzinfo=timezone.utc)
GRACE = td(minutes=5)  # make_check default grace; default timeout is 1 hour


@pytest.fixture(autouse=True)
def frozen_time():
    with time_machine.travel(NOW, tick=False):
        yield


def test_path_1_started_and_start_is_older_than_grace_returns_down(make_check):
    # N1(T) -> N2(T) -> N3
    check = make_check(status="up", last_ping=NOW, last_start=NOW - GRACE)
    assert check.get_status() == "down"


def test_path_2_started_recently_and_started_requested_returns_started(make_check):
    # N1(T) -> N2(F) -> N4(T) -> N5
    check = make_check(status="up", last_ping=NOW, last_start=NOW - td(seconds=1))
    assert check.get_status(with_started=True) == "started"


def test_path_3_started_recently_on_new_check_returns_its_status(make_check):
    # N1(T) -> N2(F) -> N4(F) -> N6(T) -> N7
    check = make_check(status="new", last_start=NOW - td(seconds=1))
    assert check.get_status() == "new"


@pytest.mark.parametrize("status", ["new", "paused", "down"])
def test_path_4_no_start_and_new_paused_or_down_returns_its_status(make_check, status):
    # N1(F) -> N6(T) -> N7
    assert make_check(status=status).get_status() == status


def test_path_5_no_next_ping_expected_returns_up(make_check):
    # N1(F) -> N6(F) -> N8(T) -> N9
    check = make_check(status="up", kind="oncalendar", schedule="2000-01-01", last_ping=NOW)
    assert check.get_status() == "up"


def test_path_6_grace_has_ended_returns_down(make_check):
    # N1(F) -> N6(F) -> N8(F) -> N10(T) -> N11
    check = make_check(status="up", last_ping=NOW - td(hours=1) - GRACE)
    assert check.get_status() == "down"


def test_path_7_inside_grace_returns_grace(make_check):
    # N1(F) -> N6(F) -> N8(F) -> N10(F) -> N12(T) -> N13
    check = make_check(status="up", last_ping=NOW - td(hours=1))
    assert check.get_status() == "grace"


def test_path_8_ping_is_on_time_returns_up(make_check):
    # N1(F) -> N6(F) -> N8(F) -> N10(F) -> N12(F) -> N14
    check = make_check(status="up", last_ping=NOW - td(minutes=1))
    assert check.get_status() == "up"
