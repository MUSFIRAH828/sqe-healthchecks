"""Read the SonarQube results of project sqe-healthchecks and fail when a threshold is broken.

Usage: python tests/team/sonar_gate.py <server-url> <token>
Thresholds (change them only with a written reason in docs/SONARQUBE_RESULTS.md):
  bugs <= MAX_BUGS, vulnerabilities <= MAX_VULNERABILITIES, coverage >= MIN_COVERAGE (percent).
"""
import base64
import json
import sys
import time
import urllib.request

PROJECT = "sqe-healthchecks"
MAX_BUGS = 0
MAX_VULNERABILITIES = 0
MIN_COVERAGE = 60.0  # placeholder: set from the first real scan and justify it


def fetch(url, token):
    request = urllib.request.Request(url)
    auth = base64.b64encode(f"{token}:".encode()).decode()
    request.add_header("Authorization", f"Basic {auth}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    server, token = sys.argv[1].rstrip("/"), sys.argv[2]
    url = f"{server}/api/measures/component?component={PROJECT}&metricKeys=bugs,vulnerabilities,coverage"
    measures = {}
    for _ in range(36):  # wait up to 3 minutes for the analysis to be processed
        try:
            data = fetch(url, token)
            measures = {m["metric"]: m.get("value") for m in data["component"]["measures"]}
            if "bugs" in measures:
                break
        except Exception as error:  # the analysis may not be visible yet
            print("waiting for the analysis:", error)
        time.sleep(5)
    if "bugs" not in measures:
        print("FAIL: no SonarQube measures found")
        sys.exit(1)
    bugs = int(measures["bugs"])
    vulns = int(measures["vulnerabilities"])
    coverage = float(measures.get("coverage", 0))
    print(f"bugs={bugs} (max {MAX_BUGS}), vulnerabilities={vulns} (max {MAX_VULNERABILITIES}), coverage={coverage}% (min {MIN_COVERAGE}%)")
    failed = bugs > MAX_BUGS or vulns > MAX_VULNERABILITIES or coverage < MIN_COVERAGE
    if failed:
        print("FAIL: SonarQube threshold broken")
        sys.exit(1)
    print("SonarQube gate passed")


if __name__ == "__main__":
    main()
