# SecondsMatter — Instructions for Claude Code

## 1. Project overview

SecondsMatter is a 2026/2027 NOVA IMS BSc Data Science Capstone Project developed by a four-person team. It is an **AI-powered decision-support prototype for emergency resource planning and dispatch**.

The application should allow users to explore emergency demand, inspect simulated resource availability, compare dispatch options using estimated travel time and remaining geographic coverage, and ask follow-up or hypothetical questions through a conversational AI agent. The original concept includes both **planning** (forecasting demand, analysing coverage, considering relocations) and **dispatch** (comparing resources for an incoming incident). Prioritise a complete, reliable MVP before adding advanced functionality.

**Safety boundary:** This is an academic simulation and research prototype, **not a real emergency dispatch system**. It must not send real dispatch instructions, determine clinical priority, claim operational readiness, or present synthetic results as verified real-world performance. Keep a human in control of simulated decisions and label simulated information clearly.

## 2. Source of truth and deadlines

The official course guidelines take precedence over this file. Course documents live in `docs/reference/`: `Project_Guidelines.pdf` (official guidelines) and `SecondsMatter_Proposal.pdf` (initial proposal). Read them before making architectural or scope decisions. The guidelines also refer to `PROPOSAL_WEEK_03.md`, `TECHNICAL_PROPOSAL_GUIDELINES.md` and `README_TEMPLATE.md`; if these are absent, ask the team to provide them when a requirement is uncertain. The initial proposal describes the starting concept, **not an immutable feature commitment**. Do not invent course requirements or assume something has been approved by the instructor.

- **Technical proposal:** 6 December 2026, 23:59 (problem and solution, member roles, technical blueprint with architecture diagram, realistic scope and timeline). Assessed later against what is delivered, so commit only to what can be built.
- **Final submission:** 3 January 2027, 23:59. Late penalties (out of 20): −2 / −5 / −9 points for days 1–3, then not accepted.
- The final application must run at a **public URL** and be demonstrable during the defence.
- All four team members must be able to explain the entire application, including AI-generated code.

**Submission logistics (from the guidelines):**

- Only the repository's **default branch** counts; work on other branches or committed after the deadline is not part of the submission / is late.
- GitHub user `mb-cardoso` must be a collaborator on the repository.
- Moodle: the same code as a zip named `TeamName_FinalProject.zip`.
- `README.md` follows `README_TEMPLATE.md` (or equivalent), with setup that works on a fresh clone, the deployment note and public URL, and credits for any code taken from other projects.
- Any technical choice outside what is taught in class must be agreed with the instructor **before** building on it.
- Defence: investor-style pitch + live demo, then technical questions to any member about any part of the code.
- Tracing must let the team open the trace of a failure it found and show what it changed because of it.
- The 10–20 case evaluation set is *recommended* by the course; this team treats it as required.

## 3. Mandatory course requirements

Design and implement **all six** required components:

1. **AI integration:** A model performs meaningful application work under prompts and system instructions. Outputs used by code must follow a validated structured schema, not brittle text parsing.
2. **Conversational agent:** The user can hold a multi-turn conversation; the agent uses prior context, **chooses** the application's tools, and can chain tool calls. A fixed code-driven workflow alone is insufficient.
3. **Custom tools:** The agent invokes team-written functions that read or change application state. Document each tool's purpose, parameters, returns, and failures in `docs/TOOLS.md`. Return recoverable errors to the agent; retry only safe transient failures; obtain confirmation before non-undoable destructive changes.
4. **Document use:** Users can provide relevant documents (for example, PDF or text operational rules for the simulation), and the application uses their contents meaningfully, with clear attribution when appropriate. Document processing cannot be a decorative upload control.
5. **Layered architecture:** Separate interface, application logic, AI provider access, tools, configuration, prompts, and schemas. The interface must not build prompts or own decision logic. Switching models should be a small, centralised configuration change.
6. **Tracing:** Produce one trace per user request, with spans for model and tool calls, model identity, latency, token use, errors/handled failures, request outcome, and conversation association. Include the deployed app. Decide and document whether prompts/responses are logged and how long traces are retained.

Also disclose that users interact with AI, avoid processing identifiable patient data, and follow applicable GDPR, AI Act, and service-provider requirements. Create a small **10–20 case** agent evaluation set and rerun it after meaningful prompt/model changes.

## 4. Data strategy and known limitations

