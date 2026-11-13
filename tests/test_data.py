import pandas as pd

from secondsmatter.data import COLUMNS, make_fleet, make_tables

POINT = '{"type": "Point", "coordinates": [-122.4, 37.7]}'


def t(hhmm):
    return f"2025-01-01T{hhmm}:00.000"


def row(incident, seq, unit_type, dispatch, on_scene, available, location=POINT):
    """One raw row, stored as text the way `download` saves it."""
    values = dict.fromkeys(COLUMNS)
    values.update(
        rowid=f"{incident}-{seq}", incident_number=incident, unit_id=f"U{seq}",
        unit_type=unit_type, als_unit="true", unit_sequence_in_call_dispatch=seq,
        call_type="Medical Incident", received_dttm=t("09:55"),
        dispatch_dttm=dispatch, on_scene_dttm=on_scene, available_dttm=available,
        case_location=location,
    )
    return values


def test_make_tables():
    """4 hand-checked rows: 3 incidents, one special case each."""
    raw = pd.DataFrame([
        # incident 1: an ambulance and an engine (the normal case)
        row("1", "1", "MEDIC", t("10:00"), t("10:08"), t("10:50")),
        row("1", "2", "ENGINE", t("10:01"), t("10:05"), t("10:30")),
        # incident 2: available BEFORE dispatch -> negative busy time
        row("2", "1", "BLS", t("11:00"), t("11:09"), t("10:55")),
        # incident 3: no location and no available time
        row("3", "1", "PRIVATE", t("12:00"), t("12:10"), None, location=None),
    ])

    incidents, responses, quality = make_tables(raw)

    assert len(responses) == 4
    assert len(incidents) == 3
    assert responses["is_ambulance"].tolist() == [True, False, True, True]
    assert responses.loc[0, "minutes_to_on_scene"] == 8
    assert responses.loc[0, "minutes_busy"] == 50
    assert pd.isna(responses.loc[2, "minutes_busy"])  # negative becomes empty
    assert responses.loc[0, "latitude"] == 37.7

    first_incident = incidents.set_index("incident_number").loc["1"]
    assert first_incident["units_sent"] == 2
    assert first_incident["ambulances_sent"] == 1

    assert quality == {
        "rows": 4,
        "incidents": 3,
        "missing_coordinates": 1,
        "missing_available_dttm": 1,
        "negative_durations": 1,
    }


def test_make_fleet():
    """3 units: a MEDIC sent 3 times, a BLS sent once, and an engine (not an ambulance)."""
    responses = pd.DataFrame({
        "unit_id":             ["M1", "M1", "M1", "B1", "E1"],
        "unit_type":           ["MEDIC", "MEDIC", "MEDIC", "BLS", "ENGINE"],
        "is_ambulance":        [True, True, True, True, False],
        "als_unit":            [True, True, False, False, True],
        "dispatch_dttm":       pd.to_datetime(["2025-01-01", "2025-02-01", "2025-03-01",
                                               "2025-01-15", "2025-01-01"]),
        "minutes_to_on_scene": [6, 8, 10, 9, 5],
        "minutes_busy":        [40, 60, None, 70, 20],
    })

    fleet = make_fleet(responses).set_index("unit_id")

    assert list(fleet.index) == ["M1", "B1"]          # engine left out, busiest first
    m1 = fleet.loc["M1"]
    assert m1["unit_type"] == "MEDIC"
    assert m1["responses"] == 3
    assert m1["als_share"] == 2 / 3                   # ALS on 2 of its 3 responses
    assert m1["first_seen"] == pd.Timestamp("2025-01-01")
    assert m1["last_seen"] == pd.Timestamp("2025-03-01")
    assert m1["median_minutes_to_on_scene"] == 8
    assert m1["median_minutes_busy"] == 50            # the empty value is skipped
