# Data

## Source

DataSF dataset `nuek-vuh3`, San Francisco Fire Department and EMS Dispatched Calls for
Service: `https://data.sf.gov/resource/nuek-vuh3.json`

The dataset is live and updated daily. Extracts are date-scoped, reproducible and saved
as local snapshots in `data/` (never in Git); the app never downloads at startup, and the
demo must not depend on a live external request. Each snapshot records its source,
extraction date, the source's own `data_as_of`, filters, transformations and quality
checks (see `data/sf_ems_<year>_info.json`).

Build the current extract with:

```bash
uv run python -m secondsmatter.data 2025
```

## The trap: rows are unit responses, not incidents

Each row is **one unit sent to an emergency**, so several rows can describe the same
emergency. Counting rows as demand overcounts it. Deduplicate at incident level for
demand, and keep the response table separately for resource analysis.

| 2025 snapshot | Count |
|---|---|
| Responses (one row per unit sent) | 369,089 |
| Incidents (one row per emergency) | 183,325 |

Both match the API's own counts. An earlier January 2025 audit found the same pattern at
a smaller scale: 33,196 response rows for 16,374 incidents.

## What the data does not contain

- Incident coordinates are **not** vehicle GPS positions.
- There are no fleet rosters, shifts or availability, so unit availability has to be
  simulated.

## Unverified assumptions

- `MEDIC`, `BLS` and `PRIVATE` are *candidate* ambulance types; their eligibility is
  unverified. `als_unit` is the observed field.
- The 2025 snapshot has 124 distinct ambulance units, a median of 8.2 min from dispatch
  to on-scene and 70.2 min busy.

## Quality findings (period-specific — revalidate for any other period)

- 2025: 1,326 of 369,089 responses (0.4%) have impossible negative durations, stored as
  empty.
- January 2025: of 12,697 ambulance-type rows, one lacked `available_dttm` and 85 had
  negative dispatch-to-available durations.

Validate chronology and coverage before modelling.

## Rules when working with this data

- Keep **observed facts**, **derived estimates** and **synthetic assumptions** separate,
  and label them wherever they are shown to the user.
- The API's column set varies between queries (36 or 37 columns), so extracts use an
  explicit column list.
- Timestamps are local San Francisco time with no time zone; take care around
  daylight-saving changes.
- San Francisco patterns do not transfer to Lisbon. Any Lisbon scenario is an
  assumption-driven demonstration and must say so.
