# SCSE '26 – Agentic SE: Robot Navigation

Used Qwen as a three-agent pipeline (Analyst → Planner → Developer) to turn a
natural-language brief into working robot navigation code, then tested it in
simulation and reviewed the output.

## How it works

```
brief.txt
  → Analyst Agent    → artifacts/requirements.json
  → Planner Agent    → artifacts/plan.json
  → Developer Agent  → generated/navigation_logic.py
  → Simulation       → artifacts/simulation_results.json
  → Code Review      → navigation_logic_revised.py
```

## Files

```
brief.txt                    the original project brief
robot_requirements.txt       Qwen asked 3x for free-text requirements (consistency check)

analyst_agent.py             Analyst Agent: brief → validated requirements JSON
planner_agent.py             Planner Agent: requirements → navigation plan JSON
developer_agent.py           Developer Agent: plan → Python code

brief_to_req.py              step 1 runner
run_analyst.py               step 2 runner
run_planner.py               step 3 runner
run_developer.py             step 4 runner

artifacts/
  requirements.json          validated requirements
  plan.json                  validated navigation plan
  simulation_results.json    raw benchmark data
  benchmark_report.md        what the tests found

generated/
  navigation_logic.py        the code Qwen wrote

navigation_logic.py          copy of generated code (root-level convenience)
navigation_logic_revised.py fixed version after review

simulator.py                 runs truth-table + grid-world tests
test_revised.py              unit tests for the revised logic

review_notes.md              code review writeup
```

## Setup

```bash
pip install -r requirements.txt
```

Get a DashScope API key from https://bailian.console.aliyun.com/ and either put
it in `.env` (copy from `.env.example`) or set it as an env var.

## Running everything

```bash
python brief_to_req.py     # free-text requirements (3 runs)
python run_analyst.py      # → artifacts/requirements.json
python run_planner.py      # → artifacts/plan.json
python run_developer.py    # → navigation_logic.py
python simulator.py        # → artifacts/simulation_results.json
python test_revised.py     # verify revised logic
```

## Test results

- 64/64 input combinations pass (100% safe, 100% goal preference)
- 4/5 grid environments reach the goal (the 5th is a dead-end safety test, correctly stops)
- Revised logic also passes all 64 unit tests

See artifacts/benchmark_report.md for details and review_notes.md for what was
fixed in the revised version.
