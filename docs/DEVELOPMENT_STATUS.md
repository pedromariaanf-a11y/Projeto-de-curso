# Development Status

_Last updated: 2026-11-12. Update this file whenever a step is finished._

This file records what is done, what is open and what comes next. Course requirements are
in `docs/COURSE.md`; data notes are in `docs/DATA.md`.

## Deadlines

| Milestone | Date | Status |
|---|---|---|
| Technical proposal (`TeamName_TechnicalProposal.pdf`) | 6 Dec 2026, 23:59 | Not started |
| Final submission (repo + Moodle zip) | 3 Jan 2027, 23:59 | In progress |

## Done

- **Packaging:** `uv` + Python 3.12, exact pins, `uv.lock` committed.
- **Config** (`src/secondsmatter/config.py`): the model ID is one line; the API key is checked for presence but never stored.
- **Interface** (`streamlit_app.py`): AI-interaction disclosure (EU AI Act Art. 50) and the "academic simulation only" warning. Chat input still disabled.
- **Deployed:** https://secondsmatter.streamlit.app/ — every push to `main` redeploys.
- **Data** (`src/secondsmatter/data.py`, `uv run python -m secondsmatter.data 2025`): downloads one year from DataSF `nuek-vuh3` and builds two local Parquet tables in `data/` (not in Git). 2025 snapshot: **369,089 responses** (one row per unit sent) and **183,325 incidents** (one row per emergency), matching the API's own counts. Of the responses, 124 distinct ambulance units; median 8.2 min dispatch-to-on-scene and 70.2 min busy. Provenance and quality go to `data/sf_ems_2025_info.json`.
- **Notebooks:** `ipykernel==7.4.0` in its own `notebooks` group, not in `dev`, so a plain `uv sync` (what the deployment runs) leaves the 22-package Jupyter stack out. `notebooks/01_explore_sf_ems_api.ipynb` asks for the kernel **SecondsMatter (uv)**, which points at `.venv`, so notebooks use the project's own package versions. The kernel is registered per machine, so each member runs these two commands once:
  ```
  uv sync --group notebooks
  uv run python -m ipykernel install --user --name secondsmatter --display-name "SecondsMatter (uv)"
  ```
- **Tests:** 3, passing with `uv run pytest`.

## Required components

| Component | Status |
|---|---|
| 1. AI integration (structured output) | Not started: no model SDK in the dependencies |
| 2. Conversational agent | Not started: chat input disabled |
| 3. Tools + `docs/TOOLS.md` | Not started |
| 4. Documents | Not started |
| 5. Layered architecture | Started: config, data and interface are separate |
| 6. Tracing | Not started |
| Evaluation set (10–20 cases) | Recommended, not required — see Open questions |
| `docs/ARCHITECTURE.md` | Not started |

## Known limitations

- Ambulance types (`MEDIC`, `BLS`, `PRIVATE`) are an **unverified assumption**; `als_unit` is the observed field.
- 1,326 of 369,089 responses (0.4%) have impossible negative durations, stored as empty. Quality findings are for 2025 only.
- The source has no fleet rosters, shifts or vehicle GPS, so unit availability will be **simulated**.
- No API key on the deployed app, so the sidebar says the key is not set. Expected until the agent exists.
- No written instructor feedback on the Week 3 proposal; section 3 of the technical proposal must say so.
- `notebooks/01_explore_sf_ems_api.ipynb` is kept only as a record of the first exploration; its logic now lives in `data.py`. Opening it without the two commands above gives a missing-kernel warning.

## Open questions

Choices that are **not** decided. They used to sit in `CLAUDE.md` as if they were
settled; they belong here until the team picks one and tries it. Record the answer under
"Done" once it works.

| Question | Notes |
|---|---|
| Tracing provider | Langfuse Cloud EU was pencilled in but never tried. Nothing installed yet. |
| Evaluation set | The course only recommends it. Build 10–20 cases, or skip? |
| Document grounding | Must answers cite which document they used, or is reading it enough? |
| Trace privacy | Do we log prompts and responses, and for how long do traces live? |
| Persistent state | Parquet snapshots work for data. Is SQLite needed for anything? |
| Architecture layers | How many layers the course requirement actually needs here. |
| Tool failure handling | Which failures are retried, and how many times. |
| Planning scope | Are demand forecasting and relocations in scope at all, or dispatch only? |
| MVP interaction | The exact end-to-end flow the demo shows — to be designed, not assumed. |

## Next step

**Simulation:** a synthetic fleet built from the real 2025 ambulance units, plus deterministic eligibility, ETA and coverage-impact calculations, with tests. It also decides which small summary tables the deployed app reads (those get committed, with a one-line exception added to `CLAUDE.md`). The agent's tools need these numbers before the agent itself is worth building.
