from datetime import date, timedelta

from fastapi import status

from app.auth.security import hash_password
from app.database import connection as database_connection


TEST_PASSWORD = "Test-Role-Password-123!"

DOCTOR_DATA = {
    "full_name": "Dr. Sarah Ahmed",
    "specialty": "Cardiology",
    "email": "sarah.ahmed@example.com",
    "phone": "+923001234567",
    "license_number": "PMDC-APPT-1001",
    "status": "Active",
}

PATIENT_DATA = {
    "full_name": "Appointment Test Patient",
    "date_of_birth": "1998-04-12",
    "gender": "Male",
}


def login_as_role(client, username: str, role: str) -> None:
    with database_connection.get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (username, hashed_password, role, is_active)
            VALUES (?, ?, ?, ?)
            """,
            (username, hash_password(TEST_PASSWORD), role, 1),
        )

    response = client.post(
        "/auth/login",
        json={"username": username, "password": TEST_PASSWORD},
    )
    assert response.status_code == status.HTTP_200_OK

    client.headers.update(
        {"Authorization": f"Bearer {response.json()['access_token']}"}
    )


def create_patient(client):
    return client.post("/patients/", json=PATIENT_DATA)


def create_doctor(client, data=None):
    return client.post("/doctors/", json=data or DOCTOR_DATA)


def create_appointment_payload(patient_id, doctor_id, **overrides):
    payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "appointment_date": (date.today() + timedelta(days=2)).isoformat(),
        "appointment_time": "10:00",
        "duration_minutes": 30,
        "reason": "Routine consultation",
    }
    payload.update(overrides)
    return payload


def create_appointment(client, **overrides):
    patient_response = create_patient(client)
    assert patient_response.status_code == status.HTTP_201_CREATED

    doctor_response = create_doctor(client)
    assert doctor_response.status_code == status.HTTP_201_CREATED

    payload = create_appointment_payload(
        patient_response.json()["id"],
        doctor_response.json()["id"],
        **overrides,
    )
    response = client.post("/appointments/", json=payload)
    return response, payload


def test_admin_can_create_appointment(client):
    response, payload = create_appointment(client)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["patient_id"] == payload["patient_id"]
    assert body["doctor_id"] == payload["doctor_id"]
    assert body["appointment_date"] == payload["appointment_date"]
    assert body["appointment_time"].startswith("10:00")
    assert body["duration_minutes"] == 30
    assert body["reason"] == "Routine consultation"
    assert body["status"] == "Scheduled"
    assert "id" in body


def test_appointment_list_returns_created_appointment(client):
    created, _ = create_appointment(client)
    assert created.status_code == status.HTTP_201_CREATED

    response = client.get("/appointments/")

    assert response.status_code == status.HTTP_200_OK
    assert any(item["id"] == created.json()["id"] for item in response.json())


def test_appointments_can_be_filtered_by_patient(client):
    created, payload = create_appointment(client)

    response = client.get(
        "/appointments/",
        params={"patient_id": payload["patient_id"]},
    )

    assert response.status_code == status.HTTP_200_OK
    assert all(
        item["patient_id"] == payload["patient_id"]
        for item in response.json()
    )
    assert any(item["id"] == created.json()["id"] for item in response.json())


def test_appointments_can_be_filtered_by_doctor(client):
    created, payload = create_appointment(client)

    response = client.get(
        "/appointments/",
        params={"doctor_id": payload["doctor_id"]},
    )

    assert response.status_code == status.HTTP_200_OK
    assert all(
        item["doctor_id"] == payload["doctor_id"]
        for item in response.json()
    )
    assert any(item["id"] == created.json()["id"] for item in response.json())


def test_admin_can_get_appointment_by_id(client):
    created, _ = create_appointment(client)

    response = client.get(f"/appointments/{created.json()['id']}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == created.json()["id"]


def test_missing_appointment_returns_404(client):
    response = client.get("/appointments/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_appointment_rejects_unknown_patient(client):
    doctor_response = create_doctor(client)
    assert doctor_response.status_code == status.HTTP_201_CREATED

    payload = create_appointment_payload(
        999999, doctor_response.json()["id"]
    )
    response = client.post("/appointments/", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_appointment_rejects_unknown_doctor(client):
    patient_response = create_patient(client)
    assert patient_response.status_code == status.HTTP_201_CREATED

    payload = create_appointment_payload(
        patient_response.json()["id"], 999999
    )
    response = client.post("/appointments/", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_appointment_rejects_inactive_doctor(client):
    patient_response = create_patient(client)
    doctor_response = create_doctor(client)
    assert patient_response.status_code == status.HTTP_201_CREATED
    assert doctor_response.status_code == status.HTTP_201_CREATED

    doctor_id = doctor_response.json()["id"]
    deactivate_response = client.patch(
        f"/doctors/{doctor_id}/deactivate"
    )
    assert deactivate_response.status_code == status.HTTP_200_OK

    payload = create_appointment_payload(
        patient_response.json()["id"], doctor_id
    )
    response = client.post("/appointments/", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_overlapping_appointments_for_same_doctor_are_rejected(client):
    first, payload = create_appointment(client)
    assert first.status_code == status.HTTP_201_CREATED

    second_payload = {
        **payload,
        "appointment_time": "10:15",
        "reason": "Follow-up consultation",
    }
    response = client.post("/appointments/", json=second_payload)

    assert response.status_code == status.HTTP_409_CONFLICT


def test_non_overlapping_appointments_for_same_doctor_are_allowed(client):
    first, payload = create_appointment(client)
    assert first.status_code == status.HTTP_201_CREATED

    second_payload = {
        **payload,
        "appointment_time": "10:30",
        "reason": "Follow-up consultation",
    }
    response = client.post("/appointments/", json=second_payload)

    assert response.status_code == status.HTTP_201_CREATED


def test_appointment_rejects_past_date(client):
    patient_response = create_patient(client)
    doctor_response = create_doctor(client)
    assert patient_response.status_code == status.HTTP_201_CREATED
    assert doctor_response.status_code == status.HTTP_201_CREATED

    payload = create_appointment_payload(
        patient_response.json()["id"],
        doctor_response.json()["id"],
        appointment_date=(date.today() - timedelta(days=1)).isoformat(),
    )
    response = client.post("/appointments/", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_appointment_rejects_invalid_time(client):
    patient_response = create_patient(client)
    doctor_response = create_doctor(client)
    assert patient_response.status_code == status.HTTP_201_CREATED
    assert doctor_response.status_code == status.HTTP_201_CREATED

    payload = create_appointment_payload(
        patient_response.json()["id"],
        doctor_response.json()["id"],
        appointment_time="not-a-time",
    )
    response = client.post("/appointments/", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_admin_can_complete_scheduled_appointment(client):
    created, _ = create_appointment(client)
    appointment_id = created.json()["id"]

    response = client.patch(
        f"/appointments/{appointment_id}/status",
        json={"status": "Completed"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "Completed"


def test_completed_appointment_cannot_be_changed_again(client):
    created, _ = create_appointment(client)
    appointment_id = created.json()["id"]

    completed = client.patch(
        f"/appointments/{appointment_id}/status",
        json={"status": "Completed"},
    )
    assert completed.status_code == status.HTTP_200_OK

    response = client.patch(
        f"/appointments/{appointment_id}/status",
        json={"status": "Cancelled"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_doctor_cannot_create_appointment(client):
    login_as_role(client, "appointmentdoctor", "doctor")

    response = client.post(
        "/appointments/",
        json=create_appointment_payload(1, 1),
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_receptionist_can_create_appointment(client):
    patient_response = create_patient(client)
    doctor_response = create_doctor(client)
    assert patient_response.status_code == status.HTTP_201_CREATED
    assert doctor_response.status_code == status.HTTP_201_CREATED

    login_as_role(client, "appointmentreceptionist", "receptionist")

    payload = create_appointment_payload(
        patient_response.json()["id"],
        doctor_response.json()["id"],
    )
    response = client.post("/appointments/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED


def test_appointment_requires_authentication(client):
    client.headers.pop("Authorization", None)

    response = client.get("/appointments/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
