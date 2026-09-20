"""
run_analyst.py
==============
Runner for the Analyst Agent.

It reads brief.txt, calls run_analyst() to obtain the validated software
requirements, and saves them as artifacts/requirements.json.

Usage:
    python run_analyst.py
"""

import json
import os

from analyst_agent import run_analyst

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEF_PATH = os.path.join(HERE, "brief.txt")
ARTIFACTS_DIR = os.path.join(HERE, "artifacts")
OUTPUT_PATH = os.path.join(ARTIFACTS_DIR, "requirements.json")


def main():
    with open(BRIEF_PATH, "r", encoding="utf-8") as handle:
        brief_text = handle.read().strip()

    # Call the Analyst Agent and receive the validated requirements.
    requirements = run_analyst(brief_text)

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(requirements, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print("Validated requirements:")
    print(json.dumps(requirements, indent=2, ensure_ascii=False))
    print("\nSaved requirements to %s" % OUTPUT_PATH)


if __name__ == "__main__":
    main()
