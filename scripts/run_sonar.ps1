# Run our unit tests with coverage, then analyse the project with SonarQube.
# Run from the repository root with the virtual environment active and SonarQube running on port 9000:
#   .\scripts\run_sonar.ps1 -Token "your-sonarqube-token"
param([Parameter(Mandatory = $true)][string]$Token)

python -m coverage erase
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m coverage run -m pytest tests/team/unit -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -m coverage xml
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

docker run --rm `
    -e SONAR_HOST_URL="http://host.docker.internal:9000" `
    -e SONAR_TOKEN="$Token" `
    -v "${PWD}:/usr/src" `
    sonarsource/sonar-scanner-cli
exit $LASTEXITCODE
