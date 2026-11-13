"""Data layer: DataSF records -> `incidents` and `responses` tables.

Source rows are unit responses, not incidents: one emergency can have several
rows, one per unit sent. Demand is counted in `incidents`, never in `responses`.
Times are kept as local San Francisco time without a time zone, as the source
gives them.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://data.sf.gov/resource/nuek-vuh3.json"
DATA_DIR = Path("data")
PAGE_SIZE = 50_000

# The columns requested from the API. A fixed list, because the API's own
# column set varies between queries. The street address is left out on purpose.
COLUMNS = [
    "rowid", "incident_number", "call_number", "unit_id", "unit_type", "als_unit",
    "unit_sequence_in_call_dispatch", "call_type", "call_type_group",
    "original_priority", "final_priority", "call_final_disposition",
    "received_dttm", "dispatch_dttm", "response_dttm", "on_scene_dttm",
    "transport_dttm", "hospital_dttm", "available_dttm",
    "station_area", "battalion", "neighborhoods_analysis_boundaries",
    "case_location", "data_as_of",
]
TIME_COLUMNS = [c for c in COLUMNS if c.endswith("_dttm")]

# ASSUMPTION (not verified): the unit types we treat as dispatchable ambulances.
AMBULANCE_TYPES = ("MEDIC", "BLS", "PRIVATE")


def _get(session, params: dict) -> list[dict]:
    """One API request. Any failure stops the download; run it again."""
    response = session.get(API_URL, params=params, timeout=120)
    response.raise_for_status()
    return response.json()


def _as_text(value):
    """Store every raw value as text; booleans and objects become JSON text."""
    if value is None or isinstance(value, str):
        return value
    return json.dumps(value)


def download(year: int, data_dir: Path = DATA_DIR, session=None) -> Path:
    """Download one year of DataSF rows and save them unchanged, plus an info file.

    Files are written only when every row arrived, so a failed download leaves
    nothing behind. Returns the path of the raw Parquet file.
    """
    session = session or requests.Session()
    where = (
        f"received_dttm >= '{year}-01-01T00:00:00' "
        f"AND received_dttm < '{year + 1}-01-01T00:00:00'"
    )

    expected = int(_get(session, {"$select": "count(*) as n", "$where": where})[0]["n"])
    if expected == 0:
        raise RuntimeError(f"No rows found for {year}")

    rows = []
    while len(rows) < expected:
        page = _get(session, {
            "$select": ",".join(COLUMNS),
            "$where": where,
            "$order": "rowid",  # a stable order, so pages never overlap or skip rows
            "$limit": PAGE_SIZE,
            "$offset": len(rows),
        })
        if not page:
            break
        rows.extend(page)
        print(f"Downloaded {len(rows):,} of {expected:,} rows")

    if len(rows) != expected:
        raise RuntimeError(
            f"Expected {expected} rows for {year} but received {len(rows)}. "
            "The source may have changed during the download; run it again."
        )

    raw = pd.DataFrame([{c: _as_text(row.get(c)) for c in COLUMNS} for row in rows])
    data_dir.mkdir(parents=True, exist_ok=True)
    raw_path = data_dir / f"sf_ems_{year}_raw.parquet"
    raw.to_parquet(raw_path, index=False)

    info = {
        "source": API_URL,
        "filter": where,
        "columns": COLUMNS,
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_as_of_max": raw["data_as_of"].max(),
        "rows": len(raw),
    }
    info_path = data_dir / f"sf_ems_{year}_info.json"
    info_path.write_text(json.dumps(info, indent=2), encoding="utf-8")
    return raw_path


def _coordinates(location) -> tuple[float, float]:
    """Read (latitude, longitude) from the API's point text; missing -> NaN."""
    if not isinstance(location, str):
        return float("nan"), float("nan")
    longitude, latitude = json.loads(location)["coordinates"]
    return latitude, longitude


