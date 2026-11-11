# SecondsMatter — Instructions for Claude Code

## 1. Project

SecondsMatter is a NOVA IMS BSc Data Science Capstone Project (2026/2027, four-person team): an **AI-powered decision-support prototype for emergency resource planning and dispatch**. Users explore emergency demand, inspect simulated resource availability, compare dispatch options by estimated travel time and remaining coverage, and ask follow-up or hypothetical questions to a conversational agent. Planning (demand forecasting, relocations) comes only after a complete, reliable dispatch MVP.

**Safety boundary:** this is an academic simulation, **not a real dispatch system**. It must not send real dispatch instructions, determine clinical priority, claim operational readiness, or present synthetic results as real-world performance. A human stays in control of every simulated decision, and simulated information is labelled as such.

## 2. Teaching mode: how to work with the team

The team are students **learning** while they build this project. Never assume they know what to do next, why it matters, or how it works. Every step must be explained so that any member can defend it at the defence.

1. **Recommend the next step.** Name the single best next step, why it is the best one now (linked to the required components, the deadlines and the MVP), and what is deliberately left for later. For a new step, wait for the user's agreement before starting.
2. **Explain how before doing.** Say which files will change, the approach, and any new concept in plain language. Explain a technical term the first time it is used.
3. **Keep steps small.** Do one step at a time, small enough to review and understand. Never chain several steps without checking in. Stop after each step.
4. **Explain the code.** For anything longer than a few lines, give a brief explanation: the main idea, the key functions, and why this design. Add code comments only where the logic is not obvious.
5. **Close each step.** Say what changed, how to run or test it, what to understand in order to defend it, and the recommended next step.

## 3. Course rules and deadlines

The course documents in `docs/reference/` take precedence over this file: `Project_Guidelines.pdf`, `Technical_Proposal_Guidelines.pdf`, `Proposal_Week_03.pdf` and the team's initial `SecondsMatter_Proposal.pdf`, which is a starting concept, not a commitment. `README_TEMPLATE.md` is referenced by the guidelines but not yet in the repo. Do not invent requirements or assume instructor approval; ask the team when unsure.

- **Technical proposal, 6 Dec 2026, 23:59:** one PDF named `TeamName_TechnicalProposal.pdf`, with the 10 sections of the guidelines in order. It contains no code and no placeholder sections. The final delivery is compared with its section 7 (scope) and section 8 (plan), so commit only to what can be built.
- **Final submission, 3 Jan 2027, 23:59:** late penalties (out of 20) are −2, −5 and −9 points for days 1–3; after that it is not accepted.
  - Only the **default branch** counts.
  - `mb-cardoso` must be a collaborator on the repository.
  - Moodle gets the same code as `TeamName_FinalProject.zip`.
  - The README gives the public URL.
- **Defence:** an investor-style pitch and live demo, then technical questions to any member about any part of the code, including AI-written code.
- Technical choices outside what is taught in class need the instructor's agreement **before** building on them.

## 4. Required components and acceptance checks

1. **AI integration:** the model does real work. Any output the code acts on comes back as validated structured output, never parsed text.
2. **Conversational agent:** a multi-turn conversation that uses earlier context. The agent **chooses** tools and chains calls; a fixed code-driven workflow does not count.
3. **Tools:** team-written functions that read or change app state, each documented in `docs/TOOLS.md` (purpose, parameters, return value, failures). Failures return a result the agent can act on. Safe transient failures are retried. A tool that deletes or overwrites asks the user first unless the change can be undone.
4. **Documents:** the app reads documents (e.g., operational rules as PDF or text) and uses their content for something the user cares about, as a core feature or to ground answers. An upload control that does nothing does not count. Team choice, beyond the course: answers cite the document they used.
5. **Layered architecture:** interface, logic, AI provider access, tools, configuration, prompts and schemas are kept apart. The interface never builds prompts or makes decisions, and changing the model means editing one line.
6. **Tracing:** one trace per user request, including in the deployed app, with a span for every model and tool call. Each trace shows the model, latency, tokens, errors and handled failures, the outcome and the conversation ID. Document whether prompts and responses are logged and how long traces are kept. The team must be able to open the trace of a failure it found and show what it changed because of it.

**Compliance:** tell users they are interacting with AI (EU AI Act Art. 50), process no identifiable patient data, and follow GDPR and the providers' terms.

**Evaluation set:** 10–20 cases with expected outputs, scored by a script and rerun after every prompt or model change. The course only recommends it; this team treats it as required.

