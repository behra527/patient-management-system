from app.database.connection import get_connection


def create_appointment(data: dict) -> dict:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO appointments (
                patient_id, doctor_id, appointment_date,
                appointment_time, duration_minutes, reason, status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Scheduled')
            """,
            (
                data["patient_id"],
                data["doctor_id"],
                data["appointment_date"],
                data["appointment_time"],
                data["duration_minutes"],
                data["reason"],
            ),
        )
        row = connection.execute(
            "SELECT * FROM appointments WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)


def get_appointment(appointment_id: int) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM appointments WHERE id = ?", (appointment_id,)
        ).fetchone()
        return dict(row) if row else None


def list_appointments(
    patient_id: int | None = None,
    doctor_id: int | None = None,
    appointment_status: str | None = None,
) -> list[dict]:
    query = "SELECT * FROM appointments WHERE 1=1"
    parameters = []

    if patient_id is not None:
        query += " AND patient_id = ?"
        parameters.append(patient_id)
    if doctor_id is not None:
        query += " AND doctor_id = ?"
        parameters.append(doctor_id)
    if appointment_status is not None:
        query += " AND status = ?"
        parameters.append(appointment_status)

    query += " ORDER BY appointment_date, appointment_time, id"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]


def find_doctor_conflict(
    doctor_id: int,
    appointment_date: str,
    start_time: str,
) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT appointment_time, duration_minutes
            FROM appointments
            WHERE doctor_id = ?
              AND appointment_date = ?
              AND status = 'Scheduled'
            """,
            (doctor_id, appointment_date),
        ).fetchall()
        return [dict(row) for row in rows]


def update_appointment_status(
    appointment_id: int, appointment_status: str
) -> dict | None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE appointments
            SET status = ?,
                updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ?
            """,
            (appointment_status, appointment_id),
        )
        row = connection.execute(
            "SELECT * FROM appointments WHERE id = ?", (appointment_id,)
        ).fetchone()
        return dict(row) if row else None
