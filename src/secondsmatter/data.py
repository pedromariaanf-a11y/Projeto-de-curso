"""Data layer: DataSF records -> `incidents` and `responses` tables.

Source rows are unit responses, not incidents: one emergency can have several
rows, one per unit sent. Demand is counted in `incidents`, never in `responses`.
Times are kept as local San Francisco time without a time zone, as the source
gives them.
"""

import json

import pandas as pd

API_URL = "https://data.sf.gov/resource/nuek-vuh3.json"

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


def _coordinates(location) -> tuple[float, float]:
    """Read (latitude, longitude) from the API's point text; missing -> NaN."""
    if not isinstance(location, str):
        return float("nan"), float("nan")
    longitude, latitude = json.loads(location)["coordinates"]
    return latitude, longitude


def _minutes(start: pd.Series, end: pd.Series) -> pd.Series:
    return (end - start).dt.total_seconds() / 60


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
    unreadable_times = 0
    for column in TIME_COLUMNS:
        parsed = pd.to_datetime(responses[column], format="ISO8601", errors="coerce")
        unreadable_times += int((parsed.isna() & responses[column].notna()).sum())
        responses[column] = parsed

    responses["als_unit"] = responses["als_unit"] == "true"  # observed
    responses["is_ambulance"] = responses["unit_type"].isin(AMBULANCE_TYPES)  # assumption
    responses["unit_sequence_in_call_dispatch"] = pd.to_numeric(
        responses["unit_sequence_in_call_dispatch"], errors="coerce"
    )
    points = [_coordinates(value) for value in responses["case_location"]]
    responses["latitude"] = [lat for lat, _ in points]
    responses["longitude"] = [lon for _, lon in points]
    responses = responses.rename(columns={"neighborhoods_analysis_boundaries": "neighborhood"})

    # Derived durations. Negative ones are impossible, so they become empty.
    to_on_scene = _minutes(responses["dispatch_dttm"], responses["on_scene_dttm"])
    busy = _minutes(responses["dispatch_dttm"], responses["available_dttm"])
    responses["minutes_to_on_scene"] = to_on_scene.where(to_on_scene >= 0)
    responses["minutes_busy"] = busy.where(busy >= 0)

    # An incident "conflicts" when its rows disagree on call type or location.
    distinct = responses.groupby("incident_number")[["call_type", "case_location"]].nunique(
        dropna=False
    )
    conflicting = int((distinct > 1).any(axis=1).sum())

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
        "unique_rowids": int(responses["rowid"].nunique()),
        "incidents": len(incidents),
        "missing_coordinates": int(responses["latitude"].isna().sum()),
        "missing_unit_type": int(responses["unit_type"].isna().sum()),
        "missing_available_dttm": int(raw["available_dttm"].isna().sum()),
        "unreadable_times": unreadable_times,
        "negative_minutes_to_on_scene": int((to_on_scene < 0).sum()),
        "negative_minutes_busy": int((busy < 0).sum()),
        "incidents_with_conflicting_details": conflicting,
    }
    return incidents, responses, quality