**Deliverables:**
- `README.md`: setup from a fresh clone, run instructions, deployment, limitations, credits.
- `docs/ARCHITECTURE.md`: the layers, data flows and trade-offs.
- `docs/TOOLS.md`
- `.env.example`
- the lockfile
- tests

**Before submitting:** clone into an empty folder and follow the README.

## 5. Data

- Source: DataSF dataset `nuek-vuh3`, SF Fire Department and EMS Dispatched Calls for Service (`https://data.sf.gov/resource/nuek-vuh3.json`).
- Rows are **unit responses**, not incidents. A January 2025 audit found 33,196 response rows for 16,374 incidents. **Never count response rows as demand**: deduplicate at incident level, and keep a separate response table for resource analysis.
- `MEDIC`, `BLS` and `PRIVATE` are candidate ambulance types; their eligibility is unverified. In the January 2025 data, of 12,697 such rows one lacked `available_dttm` and 85 had negative dispatch-to-available durations. These findings are period-specific, so validate chronology and coverage before modelling.
- Incident coordinates are not vehicle GPS positions. The data does not show full rosters, shifts or availability.
- Keep **observed facts**, **derived estimates** and **synthetic assumptions** separate in data, API responses, UI and evaluation.
- Use reproducible, date-scoped API extracts saved as local snapshots, never a full download at app startup. Record the source, extraction date, filters, transformations and quality checks. Data files stay out of Git (`data/`).
- The dataset is live and updated daily, so record each snapshot's extraction date and the source's `data_as_of`. The API's column set varies between queries (36 or 37 columns), so extracts use an explicit column list. Timestamps are local San Francisco time without a time zone; take care around daylight-saving changes.
- San Francisco patterns do not transfer to Lisbon. A Lisbon scenario must be labelled as an assumption-driven demonstration.

## 6. MVP and stack

Build one end-to-end interaction first:
1. The user describes a simulated emergency.
2. The agent calls tools to inspect available units and compare them.
3. Deterministic Python computes eligibility, ETA and coverage impact; the LLM never invents these figures.
4. The agent presents the options with their assumptions.
5. In a follow-up ("unit X is unavailable"), the agent keeps the context and updates the result.
6. In a relevant scenario, the agent consults an uploaded rules document.

Use simple baselines before any optimisation.

**Stack:**
- Python 3.12, `uv` with exact pins and a committed `uv.lock`, Streamlit.
- Anthropic Python SDK, isolated in one layer. The model ID is `LLM_MODEL` in `src/secondsmatter/config.py`.
- Langfuse Cloud EU for tracing (planned).
- pandas and Parquet for data; SQLite only if persistent state is needed.
- Deployment on Streamlit Community Cloud, with `streamlit_app.py` as the entrypoint.

Add a dependency only when a feature uses it. Avoid unneeded frameworks and infrastructure. The demo must not depend on a live external data request.

## 7. Repository layout and commands

The repository root holds only these files: `README.md`, `CLAUDE.md`, `streamlit_app.py`, `pyproject.toml`, `uv.lock`, `.env.example` and `.gitignore`. Everything else lives in a folder:

| Folder | Contents |
|---|---|
| `src/secondsmatter/` | Application code |
| `tests/` | Tests |
| `notebooks/` | Exploration only; reusable code moves to `src/` |
| `docs/` | Project docs; course documents in `docs/reference/` |
| `data/` | Local only, not in Git |

Do not create empty placeholder files or folders. Add a module only when a feature needs it, and announce every new file.

```bash
uv sync                                  # create/update .venv (local only, not in Git)
uv run streamlit run streamlit_app.py    # run the app
uv run pytest                            # run the tests
```

## 8. Working rules

- **Git:** commit directly to `main`. No feature branches, pull requests or colleague review are required. Pull before starting, and write short commit messages in English. Claude asks the user in chat before committing or pushing.
- **Language:** code, docs and commit messages are in English. When a team member writes in Portuguese, reply in Portuguese.
- Inspect the repo before changing it, and don't assume files exist. Explain the plan briefly, then make the smallest useful increment without breaking working behaviour.
- Typed, documented tool contracts; validated inputs; explicit failure handling; tests for deterministic calculations.
- Credentials come from environment variables, and `.env.example` lists names only. **Never commit secrets or `.env`.**
- No destructive commands, paid resources or large downloads without explicit approval.
- After each change, report which files changed, how to run or test them, what was verified, and the known limitations.
- After each finished step, update `docs/DEVELOPMENT_STATUS.md` (completed work, current status, next recommended step).
- Prefer readable, explainable code. Every member must be able to defend every line.

**A small, complete, deployed, well-tested application beats an ambitious broken one.**