- Main candidate source: San Francisco Fire Department and EMS Dispatched Calls for Service, DataSF dataset `nuek-vuh3`.
- API endpoint: `https://data.sf.gov/resource/nuek-vuh3.json`.
- A preliminary January 2025 audit retrieved **33,196 unit-response rows** and **16,374 distinct incident IDs**. There are multiple responses per incident; **never count response rows as incident demand**.
- `unit_id`, `unit_type`, `received_dttm`, `dispatch_dttm`, `available_dttm`, and `case_location` were observed. `MEDIC`, `BLS`, and `PRIVATE` are candidate ambulance-related unit types, but operational eligibility must be verified.
- Of 12,697 candidate ambulance-related response rows in that month, one lacked `available_dttm` and 85 had negative dispatch-to-availability durations. These findings are **preliminary, period-specific**, not general guarantees of quality.
- Public incident coordinates are not full historical vehicle GPS positions. The dataset does **not** establish complete fleet rosters, shifts, or vehicle availability outside recorded assignments.
- Separate **observed historical facts**, **derived estimates**, and **synthetic simulation assumptions** in the data model, API responses, UI, and evaluation.
- For demand modelling, deduplicate at incident level. Preserve a separate response/assignment table for resource analysis. Validate timestamp chronology and geographic coverage before fitting models.
- Fetch reproducible, date-scoped API batches; do not download the full dataset on app startup. Cache or snapshot modelling data locally for repeatable testing. Record source, extraction date, date filters, transformations, and quality checks. Keep large data files out of Git.
- Do **not** assume San Francisco patterns transfer directly to Lisbon. A Lisbon scenario would be a separately labelled, assumption-driven demonstration unless suitable local data becomes available.

## 5. Recommended MVP and implementation choices

Build **one complete end-to-end interaction** first:

1. A user describes a simulated emergency and asks which eligible resource to dispatch.
2. The agent calls tools to inspect simulated available units and compare alternatives.
3. Deterministic Python code calculates eligibility, estimated arrival time, and coverage impact; the LLM does **not** invent these figures.
4. The agent presents clear options with assumptions and limitations.
5. In a follow-up, the user changes an assumption (e.g., a unit becomes unavailable); the agent retains context, calls the relevant tools, and explains the updated result.
6. The agent can consult a user-provided operational-rules document in a relevant scenario.

Implement planning-mode demand forecasting and relocation recommendations incrementally after the essential agent, tools, simulation, document handling, tracing, and deployment work. Use simple baselines before more advanced optimisation. Do not promise more in the technical proposal than can be delivered and defended.

**Preferred stack (unless an existing repository decision or justified alternative suggests otherwise):**

- Python backend, Streamlit interface.
- Anthropic's **current** Python SDK for the application LLM; keep provider-specific code isolated. Claude Code is the development assistant, not automatically the runtime API.
- Langfuse Cloud EU for tracing (or a justified equivalent).
- `uv` with a committed lockfile and exactly pinned dependencies.
- Pandas and Parquet for data preparation; SQLite only when persistent application state is needed.
- Mapping and routing libraries only when a tested use case requires them.
- Public deployment early, preferably Streamlit Community Cloud.

Avoid unnecessary frameworks, speculative dependencies, and complex infrastructure. Never rely on a live external data request for the core demonstration if a reproducible local snapshot can be used.

## 6. Codebase and collaboration rules

Before making changes:

- Inspect the existing repository, docs, and tests. **Do not assume files or features exist.**
- Explain briefly what you plan to change and why; implement the smallest useful increment.
- Preserve existing functioning behaviour unless a change is explicitly requested.
- Place reusable implementation in `src/` modules rather than copying logic between notebooks and the UI.
- Keep tool contracts typed and documented. Validate inputs, handle failures explicitly, and write tests for critical deterministic calculations.
- Use environment variables for credentials; maintain `.env.example` with variable names only. **Never commit secrets or `.env` files.**
- Keep datasets, caches, generated model artefacts, and large exports out of Git unless deliberately approved.
- Do not run destructive shell commands, create paid resources, trigger large downloads, or commit/push without explicit approval.
- Whenever you finish a change, state which files changed, how to run/test it, what was verified, and any known limitations.
- Prefer readable and explainable code over clever abstractions. The entire team must be able to defend every choice.

## 7. Documentation and acceptance checks

Maintain these deliverables as the project evolves:

- `README.md` — purpose, setup from a fresh clone, how to run, deployment URL and deployment process, limitations, third-party credits.
- `docs/ARCHITECTURE.md` — layers, data flows, component choices, and trade-offs.
- `docs/TOOLS.md` — every agent tool's purpose, parameters, outputs, failures, and side effects.
- `.env.example` — required environment variables, with no values or secrets.
- Reproducible dependency lockfile; tests and agent evaluation cases.

Before final submission, verify: multi-turn tool selection/chaining, meaningful document use, structured outputs, safe tool failure handling, complete per-request tracing in deployment, reproducible data preparation, clear simulated-data disclosures, public accessibility, and setup from a fresh repository clone. Follow the official GitHub/Moodle submission instructions and deadlines.

**Guiding principle: A small, complete, deployed, well-tested AI application is better than an ambitious but broken one.**
