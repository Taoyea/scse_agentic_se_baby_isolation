"""
brief_to_req.py
===============
First step of the Requirements Engineering task.

Reads the natural-language robot navigation brief (brief.txt), asks the
Qwen model SEVERAL times to turn it into software requirements, prints
every response so its consistency can be inspected, and saves all runs
into robot_requirements.txt.

Usage:
    python brief_to_req.py
"""

import os
from datetime import datetime

from analyst_agent import MODEL, get_client

# Number of times to ask Qwen, so the outputs can be compared for consistency.
N_RUNS = 3

HERE = os.path.dirname(os.path.abspath(__file__))
BRIEF_PATH = os.path.join(HERE, "brief.txt")
OUTPUT_PATH = os.path.join(HERE, "robot_requirements.txt")

SYSTEM_PROMPT = (
    "You are a senior software requirements analyst. "
    "You are given a customer's natural-language project brief. "
    "Your job is to extract clear, explicit, testable software requirements "
    "from it. List the requirements as numbered bullet points, grouped under "
    "short headings when useful. Cover the system's goal, the inputs it "
    "receives, the actions it may take, its safety rules and what it must do "
    "when no safe action exists. Do not invent features that are not in the brief."
)


def generate_requirements(client, brief_text):
    """Ask Qwen once for a free-text list of software requirements."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": brief_text},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


def main():
    with open(BRIEF_PATH, "r", encoding="utf-8") as handle:
        brief_text = handle.read().strip()

    client = get_client()
    sections = []

    for run in range(1, N_RUNS + 1):
        print("\n" + "=" * 70)
        print("RUN %d/%d" % (run, N_RUNS))
        print("=" * 70)
        output = generate_requirements(client, brief_text)
        print(output)
        sections.append(
            "RUN %d - %s\nModel: %s\n\n%s"
            % (run, datetime.now().isoformat(timespec="seconds"), MODEL, output)
        )

    header = (
        "ROBOT NAVIGATION - SOFTWARE REQUIREMENTS GENERATED FROM brief.txt\n"
        "Generated: %s\nModel: %s\nNumber of runs: %d\n"
        % (datetime.now().isoformat(timespec="seconds"), MODEL, N_RUNS)
        + "=" * 70
    )
    body = ("\n\n" + "-" * 70 + "\n\n").join(sections)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as handle:
        handle.write(header + "\n" + body + "\n")

    print("\nSaved all %d runs to %s" % (N_RUNS, OUTPUT_PATH))


if __name__ == "__main__":
    main()
