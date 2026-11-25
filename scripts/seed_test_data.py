"""Seed synthetic test data for the SQE project (Healthchecks).

Run from the repository root:   python scripts/seed_test_data.py

Creates (only if missing):
  - 3 users: owner / member / viewer  (all synthetic, password below)
  - 1 project owned by owner, with member (role w) and viewer (role r) invited
  - 5 checks with different timeouts, grace times and statuses
  - API keys for the project, saved to tests/team/seed_output.json
"""
import json
import os
import sys
from datetime import timedelta as td
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hc.settings")

import django  # noqa: E402

django.setup()

from django.contrib.auth.models import User  # noqa: E402
from django.utils.timezone import now  # noqa: E402

from hc.accounts.models import Member, Profile, Project  # noqa: E402
from hc.api.models import Check  # noqa: E402

PASSWORD = "Test#Pass2026"
USERS = {
    "owner": "owner@example.com",
    "member": "member@example.com",
    "viewer": "viewer@example.com",
}

# name, timeout (s), grace (s), status
CHECKS = [
    ("Nightly Backup", 3600, 300, "new"),
    ("Hourly Report", 3600, 600, "up"),
    ("Daily Cleanup", 86400, 3600, "up"),
    ("Weekly Export", 604800, 7200, "new"),
    ("Paused Job", 3600, 300, "paused"),
]


def get_or_make_user(email: str) -> User:
    user = User.objects.filter(email=email).first()
    if user is None:
        user = User(username=email.split("@")[0], email=email)
        user.set_password(PASSWORD)
        user.save()
    Profile.objects.for_user(user)
    return user


def main() -> None:
    users = {role: get_or_make_user(email) for role, email in USERS.items()}

    project = Project.objects.filter(owner=users["owner"], name="SQE Project").first()
    created_project = project is None
    if created_project:
        project = Project(owner=users["owner"], name="SQE Project")
        project.badge_key = users["owner"].username
        project.save()

    project.invite(users["member"], Member.Role.REGULAR)
    project.invite(users["viewer"], Member.Role.READONLY)

    for name, timeout, grace, status in CHECKS:
        if Check.objects.filter(project=project, name=name).exists():
            continue
        c = Check(project=project, name=name)
        c.slug = name.lower().replace(" ", "-")
        c.timeout = td(seconds=timeout)
        c.grace = td(seconds=grace)
        c.status = status
        if status == "up":
            c.last_ping = now()
            c.alert_after = c.going_down_after()
        c.save()

    out = {
        "password_for_all_users": PASSWORD,
        "users": USERS,
        "project_code": str(project.code),
    }
    if created_project:
        out["api_key_rw"] = project.set_api_key()
        out["api_key_ro"] = project.set_api_key_readonly()
        project.save()
    else:
        out["note"] = "Project already existed; API keys were not regenerated."

    target = ROOT / "tests" / "team" / "seed_output.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if created_project or not target.exists():
        target.write_text(json.dumps(out, indent=2))
    print("Seed complete. Project code:", project.code)
    print("Checks in project:", Check.objects.filter(project=project).count())
    print("Output saved to", target)


if __name__ == "__main__":
    main()
