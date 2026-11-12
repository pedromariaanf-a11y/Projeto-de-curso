# SecondsMatter — Instructions for Claude Code

## Project

SecondsMatter is a NOVA IMS BSc Data Science capstone project (2026/2027, four-person
team): an AI-powered decision-support prototype for emergency resource planning and
dispatch. The team are students learning while they build it. The project is at an early
stage — most design choices are still open.

**Safety boundary:** this is an academic simulation, not a real dispatch system. It must
not send real dispatch instructions, determine clinical priority, claim operational
readiness, or present synthetic results as real-world performance. Simulated information
is labelled as such, and a human stays in control of every simulated decision. Tell users
they are interacting with AI; process no identifiable patient data.

## How to work with the team

1. **Recommend the next step.** Name the single best next step, why it is the best one
   now, and what is deliberately left for later. Wait for agreement before starting it.
2. **Explain before doing.** Say which files will change, the approach, and any new
   concept in plain language. Explain a technical term the first time it is used.
3. **One small step at a time.** Small enough to review and understand. Never chain
   steps without checking in. Stop after each step.
4. **Explain the code.** The main idea, the key functions, and why this design. Comments
   only where the logic is not obvious.
5. **Close each step.** What changed, how to run or test it, what to understand in order
   to defend it, and the recommended next step.

Every member must be able to defend every line at the defence, including AI-written code.

## How to plan

- Plan the next step, not the project. Choose the smallest increment that makes something
  work end to end.
- **Do not record decisions about the future in this file.** When a choice comes up,
  present the options and the trade-offs, let the team decide, and write the decision in
  `docs/DEVELOPMENT_STATUS.md` once it has been made and tried.
- Ask when unsure. Never invent a course requirement or assume the instructor approved
  something.
- The course documents in `docs/reference/` take precedence over this file.
- Dates: technical proposal 6 Dec 2026, final submission 3 Jan 2027. Details in
  `docs/COURSE.md`.
- Six components must exist by the end: AI integration, a conversational agent,
  team-written tools, document reading, a layered architecture, and tracing. How each one
  is built is open.
- Prefer simple baselines, the fewest files, the least infrastructure. A small, complete,
  well-tested application beats an ambitious broken one.

## Repository

The root holds only `README.md`, `CLAUDE.md`, `streamlit_app.py`, `pyproject.toml`,
`uv.lock`, `.env.example` and `.gitignore`. Code in `src/secondsmatter/`, tests in
`tests/`, exploration in `notebooks/`, docs in `docs/` (course PDFs in `docs/reference/`),
local data in `data/` (never in Git). Add a file or module only when a feature needs it,
and announce every new one. No empty placeholders.

```bash
uv sync                                  # create/update .venv
uv run streamlit run streamlit_app.py    # run the app
uv run pytest                            # run the tests
```

Python 3.12, `uv` with a committed `uv.lock`, Streamlit, Anthropic Python SDK. Add a
dependency only when a feature uses it.

## Working rules

- **Git:** commit directly to `main`; no branches or pull requests. Pull before starting.
  Short commit messages in English. Ask in chat before committing or pushing.
- **Language:** code, docs and commit messages in English. Reply in Portuguese when a
  team member writes in Portuguese.
- Inspect the repo before changing it; don't assume files exist.
- Credentials come from environment variables; `.env.example` lists names only. Never
  commit secrets or `.env`.
- No destructive commands, paid resources or large downloads without approval.
- Tests for the core deterministic logic, not for everything.
- The data has non-obvious traps — response rows are not incidents. Read `docs/DATA.md`
  before touching data code.
- After each change, report which files changed, how to run or test them, what was
  verified, and the known limitations.
- After each finished step, update `docs/DEVELOPMENT_STATUS.md`.
