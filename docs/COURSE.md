# Course Requirements

What the course asks for. The documents in `docs/reference/` take precedence over this
file and over `CLAUDE.md`:

- `Project_Guidelines.pdf`
- `Technical_Proposal_Guidelines.pdf`
- `Proposal_Week_03.pdf`
- `SecondsMatter_Proposal.pdf` — the team's own starting concept, not a commitment
- `README_TEMPLATE.md` — referenced by the guidelines, not yet in the repo

Nothing here is an instructor approval. When a requirement is unclear, ask the
instructor rather than inferring one.

## Deadlines

**Technical proposal — 6 Dec 2026, 23:59.** One PDF named
`TeamName_TechnicalProposal.pdf`, with the 10 sections of the guidelines in order, no
code and no placeholder sections. The final delivery is compared against its section 7
(scope) and section 8 (plan), so it should commit only to what can be built.

**Final submission — 3 Jan 2027, 23:59.** Late penalties out of 20: −2, −5 and −9 points
for days 1–3; after that it is not accepted.

- Only the **default branch** counts.
- `mb-cardoso` must be a collaborator on the repository.
- Moodle gets the same code as `TeamName_FinalProject.zip`.
- The README gives the public URL.

**Defence.** An investor-style pitch and live demo, then technical questions to any
member about any part of the code, including AI-written code.

## Required components

1. **AI integration** — the model does real work. Any output the code acts on comes back
   as validated structured output, not parsed text.
2. **Conversational agent** — a multi-turn conversation that uses earlier context. The
   agent chooses tools and chains calls; a fixed code-driven workflow does not count.
3. **Tools** — team-written functions that read or change app state, each documented in
   `docs/TOOLS.md` (purpose, parameters, return value, failures). Failures return a
   result the agent can act on.
4. **Documents** — the app reads documents (for example operational rules as PDF or
   text) and uses their content for something the user cares about, as a core feature or
   to ground answers. An upload control that does nothing does not count.
5. **Layered architecture** — interface, logic, AI provider access, tools, configuration
   and prompts are kept apart. The interface does not build prompts or make decisions,
   and changing the model means editing one line.
6. **Tracing** — one trace per user request, including in the deployed app, with a span
   for every model and tool call, showing the model, latency, tokens, errors and handled
   failures, the outcome and the conversation ID. The team must be able to open the trace
   of a failure it found and show what it changed because of it.

**Recommended, not required:** an evaluation set of 10–20 cases with expected outputs,
scored by a script and rerun after prompt or model changes.

## Compliance

- Tell users they are interacting with AI (EU AI Act Art. 50).
- Process no identifiable patient data.
- Follow GDPR and the providers' terms.

## Deliverables

- `README.md` — setup from a fresh clone, run instructions, deployment, limitations,
  credits.
- `docs/ARCHITECTURE.md` — the layers, data flows and trade-offs.
- `docs/TOOLS.md`
- `.env.example`
- the lockfile
- tests

**Before submitting:** clone into an empty folder and follow the README.
