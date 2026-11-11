# SecondsMatter

AI-powered decision-support prototype for emergency resource planning and dispatch.
NOVA IMS BSc Data Science Capstone Project, 2026/2027.

> **Academic simulation only.** SecondsMatter is a research prototype, not a real
> emergency dispatch system. It does not send dispatch instructions or assess clinical
> priority, and its fleet availability is simulated. Users interact with an AI system.

**Status:** project skeleton. The agent, tools, data pipeline and tracing are not built yet.

**Public URL:** https://secondsmatter.streamlit.app/

## Setup from a fresh clone

Requirements: [uv](https://docs.astral.sh/uv/). It installs Python 3.12 automatically if it is missing.

```bash
git clone https://github.com/pedromariaanf-a11y/Projeto-de-curso.git
cd Projeto-de-curso
uv sync
cp .env.example .env   # then fill in ANTHROPIC_API_KEY
```

**About the environment.** `uv sync` creates `.venv/`, a private Python 3.12 with the exact
library versions from `uv.lock`, separate from any other Python on your computer. Run it again
after every `git pull`. `uv run <command>` runs a command inside `.venv`, so there is no need to
activate it; calling `python` or `pip` directly may use a different Python.

## Run

```bash
uv run streamlit run streamlit_app.py
```

## Test

```bash
uv run pytest
```

## Project layout

| Path | Purpose |
|---|---|
| `streamlit_app.py` | Interface only: renders the page and calls `src/secondsmatter/` |
| `src/secondsmatter/config.py` | Settings from environment variables, including the model ID |
| `tests/` | Automated tests |
| `notebooks/` | Exploratory analysis (reusable code moves to `src/`) |
| `docs/reference/` | Course guidelines and project proposals |
| `pyproject.toml`, `uv.lock` | Dependencies pinned with uv (must stay at the root) |
| `.env.example` | Names of required environment variables, no values |
| `data/`, `.venv/` | Local only, never committed: datasets and the Python environment |

## Data

San Francisco Fire Department and EMS Dispatched Calls for Service
([DataSF `nuek-vuh3`](https://data.sf.gov/resource/nuek-vuh3.json)). Data files are kept
out of Git in `data/`.

Build the local data for one year (downloads once, a few minutes, then reuses the file):

```bash
uv run python -m secondsmatter.data 2025
```

This filters on `received_dttm` within the calendar year, requests a fixed list of 24 columns
(no street address), and writes to `data/`:

| File | Contents |
|---|---|
| `sf_ems_2025_raw.parquet` | The rows exactly as the API returned them (text) |
| `sf_ems_2025_info.json` | Source, filter, columns, extraction time, latest `data_as_of`, quality checks |
| `responses_2025.parquet` | One row per **unit sent**: times, unit type, durations in minutes |
| `incidents_2025.parquet` | One row per **incident** (demand): call type, location, units and ambulances sent |

Source rows are unit responses, so demand is counted in `incidents`, never in `responses`.
Times are local San Francisco time without a time zone. `is_ambulance` (unit types `MEDIC`,
`BLS`, `PRIVATE`) is a project assumption; `als_unit` is observed in the source. The dataset
is updated daily, so delete the raw file and rerun to get fresher data.

## Deployment

Deployed on Streamlit Community Cloud from the `main` branch, with `streamlit_app.py` as
the entrypoint and Python 3.12 (set under Advanced settings). Dependencies are installed
from `uv.lock`. Every push to `main` redeploys the app. Secrets are set in the app's
Secrets settings, using the names in `.env.example`.

## Credits

None yet.
