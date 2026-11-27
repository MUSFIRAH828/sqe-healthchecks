"""Shared fixtures for the team tests."""
import uuid
from datetime import timedelta as td

import pytest
from django.contrib.auth.models import User

from hc.accounts.models import Project
from hc.api.models import Check


@pytest.fixture
def project(db):
    user = User.objects.create(username="alice", email="alice@example.com")
    return Project.objects.create(owner=user, name="Unit Test Project")


@pytest.fixture
def make_check(project):
    """Return a function that creates a Check with the given settings."""

    def _make(status="new", **fields):
        check = Check(project=project, name="unit check")
        check.timeout = td(hours=1)
        check.grace = td(minutes=5)
        check.status = status
        for key, value in fields.items():
            setattr(check, key, value)
        check.save()
        return check

    return _make


@pytest.fixture
def do_ping():
    """Return a function that sends a ping to a check, like the ping view does."""

    def _ping(check, action="success", body=b"", rid=None, exitstatus=None):
        check.ping("1.2.3.4", "http", "GET", "unit-test", body, action, rid, exitstatus)
        check.refresh_from_db()
        return check

    return _ping


@pytest.fixture
def new_rid():
    return lambda: uuid.uuid4()
