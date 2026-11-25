# Reset the local Healthchecks database and re-seed synthetic data.
# Run from the repository root, with the virtual environment active:
#   .\scripts\reset_db.ps1
# Stop the dev server (Ctrl+C) before running this.
$ErrorActionPreference = "Stop"
if (Test-Path "hc.sqlite") { Remove-Item "hc.sqlite" -Force }
python manage.py migrate
python scripts/seed_test_data.py
