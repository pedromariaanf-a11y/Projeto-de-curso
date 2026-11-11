# Development Status

_Last updated: 2026-11-11 (commit `db90f6e`). Update this file whenever a step is finished._

Only work that can be checked in the repository is listed as done.

## Deadlines

| Milestone | Date | Status |
|---|---|---|
| Technical proposal (`TeamName_TechnicalProposal.pdf`) | 6 Dec 2026, 23:59 | Not started |
| Final submission (repo + Moodle zip) | 3 Jan 2027, 23:59 | In progress |

## Completed work

- **Repository setup**
  - The course documents are in `docs/reference/`.
  - `.gitignore` excludes `.env`, `.venv/` and `data/`.
  - The root contains only the essential files.
- **Packaging**
  - The `uv` project uses Python 3.12, with exact pins (`streamlit==1.67.0`, `python-dotenv==1.2.4`, and `pytest==9.2.0` for development) and a committed `uv.lock`.
- **Configuration layer** (`src/secondsmatter/config.py`)
  - Settings are read from environment variables.
  - The model ID is set in one line (`LLM_MODEL = "claude-opus-5-5"`).
  - The API key is checked for presence but never stored.
- **Interface** (`streamlit_app.py`)
  - The page shows the AI-interaction disclosure (EU AI Act Art. 50) and the "academic simulation only" warning.
  - The sidebar shows the model and whether the key is configured.
  - The chat input is disabled.
- **Tests** (`tests/test_config.py`)
  - 2 tests for the configuration; both pass with `uv run pytest`.
- **Deployment**
  - The app is public at https://secondsmatter.streamlit.app/ (Streamlit Community Cloud, `main` branch, Python 3.12).
  - Every push to `main` redeploys it.
- **Data exploration** (`notebooks/01_explore_sf_ems_api.ipynb`)
  - January 2025 extract from DataSF `nuek-vuh3`: 33,196 response rows, 16,374 incidents, 228 units.
  - Candidate ambulance types: `MEDIC`, `BLS` and `PRIVATE`.
  - Quality checks: 1 missing `available_dttm` and 85 negative busy durations.
- **Docs**
  - `README.md` covers setup, run, test, the project layout and the public URL.
  - `CLAUDE.md` holds the project rules and the teaching-mode working style.

## Current status

The skeleton is deployed. **None of the six required components is implemented yet.**

| Required component | Status |
|---|---|
| 1. AI integration (structured output) | Not started: no model SDK in the dependencies |
| 2. Conversational agent | Not started: chat input disabled |
| 3. Tools + `docs/TOOLS.md` | Not started |
| 4. Documents | Not started |
| 5. Layered architecture | Started: separate config and interface layers |
| 6. Tracing | Not started |
| Evaluation set (10–20 cases) | Not started |
| `docs/ARCHITECTURE.md` | Not started |

## Pending tasks (priority order)

1. **Reproducible data extract:** move the notebook logic into `src/`, fetch a date-scoped API batch, and save it as a local snapshot. Build separate incident and response tables, with tests.
2. **Simulation:** a synthetic fleet, plus deterministic eligibility, ETA and coverage calculations, with tests.
3. **Agent:** an Anthropic SDK tool loop with the first tools and structured outputs.
4. **Tracing:** Langfuse spans for model and tool calls, from the first agent interaction.
5. **Document use:** an uploaded operational-rules document that the agent consults.
6. **Documentation:** `docs/TOOLS.md`, `docs/ARCHITECTURE.md`, and the evaluation set with a scoring script.
7. **Technical proposal:** write it in parallel; due 6 Dec.

## Technical decisions

| Decision | Reason |
|---|---|
| Python 3.12 + `uv` + `uv.lock` | Exact pins are required by the guidelines, and Streamlit Cloud installs from `uv.lock` |
| Streamlit + Streamlit Community Cloud | Taught in class, free public URL, redeploys on every push |
| `src/` package layout | Lets the app and the tests import the same code; the interface stays separate from the logic |
| Model ID in `config.py` | Switching the model means editing one line (a course requirement) |
| Secrets from environment variables | No keys in Git; `.env` locally, Secrets on Streamlit Cloud |
| Commit directly to `main` | Team decision; only `main` counts for grading |
| Add libraries only when a feature uses them | Keeps the setup small and explainable |

## Known issues and limitations

- No API key is set on the deployed app, so the sidebar shows "ANTHROPIC_API_KEY is not set". This is expected until the agent exists.
- `README_TEMPLATE.md`, referenced by the guidelines, is not in the repository.
- The notebook uses `requests` and `pandas`, which are not project dependencies, so it does not run inside the `uv` environment yet.
- The data audit covers January 2025 only; its quality findings are not general.
- The dataset has no fleet rosters, shifts or vehicle GPS positions, so availability will be simulated.
- On one development machine, `uv` could not download its own Python 3.12, and the local Python 3.12 was used instead.

## Next recommended step

**Reproducible data extract (task 1).** The agent's tools need real incident and unit data, and `CLAUDE.md` requires date-scoped, reproducible snapshots kept out of Git. It is the base for steps 2–4.
