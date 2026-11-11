import json

import pandas as pd
import pytest

from secondsmatter import data
from secondsmatter.data import COLUMNS, download, make_tables

POINT = '{"type": "Point", "coordinates": [-122.4, 37.7]}'


def row(rowid, incident, seq, unit_id, unit_type, als, dispatch, on_scene, available,
        location=POINT, call_type="Medical Incident"):
    """One raw row, stored as text the way `download` saves it."""
    values = dict.fromkeys(COLUMNS)
    values.update(
        rowid=rowid, incident_number=incident, unit_id=unit_id, unit_type=unit_type,
        als_unit=als, unit_sequence_in_call_dispatch=seq, call_type=call_type,
        received_dttm="2025-01-01T09:55:00.000",
        dispatch_dttm=dispatch, on_scene_dttm=on_scene, available_dttm=available,
        case_location=location,
    )
    return values


def t(hhmm):
    return f"2025-01-01T{hhmm}:00.000"


def raw_rows():
    """6 hand-checked rows, 4 incidents, one special case each."""
    return pd.DataFrame([
        # incident 1: an ambulance and an engine (normal case)
        row("1-M01", "1", "1", "M01", "MEDIC", "true", t("10:00"), t("10:08"), t("10:50")),
        row("1-E01", "1", "2", "E01", "ENGINE", "true", t("10:01"), t("10:05"), t("10:30")),
        # incident 2: available BEFORE dispatch -> negative busy time
        row("2-B01", "2", "1", "B01", "BLS", "false", t("11:00"), t("11:09"), t("10:55")),
        # incident 3: first row has no location and no available time;
        # second row disagrees on call type -> one conflicting incident
        row("3-P01", "3", "1", "P01", "PRIVATE", "false", t("12:00"), t("12:10"), None,
            location=None),
        row("3-T01", "3", "2", "T01", "TRUCK", "false", t("12:02"), t("12:12"), t("12:40"),
            call_type="Alarms"),
        # incident 4: dispatch time cannot be read
        row("4-E02", "4", "1", "E02", "ENGINE", "false", "not-a-date", t("13:10"), t("13:40"),
            call_type="Alarms"),
    ])


def test_make_tables_counts_and_durations():
    incidents, responses, _ = make_tables(raw_rows())

    assert len(responses) == 6
    assert len(incidents) == 4

    first = incidents.set_index("incident_number").loc["1"]
    assert first["units_sent"] == 2
    assert first["ambulances_sent"] == 1
    # incident 3 keeps the details of its first dispatched unit
    assert incidents.set_index("incident_number").loc["3", "call_type"] == "Medical Incident"

    assert responses["is_ambulance"].tolist() == [True, False, True, True, False, False]
    assert responses.loc[0, "minutes_to_on_scene"] == 8
    assert responses.loc[0, "minutes_busy"] == 50
    assert pd.isna(responses.loc[2, "minutes_busy"])  # negative becomes empty
    assert responses.loc[0, "latitude"] == 37.7


def test_make_tables_quality_report():
    _, _, quality = make_tables(raw_rows())

    assert quality == {
        "rows": 6,
        "unique_rowids": 6,
        "incidents": 4,
        "missing_coordinates": 1,
        "missing_unit_type": 0,
        "missing_available_dttm": 1,
        "unreadable_times": 1,
        "negative_minutes_to_on_scene": 0,
        "negative_minutes_busy": 1,
        "incidents_with_conflicting_details": 1,
    }


# --- download: a fake connection replaces the internet ---------------------

class FakeResponse:
    def __init__(self, status_code, body=None):
        self.status_code = status_code
        self.body = body

    def json(self):
        return self.body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    """Answers each `get` with the next prepared response, and records the params."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, params, timeout):
        self.calls.append(params)
        return self.responses.pop(0)


def api_row(rowid):
    """A row as the API sends it: als_unit is a boolean, case_location an object."""
    return {"rowid": rowid, "als_unit": True,
            "case_location": {"type": "Point", "coordinates": [-122.4, 37.7]},
            "data_as_of": "2026-03-11T03:23:01.000"}


@pytest.fixture(autouse=True)
def fast_and_small(monkeypatch):
    monkeypatch.setattr(data, "RETRY_WAIT_SECONDS", 0)
    monkeypatch.setattr(data, "PAGE_SIZE", 2)


def test_download_joins_pages_and_retries(tmp_path):
    session = FakeSession([
        FakeResponse(200, [{"n": "3"}]),                       # count query
        FakeResponse(503),                                     # server busy -> retry
        FakeResponse(200, [api_row("a"), api_row("b")]),       # page 1
        FakeResponse(200, [api_row("c")]),                     # page 2
    ])

    path = download(2025, data_dir=tmp_path, session=session)

    raw = pd.read_parquet(path)
    assert raw["rowid"].tolist() == ["a", "b", "c"]
    assert raw.loc[0, "als_unit"] == "true"          # stored as text
    assert session.calls[-1]["$offset"] == 2          # second page starts after 2 rows
    info = json.loads((tmp_path / "sf_ems_2025_info.json").read_text())
    assert info["rows"] == 3
    assert info["columns"] == COLUMNS


def test_download_count_mismatch_writes_nothing(tmp_path):
    session = FakeSession([
        FakeResponse(200, [{"n": "3"}]),                       # API says 3 rows
        FakeResponse(200, [api_row("a"), api_row("b")]),       # but only 2 arrive
        FakeResponse(200, []),
    ])

    with pytest.raises(RuntimeError, match="Expected 3 rows"):
        download(2025, data_dir=tmp_path, session=session)

    assert list(tmp_path.iterdir()) == []
