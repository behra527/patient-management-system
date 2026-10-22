from typing import Any

from app.database.connection import get_connection


def create_invoice(data: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO invoices (
                invoice_number, patient_id, appointment_id,
                description, total_amount_paisa, due_date
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data["invoice_number"],
                data["patient_id"],
                data.get("appointment_id"),
                data["description"],
                data["total_amount_paisa"],
                data["due_date"],
            ),
        )
        invoice_id = cursor.lastrowid

        row = connection.execute(
            """
            SELECT
                i.*,
                0 AS amount_paid_paisa,
                i.total_amount_paisa AS balance_due_paisa
            FROM invoices AS i
            WHERE i.id = ?
            """,
            (invoice_id,),
        ).fetchone()

        return dict(row)


def get_invoice(invoice_id: int) -> dict[str, Any] | None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                i.*,
                COALESCE(SUM(p.amount_paisa), 0) AS amount_paid_paisa,
                i.total_amount_paisa
                    - COALESCE(SUM(p.amount_paisa), 0) AS balance_due_paisa
            FROM invoices AS i
            LEFT JOIN payments AS p ON p.invoice_id = i.id
            WHERE i.id = ?
            GROUP BY i.id
            """,
            (invoice_id,),
        ).fetchone()

        return dict(row) if row else None


def list_invoices(
    patient_id: int | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    query = """
        SELECT
            i.*,
            COALESCE(SUM(p.amount_paisa), 0) AS amount_paid_paisa,
            i.total_amount_paisa
                - COALESCE(SUM(p.amount_paisa), 0) AS balance_due_paisa
        FROM invoices AS i
        LEFT JOIN payments AS p ON p.invoice_id = i.id
    """
    conditions: list[str] = []
    parameters: list[Any] = []

    if patient_id is not None:
        conditions.append("i.patient_id = ?")
        parameters.append(patient_id)

    if status is not None:
        conditions.append("i.status = ?")
        parameters.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY i.id ORDER BY i.created_at DESC, i.id DESC"

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()
        return [dict(row) for row in rows]


def create_payment(data: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO payments (
                invoice_id, amount_paisa, payment_method, reference
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                data["invoice_id"],
                data["amount_paisa"],
                data["payment_method"],
                data.get("reference"),
            ),
        )
        payment_id = cursor.lastrowid

        row = connection.execute(
            "SELECT * FROM payments WHERE id = ?",
            (payment_id,),
        ).fetchone()

        return dict(row)


def list_payments(invoice_id: int) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM payments
            WHERE invoice_id = ?
            ORDER BY paid_at DESC, id DESC
            """,
            (invoice_id,),
        ).fetchall()

        return [dict(row) for row in rows]


def update_invoice_status(invoice_id: int, status: str) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE invoices
            SET status = ?,
                updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
            WHERE id = ?
            """,
            (status, invoice_id),
        )