def make_tables(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Build (incidents, responses, quality) from raw rows stored as text.

    Pure function: no files, no network. Bad values never stop the build;
    they become empty and are counted in `quality`.
    """
    missing = [c for c in COLUMNS if c not in raw.columns]
    if missing:
        raise ValueError(f"Missing column(s) in raw data: {', '.join(missing)}")

    responses = raw[COLUMNS].copy()

    # Text -> real dates. A time that cannot be read becomes empty (NaT).
    for column in TIME_COLUMNS:
        responses[column] = pd.to_datetime(
            responses[column], format="ISO8601", errors="coerce"
        )

    responses["als_unit"] = responses["als_unit"] == "true"  # observed
    responses["is_ambulance"] = responses["unit_type"].isin(AMBULANCE_TYPES)  # assumption
    responses["unit_sequence_in_call_dispatch"] = pd.to_numeric(
        responses["unit_sequence_in_call_dispatch"], errors="coerce"
    )
    points = [_coordinates(value) for value in responses["case_location"]]
    responses["latitude"] = [lat for lat, _ in points]
    responses["longitude"] = [lon for _, lon in points]
    responses = responses.rename(columns={"neighborhoods_analysis_boundaries": "neighborhood"})

    # Derived durations, in minutes. Negative ones are impossible, so they become empty.
    to_on_scene = (
        responses["on_scene_dttm"] - responses["dispatch_dttm"]
    ).dt.total_seconds() / 60
    busy = (
        responses["available_dttm"] - responses["dispatch_dttm"]
    ).dt.total_seconds() / 60
    responses["minutes_to_on_scene"] = to_on_scene.where(to_on_scene >= 0)
    responses["minutes_busy"] = busy.where(busy >= 0)

    responses = responses.drop(columns=["case_location", "data_as_of"])

    # One row per incident. Details come from the first dispatched unit
    # ("first" skips empty values, so a missing location is taken from the next unit).
    incidents = (
        responses.sort_values(["incident_number", "unit_sequence_in_call_dispatch"])
        .groupby("incident_number", as_index=False)
        .agg(
            received_dttm=("received_dttm", "min"),
            call_type=("call_type", "first"),
            call_type_group=("call_type_group", "first"),
            final_priority=("final_priority", "first"),
            station_area=("station_area", "first"),
            neighborhood=("neighborhood", "first"),
            latitude=("latitude", "first"),
            longitude=("longitude", "first"),
            units_sent=("unit_id", "size"),
            ambulances_sent=("is_ambulance", "sum"),
        )
    )

    quality = {
        "rows": len(responses),
        "incidents": len(incidents),
        "missing_coordinates": int(responses["latitude"].isna().sum()),
        "missing_available_dttm": int(raw["available_dttm"].isna().sum()),
        "negative_durations": int(((to_on_scene < 0) | (busy < 0)).sum()),
    }
    return incidents, responses, quality


def make_fleet(responses: pd.DataFrame) -> pd.DataFrame:
    """One row per ambulance unit, measured from its 2025 responses (nothing simulated).

    The data has no home base for a unit, and the care level belongs to the shift,
    not the vehicle, so `als_share` is the share of responses with advanced care.
    """
    ambulances = responses[responses["is_ambulance"]]
    return (
        ambulances.groupby("unit_id", as_index=False)
        .agg(
            unit_type=("unit_type", "first"),
            responses=("unit_id", "size"),
            als_share=("als_unit", "mean"),  # True counts as 1, so the mean is the share
            first_seen=("dispatch_dttm", "min"),
            last_seen=("dispatch_dttm", "max"),
            median_minutes_to_on_scene=("minutes_to_on_scene", "median"),
            median_minutes_busy=("minutes_busy", "median"),
        )
        .sort_values("responses", ascending=False, ignore_index=True)
    )


def build_tables(year: int, data_dir: Path = DATA_DIR) -> dict:
    """Raw file -> incidents, responses and fleet Parquet files; quality saved in the info file."""
    raw_path = data_dir / f"sf_ems_{year}_raw.parquet"
    if not raw_path.exists():
        raise FileNotFoundError(f"{raw_path} not found; download the data first")

    incidents, responses, quality = make_tables(pd.read_parquet(raw_path))
    incidents.to_parquet(data_dir / f"incidents_{year}.parquet", index=False)
    responses.to_parquet(data_dir / f"responses_{year}.parquet", index=False)
    make_fleet(responses).to_parquet(data_dir / f"fleet_{year}.parquet", index=False)

    info_path = data_dir / f"sf_ems_{year}_info.json"
    info = json.loads(info_path.read_text(encoding="utf-8")) if info_path.exists() else {}
    info["quality"] = quality
    info_path.write_text(json.dumps(info, indent=2), encoding="utf-8")
    return quality


def main() -> None:
    """Command line: `uv run python -m secondsmatter.data 2025`."""
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python -m secondsmatter.data <year>, e.g. 2025")
    year = int(sys.argv[1])

    raw_path = DATA_DIR / f"sf_ems_{year}_raw.parquet"
    if raw_path.exists():
        print(f"Using {raw_path} (delete it to download fresh data)")
    else:
        download(year)
    print(json.dumps(build_tables(year), indent=2))


if __name__ == "__main__":
    main()
