from fastapi import status

from app.auth.security import hash_password
from app.database import connection as database_connection


TEST_PASSWORD = "Test-Role-Password-123!"

DOCTOR_DATA = {
    "full_name": "Dr. Sarah Ahmed",
    "specialty": "Cardiology",
    "email": "sarah.ahmed@example.com",
    "phone": "+923001234567",
    "license_number": "PMDC-TEST-1001",
    "status": "Active",
}


def login_as_role(client, username: str, role: str) -> None:
    with database_connection.get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (
                username, hashed_password, role, is_active
            )
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


def create_doctor(client, data=None):
    return client.post("/doctors/", json=data or DOCTOR_DATA)


def test_admin_can_create_doctor(client):
    response = create_doctor(client)

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["full_name"] == DOCTOR_DATA["full_name"]
    assert body["email"] == DOCTOR_DATA["email"]
    assert body["status"] == "Active"
    assert "id" in body


def test_doctor_list_returns_created_doctors(client):
    created = create_doctor(client)
    assert created.status_code == status.HTTP_201_CREATED

    response = client.get("/doctors/")

    assert response.status_code == status.HTTP_200_OK
    assert any(item["id"] == created.json()["id"] for item in response.json())


def test_admin_can_get_doctor_by_id(client):
    created = create_doctor(client)
    doctor_id = created.json()["id"]

    response = client.get(f"/doctors/{doctor_id}")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == doctor_id


def test_admin_can_update_doctor(client):
    created = create_doctor(client)
    doctor_id = created.json()["id"]
    updated_data = {
        **DOCTOR_DATA,
        "full_name": "Dr. Sarah Updated",
        "specialty": "Neurology",
        "email": "sarah.updated@example.com",
        "license_number": "PMDC-TEST-1002",
    }

    response = client.put(f"/doctors/{doctor_id}", json=updated_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == "Dr. Sarah Updated"
    assert response.json()["specialty"] == "Neurology"


def test_duplicate_email_is_rejected(client):
    first = create_doctor(client)
    assert first.status_code == status.HTTP_201_CREATED

    duplicate = {
        **DOCTOR_DATA,
        "license_number": "PMDC-TEST-1003",
    }
    response = create_doctor(client, duplicate)

    assert response.status_code == status.HTTP_409_CONFLICT


def test_duplicate_license_number_is_rejected(client):
    first = create_doctor(client)
    assert first.status_code == status.HTTP_201_CREATED

    duplicate = {
        **DOCTOR_DATA,
        "email": "another.doctor@example.com",
    }
    response = create_doctor(client, duplicate)

    assert response.status_code == status.HTTP_409_CONFLICT


def test_missing_doctor_returns_404(client):
    response = client.get("/doctors/999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_admin_can_deactivate_doctor(client):
    created = create_doctor(client)
    doctor_id = created.json()["id"]

    response = client.patch(f"/doctors/{doctor_id}/deactivate")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "Inactive"


def test_doctor_can_read_doctor_directory(client):
    login_as_role(client, "testdoctor", "doctor")

    response = client.get("/doctors/")

    assert response.status_code == status.HTTP_200_OK


def test_receptionist_can_read_doctor_directory(client):
    login_as_role(client, "testreceptionist", "receptionist")

    response = client.get("/doctors/")

    assert response.status_code == status.HTTP_200_OK


def test_doctor_cannot_create_doctor(client):
    login_as_role(client, "testdoctor", "doctor")

    response = create_doctor(client)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_receptionist_cannot_update_doctor(client):
    created = create_doctor(client)
    doctor_id = created.json()["id"]
    login_as_role(client, "testreceptionist", "receptionist")

    response = client.put(
        f"/doctors/{doctor_id}",
        json={
            **DOCTOR_DATA,
            "email": "updated.sarah@example.com",
            "license_number": "PMDC-TEST-1004",
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_doctor_cannot_deactivate_doctor(client):
    created = create_doctor(client)
    doctor_id = created.json()["id"]
    login_as_role(client, "testdoctor", "doctor")

    response = client.patch(f"/doctors/{doctor_id}/deactivate")

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_doctor_rejects_invalid_email(client):
    invalid_data = {
        **DOCTOR_DATA,
        "email": "not-an-email",
        "license_number": "PMDC-TEST-1005",
    }

    response = create_doctor(client, invalid_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
