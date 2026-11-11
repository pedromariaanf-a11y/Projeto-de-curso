# SecondsMatter

AI-powered decision-support prototype for emergency resource planning and dispatch.
NOVA IMS BSc Data Science Capstone Project, 2026/2027.

> **Academic simulation only.** SecondsMatter is a research prototype, not a real
> emergency dispatch system. It does not send dispatch instructions or assess clinical
> priority, and its fleet availability is simulated. Users interact with an AI system.

**Status:** project skeleton. The agent, tools, data pipeline and tracing are not built yet.

**Public URL:** not deployed yet.

## Setup from a fresh clone

Requirements: [uv](https://docs.astral.sh/uv/) and Python 3.12.

```bash
git clone https://github.com/pedromariaanf-a11y/Projeto-de-curso.git
cd Projeto-de-curso
uv sync
cp .env.example .env   # then fill in ANTHROPIC_API_KEY
```

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

## Deployment

Planned on Streamlit Community Cloud, with `streamlit_app.py` as the entrypoint and
secrets set under the app's Secrets settings using the names in `.env.example`.

## Credits

None yet.
