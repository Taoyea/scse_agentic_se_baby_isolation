# SCSE '26 – Agentic Software Engineering: Robot Navigation Requirements

This project converts a natural-language project brief (`brief.txt`) for a
mobile robot navigation component into explicit, validated software
requirements, using the **Qwen** model as an "Analyst Agent".

## Project structure

```
agentic_se/
├── artifacts/
│   └── requirements.json      # Final validated requirements (generated)
├── analyst_agent.py           # Analyst Agent: run_analyst() + validate_requirements()
├── brief.txt                  # Customer's natural-language brief (input)
├── brief_to_req.py            # Step 1: ask Qwen several times, save free-text output
├── run_analyst.py             # Runner: brief -> Analyst Agent -> requirements.json
├── robot_requirements.txt     # Step 1 output: several Qwen runs (generated)
├── requirements.txt           # Python dependencies
├── .env.example               # Template for configuring the API key
└── .gitignore
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

## Run

Step 1 – ask Qwen several times and inspect consistency of the free-text
requirements (saved to `robot_requirements.txt`):

```bash
python brief_to_req.py
```

Step 2 – run the Analyst Agent to obtain the strict, validated JSON
requirements (saved to `artifacts/requirements.json`):

```bash
python run_analyst.py
```

## Execution flow

```
brief.txt
   └─> run_analyst.py
          └─> run_analyst(brief_text)
                 └─> system prompt + brief ─> Qwen ─> JSON text
                        └─> validation (validate_requirements)
                               └─> artifacts/requirements.json
```
