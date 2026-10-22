import sqlite3

from app.database.connection import get_connection


def create_doctor(data: dict) -> dict:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO doctors
                (full_name, specialty, email, phone, license_number, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data["full_name"], data["specialty"], data["email"],
                data.get("phone"), data["license_number"], data["status"],
            ),
        )
        row = connection.execute(
            "SELECT * FROM doctors WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)


def get_doctor(doctor_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM doctors WHERE id = ?", (doctor_id,)
        ).fetchone()
        return dict(row) if row else None


def list_doctors() -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM doctors ORDER BY full_name COLLATE NOCASE, id"
        ).fetchall()
        return [dict(row) for row in rows]


def update_doctor(doctor_id: int, data: dict) -> dict | None:
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM doctors WHERE id = ?", (doctor_id,)
        ).fetchone()
        if existing is None:
            return None

        connection.execute(
            """
            UPDATE doctors
            SET full_name = ?, specialty = ?, email = ?, phone = ?,
                license_number = ?, status = ?,
                updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ?
            """,
            (
                data["full_name"], data["specialty"], data["email"],
                data.get("phone"), data["license_number"], data["status"],
                doctor_id,
            ),
        )
        row = connection.execute(
            "SELECT * FROM doctors WHERE id = ?", (doctor_id,)
        ).fetchone()
        return dict(row)


def deactivate_doctor(doctor_id: int) -> dict | None:
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM doctors WHERE id = ?", (doctor_id,)
        ).fetchone()
        if existing is None:
            return None

        connection.execute(
            """
            UPDATE doctors
            SET status = 'Inactive',
                updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ?
            """,
            (doctor_id,),
        )
        row = connection.execute(
            "SELECT * FROM doctors WHERE id = ?", (doctor_id,)
        ).fetchone()
        return dict(row)
