#!/usr/bin/env python3
"""
DevWatch — Magazine Generator
Injects REPOS_DATA JSON into index.html template.
Usage: python3 generate-mag.py repos.json
"""
import json, sys, re
from datetime import datetime

# English words that must never appear in FR fields
# Tech proper nouns (framework, pipeline, RAG, LLM, harness, workflow, MCP,
# open-source, plugin, skills, pattern, auto-capture, hedge fund) are allowed.
FR_FORBIDDEN = {
    "measurably", "genuinely", "genuinement", "curates", "curaite",
    "shipping", "shippent", "actually", "novel", "benchmark",
    "insight", "directly", "immediately", "this week", "every",
    "this", "the ", " is ", " are ", " and ", " or ", " with ",
    " for ", " in ", " of ", " to ", " a ", " an ",
}

def check_fr_fields(repos):
    """Warn on English words found in FR text fields."""
    warnings = []
    fr_fields = ["headline", "description", "weekStars", "whyItMatters"]
    for repo in repos:
        path = repo.get("path", "?")
        fr = repo.get("fr", {})
        for field in fr_fields:
            text = fr.get(field, "")
            for word in FR_FORBIDDEN:
                # whole-word match, case-insensitive
                pattern = r'(?<![a-zA-Z])' + re.escape(word) + r'(?![a-zA-Z])'
                if re.search(pattern, text, re.IGNORECASE):
                    warnings.append(f"  ⚠️  [{path}] fr.{field}: mot anglais détecté → '{word}'")
    return warnings

def generate(repos_json_path: str):
    with open(repos_json_path) as f:
        data = json.load(f)

    repos = data["repos"]
    now = datetime.now()
    week = now.isocalendar()[1]
    year = now.year

    # Validate FR fields before generating
    warnings = check_fr_fields(repos)
    if warnings:
        print("🚨 Problèmes de traduction FR détectés :")
        for w in warnings:
            print(w)
        print("Corrige repos.json avant de générer.\n")
        sys.exit(1)

    is_first_issue = (week == 16 and year == 2026)  # Numéro de lancement
    issue_meta = {
        "fr": {
            "kicker": (
                f"Numéro №{week:02d} · Sélection de lancement · Audité sécurité"
                if is_first_issue else
                f"Numéro №{week:02d} · Semaine {week}, {year} · Audité sécurité"
            ),
            "subtitle": f"Les {len(repos)} repos qui valent notre attention cette semaine."
        },
        "en": {
            "kicker": (
                f"Issue №{week:02d} · Launch Selection · Security-Audited"
                if is_first_issue else
                f"Issue №{week:02d} · Week {week}, {year} · Security-Audited"
            ),
            "subtitle": f"The {len(repos)} repos worth our attention this week."
        }
    }

    # Read template (never overwrite the template itself)
    with open("_template.html") as f:
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
