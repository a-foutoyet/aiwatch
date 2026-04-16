#!/usr/bin/env python3
"""
DevWatch — Magazine Generator
Injects REPOS_DATA JSON into index.html template.
Usage: python3 generate-mag.py repos.json
"""
import json, sys, re, subprocess
from datetime import datetime

def generate(repos_json_path: str):
    with open(repos_json_path) as f:
        data = json.load(f)

    repos = data["repos"]
    now = datetime.now()
    week = now.isocalendar()[1]
    year = now.year

    issue_meta = {
        "kicker": f"Issue №{week:02d} · Week {week}, {year} · Security-Audited",
        "subtitle": f"The {len(repos)} repos worth your attention this week."
    }

    # Read template
    with open("index.html") as f:
        html = f.read()

    # Inject data
    html = html.replace("__REPOS_DATA__", json.dumps(repos, ensure_ascii=False))
    html = html.replace("__ISSUE_META__", json.dumps(issue_meta, ensure_ascii=False))

    with open("index.html", "w") as f:
        f.write(html)

    print(f"✅ Generated index.html — {len(repos)} repos — Issue №{week:02d}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate-mag.py repos.json")
        sys.exit(1)
    generate(sys.argv[1])
