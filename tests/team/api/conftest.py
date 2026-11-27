"""Fixtures for the API tests (they call the running application with Requests).

Start the app first (python manage.py runserver) and seed it (python scripts/seed_test_data.py).
Set API_BASE_URL if the app is not on http://localhost:8000.
Set API_TESTS_REQUIRED=1 to make a missing server a failure instead of a skip (used in CI).
"""
import json
import os
import uuid
from pathlib import Path

import pytest
import requests

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")
SEED_FILE = Path(__file__).resolve().parents[1] / "seed_output.json"


class Api:
    """Small helper around Requests for the checks API."""

    def __init__(self, base_url, rw_key, ro_key):
        self.base_url = base_url
        self.rw_key = rw_key
        self.ro_key = ro_key

    def headers(self, key):
        return {"X-Api-Key": key} if key else {}

    def create(self, body, key="rw"):
        key = {"rw": self.rw_key, "ro": self.ro_key}.get(key, key)
        return requests.post(
            f"{self.base_url}/api/v3/checks/", json=body, headers=self.headers(key), timeout=10
        )

    def list_checks(self, key="rw"):
        key = {"rw": self.rw_key, "ro": self.ro_key}.get(key, key)
        r = requests.get(f"{self.base_url}/api/v3/checks/", headers=self.headers(key), timeout=10)
        r.raise_for_status()
        return r.json()["checks"]

    def get_check(self, check_uuid, key="rw"):
        key = {"rw": self.rw_key, "ro": self.ro_key}.get(key, key)
        return requests.get(
            f"{self.base_url}/api/v3/checks/{check_uuid}", headers=self.headers(key), timeout=10
        )

    def ping(self, check_uuid, suffix="", method="GET", **kwargs):
        url = f"{self.base_url}/ping/{check_uuid}{suffix}"
        return requests.request(method, url, timeout=10, **kwargs)

    def post_action(self, check_uuid, action, key="rw"):
        """Call POST /api/v3/checks/<uuid>/pause or /resume."""
        key = {"rw": self.rw_key, "ro": self.ro_key}.get(key, key)
        url = f"{self.base_url}/api/v3/checks/{check_uuid}/{action}"
        return requests.post(url, headers=self.headers(key), timeout=10)

    def state(self, check_uuid):
        """(status, n_pings, last_ping) of a check, read back through the API."""
        data = self.get_check(check_uuid).json()
        return data["status"], data["n_pings"], data["last_ping"]


@pytest.fixture(scope="session")
def api():
    required = os.environ.get("API_TESTS_REQUIRED") == "1"
    if not SEED_FILE.exists():
        msg = f"{SEED_FILE} not found. Run: python scripts/seed_test_data.py"
        pytest.fail(msg) if required else pytest.skip(msg)
    seed = json.loads(SEED_FILE.read_text())
    try:
        requests.get(BASE_URL + "/", timeout=5)
    except requests.RequestException:
        msg = f"Application is not running at {BASE_URL}. Run: python manage.py runserver"
        pytest.fail(msg) if required else pytest.skip(msg)
    return Api(BASE_URL, seed["api_key_rw"], seed["api_key_ro"])


@pytest.fixture
def unique_name():
    return lambda prefix="api": f"{prefix}-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def new_check(api, unique_name):
    """A fresh check (status new, no pings); returns its uuid."""
    r = api.create({"name": unique_name("ping"), "timeout": 3600, "grace": 300})
    assert r.status_code == 201
    return r.json()["uuid"]
