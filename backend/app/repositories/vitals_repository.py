from typing import Any

from app.database.connection import get_connection


def create_vitals(vitals_data: dict[str, Any]) -> dict[str, Any]:
    """Persist a vitals record and return the created record."""
    blood_pressure = vitals_data["blood_pressure"]

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO vitals (
                patient_id,
                age,
                systolic,
                diastolic,
                glucose_level
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                vitals_data["patient_id"],
                vitals_data["age"],
                blood_pressure["systolic"],
                blood_pressure["diastolic"],
                vitals_data["glucose_level"],
            ),
        )

        row = connection.execute(
            """
            SELECT *
            FROM vitals
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

        if row is None:
            raise RuntimeError("Created vitals record could not be retrieved")

        return _serialize_vitals(dict(row))


def get_patient_vitals(
    patient_id: str,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Return a patient's vitals history, newest record first."""
    query = """
        SELECT *
        FROM vitals
        WHERE patient_id = ?
        ORDER BY recorded_at DESC, id DESC
    """
    parameters: tuple[Any, ...] = (patient_id,)

    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        query += " LIMIT ?"
        parameters = (patient_id, limit)

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

        return [_serialize_vitals(dict(row)) for row in rows]


def get_patient_vitals_summary(patient_id: str) -> dict[str, Any]:
    """Calculate average measurements and record count for a patient."""
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                COUNT(*) AS total_records,
                AVG(systolic) AS average_systolic,
                AVG(diastolic) AS average_diastolic,
                AVG(glucose_level) AS average_glucose_level
            FROM vitals
            WHERE patient_id = ?
            """,
            (patient_id,),
        ).fetchone()

        if row is None:
            raise RuntimeError("Vitals summary query returned no result")

        result = dict(row)

        # An empty history has zero records and zero-valued averages.
        return {
            "patient_id": patient_id,
            "average_systolic": float(result["average_systolic"] or 0),
            "average_diastolic": float(result["average_diastolic"] or 0),
            "average_glucose_level": float(
                result["average_glucose_level"] or 0
            ),
            "total_records": result["total_records"],
        }


def _serialize_vitals(record: dict[str, Any]) -> dict[str, Any]:
    """Convert database columns into the API's nested blood pressure shape."""
    return {
        "id": record["id"],
        "patient_id": record["patient_id"],
        "age": record["age"],
        "blood_pressure": {
            "systolic": record["systolic"],
            "diastolic": record["diastolic"],
        },
        "glucose_level": record["glucose_level"],
        "recorded_at": record["recorded_at"],
    }
