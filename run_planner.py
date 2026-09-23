import json
from pathlib import Path

from planner_agent import run_planner


## Create a function/logic that reads the requirements from requirements.json, 
# then calls the run_planner function with the requirements as input, and finally writes the validated plan to plan.json. 
HERE = Path(__file__).resolve().parent
REQUIREMENTS_PATH = HERE / "artifacts" / "requirements.json"
PLAN_PATH = HERE / "artifacts" / "plan.json"


def main():
    with open(REQUIREMENTS_PATH, "r", encoding="utf-8") as handle:
        requirements = json.load(handle)

    plan = run_planner(requirements)

    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PLAN_PATH, "w", encoding="utf-8") as handle:
        json.dump(plan, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print("Validated plan:")
    print(json.dumps(plan, indent=2, ensure_ascii=False))
    print("\nSaved plan to %s" % PLAN_PATH)


if __name__ == "__main__":
    main()
