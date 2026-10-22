from datetime import datetime

import pytest


VALID_PAYLOAD = {
    "patient_id": "PAT-VITALS-001",
    "age": 35,
    "blood_pressure": {
        "systolic": 120,
        "diastolic": 80,
    },
    "glucose_level": 95.5,
}


def test_health_endpoint_is_public(client):
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"

    timestamp = datetime.fromisoformat(data["timestamp"])
    assert timestamp.utcoffset() is not None


def test_create_vitals_success(client):
    response = client.post("/vitals", json=VALID_PAYLOAD)

    assert response.status_code == 201
    data = response.json()
    assert data["patient_id"] == VALID_PAYLOAD["patient_id"]
    assert data["age"] == 35
    assert data["blood_pressure"] == {"systolic": 120, "diastolic": 80}
    assert data["glucose_level"] == 95.5
    assert data["id"] > 0
    assert data["recorded_at"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("age", -1),
        ("age", 121),
        ("age", 35.5),
        ("age", "35"),
        ("patient_id", ""),
        ("patient_id", "   "),
        ("glucose_level", 0),
        ("glucose_level", -1),
        ("glucose_level", "95"),
    ],
)
def test_invalid_vitals_fields_return_400(client, field, value):
    payload = {
        **VALID_PAYLOAD,
        "blood_pressure": dict(VALID_PAYLOAD["blood_pressure"]),
    }
    payload[field] = value

    response = client.post("/vitals", json=payload)

    assert response.status_code == 400
    assert response.json()["errors"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("systolic", 49),
        ("systolic", 301),
        ("systolic", "120"),
        ("diastolic", 29),
        ("diastolic", 201),
        ("diastolic", "80"),
    ],
)
def test_invalid_blood_pressure_returns_400(client, field, value):
    payload = {
        **VALID_PAYLOAD,
        "blood_pressure": {
            **VALID_PAYLOAD["blood_pressure"],
            field: value,
        },
    }

    response = client.post("/vitals", json=payload)

    assert response.status_code == 400
    assert response.json()["errors"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"patient_id": "PAT-1"},
        {**VALID_PAYLOAD, "blood_pressure": {}},
        {**VALID_PAYLOAD, "unexpected": "value"},
    ],
)
def test_missing_or_extra_data_returns_400(client, payload):
    response = client.post("/vitals", json=payload)

    assert response.status_code == 400


def test_vitals_history_and_limit(client):
    payload = {**VALID_PAYLOAD, "patient_id": "PAT-HISTORY-001"}

    first = client.post("/vitals", json=payload)
    second_payload = {
        **payload,
        "glucose_level": 110,
        "blood_pressure": {"systolic": 130, "diastolic": 85},
    }
    second = client.post("/vitals", json=second_payload)

    assert first.status_code == 201
    assert second.status_code == 201

    history = client.get("/patients/PAT-HISTORY-001/vitals")
    assert history.status_code == 200
    assert len(history.json()) == 2

    limited = client.get("/patients/PAT-HISTORY-001/vitals?limit=1")
    assert limited.status_code == 200
    assert len(limited.json()) == 1
    assert limited.json()[0]["id"] == second.json()["id"]


def test_vitals_summary(client):
    patient_id = "PAT-SUMMARY-001"

    records = [
        {
            **VALID_PAYLOAD,
            "patient_id": patient_id,
            "blood_pressure": {"systolic": 120, "diastolic": 80},
            "glucose_level": 90,
        },
        {
            **VALID_PAYLOAD,
            "patient_id": patient_id,
            "blood_pressure": {"systolic": 140, "diastolic": 100},
            "glucose_level": 110,
        },
    ]

    for record in records:
        response = client.post("/vitals", json=record)
        assert response.status_code == 201

    response = client.get(f"/patients/{patient_id}/summary")

    assert response.status_code == 200
    assert response.json() == {
        "patient_id": patient_id,
        "average_systolic": 130.0,
        "average_diastolic": 90.0,
        "average_glucose_level": 100.0,
        "total_records": 2,
    }


def test_empty_patient_summary(client):
    response = client.get("/patients/PAT-NO-RECORDS/vitals")
    assert response.status_code == 200
    assert response.json() == []

    summary = client.get("/patients/PAT-NO-RECORDS/summary")
    assert summary.status_code == 200
    assert summary.json()["total_records"] == 0
    assert summary.json()["average_systolic"] == 0


def test_vitals_endpoints_require_authentication(client):
    client.cookies.clear()
    client.headers.pop("Authorization", None)

    response = client.post("/vitals", json=VALID_PAYLOAD)

    assert response.status_code == 401
