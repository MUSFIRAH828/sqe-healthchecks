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

    def ping(self, check_uuid, suffix=""):
        return requests.get(f"{self.base_url}/ping/{check_uuid}{suffix}", timeout=10)


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
