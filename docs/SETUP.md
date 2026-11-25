# Setup, seed and reset (Windows PowerShell)

Upstream: https://github.com/healthchecks/healthchecks (BSD 3-clause)
Baseline commit: c1039ad23395162c5e2f17d324d8ccdaa60a1d14 (2026-11-23, "Bump cronsim to 2.9")
Requires Python 3.12 or newer.

## Install (once)
```
git clone https://github.com/MUSFIRAH828/sqe-healthchecks.git
cd sqe-healthchecks
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
```

## Create the database and seed synthetic data
```
python manage.py migrate
python scripts/seed_test_data.py
```
Seeded users (all use the password in `tests/team/seed_output.json`):
- owner@example.com  - project owner
- member@example.com - project member (role "w", can create checks)
- viewer@example.com - read-only member (role "r")

The project "SQE Project" gets 5 checks. Running the seed script again does not create duplicates.

## Start the application
```
python manage.py runserver
```
Open http://localhost:8000 and sign in with email and password.

## Reset between test runs
Stop the server (Ctrl+C), then:
```
.\scripts\reset_db.ps1
```
This deletes `hc.sqlite`, recreates the schema and seeds the data again.
