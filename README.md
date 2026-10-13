# SCSE '26 – Agentic Software Engineering: Robot Navigation

This project converts a natural-language project brief (`brief.txt`) for a
mobile robot navigation component into explicit, validated software
requirements, a navigation plan, and working Python code — using the **Qwen**
model as a multi-agent pipeline (Analyst → Planner → Developer). The generated
code is then benchmarked in simulation and reviewed.

## Project structure

```
scse_agentic_se_baby_isolation/
├── brief.txt                      # Customer's natural-language brief (input)
├── robot_requirements.txt         # Step 1: Qwen free-text requirement runs (generated)
│
├── analyst_agent.py               # Analyst Agent: brief → validated requirements JSON
├── planner_agent.py               # Planner Agent: requirements → navigation plan JSON
├── developer_agent.py             # Developer Agent: plan → Python navigation code
│
├── brief_to_req.py                # Step 1 runner: ask Qwen several times
├── run_analyst.py                 # Step 2 runner: brief → artifacts/requirements.json
├── run_planner.py                 # Step 3 runner: requirements → artifacts/plan.json
├── run_developer.py               # Step 4 runner: plan → navigation_logic.py
│
├── artifacts/
│   ├── requirements.json          # Validated requirements (generated)
│   ├── plan.json                  # Validated navigation plan (generated)
│   ├── simulation_results.json    # Full simulation benchmark data (generated)
│   └── benchmark_report.md        # Human-readable benchmark report (generated)
│
├── generated/
│   └── navigation_logic.py        # AI-generated navigation logic (Developer Agent output)
│
├── navigation_logic.py            # Copy of the generated logic (root-level convenience)
├── navigation_logic_revised.py    # Revised logic after code review
│
├── simulator.py                   # Simulation benchmark: truth table + grid worlds
├── test_revised.py                # Unit tests for the revised logic
│
├── review_notes.md                # Code review of the generated navigation logic
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Template for configuring the API key
├── .gitignore
└── README.md
```

## The agent pipeline

```
brief.txt
   │
   ▼  Analyst Agent (analyst_agent.py)
artifacts/requirements.json
   │
   ▼  Planner Agent (planner_agent.py)
artifacts/plan.json
   │
   ▼  Developer Agent (developer_agent.py)
generated/navigation_logic.py
   │
   ▼  Simulation (simulator.py)
artifacts/simulation_results.json + benchmark_report.md
   │
   ▼  Code Review (review_notes.md)
navigation_logic_revised.py
```

## The requirements JSON

The Analyst Agent returns a JSON object with **exactly** these keys:

```json
{
  "goal": "string",
  "allowed_actions": ["FORWARD", "LEFT", "RIGHT", "STOP"],
  "safe_stop": true,
  "avoid.obstacles": true
}
```

The only actions allowed in the whole navigation system are
`FORWARD`, `LEFT`, `RIGHT`, `STOP` — no other action is accepted by the
validator.

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Get a DashScope (Qwen) API key from
   <https://bailian.console.aliyun.com/> (API-KEY section).

3. Configure the key using **one** of these methods:

   - Copy `.env.example` to `.env` and paste your key:
     ```
     DASHSCOPE_API_KEY=sk-xxxxxxxx
     ```
   - Or set an environment variable:
     ```bash
     # PowerShell
     $env:DASHSCOPE_API_KEY = "sk-xxxxxxxx"
     # bash
     export DASHSCOPE_API_KEY="sk-xxxxxxxx"
     ```

## Run the full pipeline

### Step 1 – Free-text requirements (consistency check)

Ask Qwen several times to turn the brief into free-text requirements and
inspect consistency (saved to `robot_requirements.txt`):

```bash
python brief_to_req.py
```

### Step 2 – Analyst Agent (validated requirements JSON)

```bash
python run_analyst.py
```

Output: `artifacts/requirements.json`

### Step 3 – Planner Agent (navigation plan)

```bash
python run_planner.py
```

Output: `artifacts/plan.json`

### Step 4 – Developer Agent (navigation code)

```bash
python run_developer.py
```

Output: `navigation_logic.py` (also copied to `generated/navigation_logic.py`)

### Step 5 – Simulation benchmark

Run the exhaustive truth-table test (all 64 input combinations) and five
grid-world environments:

```bash
python simulator.py
```

Outputs:
- `artifacts/simulation_results.json` — raw benchmark data
- `artifacts/benchmark_report.md` — human-readable report

### Step 6 – Test the revised logic

```bash
python test_revised.py
```

## Simulation results summary

| Test | Result |
|---|---|
| Truth-table safety (64 combos) | 100% |
| Truth-table goal preference | 100% |
| Grid environments (goal reached) | 4 / 5 |
| Dead-end safe stop | Correct |

See `artifacts/benchmark_report.md` for full details.

## Revision after review

The code review (`review_notes.md`) identified that the generated logic wanders
when no goal-direction signal is present. The revised implementation
(`navigation_logic_revised.py`) stops in that case as a safer default, while
preserving all original safety and goal-preference guarantees.
