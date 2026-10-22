import sqlite3
from datetime import date
from typing import Any

from app.database.connection import get_connection
from app.repositories import billing_repository


def create_invoice(data: dict[str, Any]) -> dict[str, Any]:
    invoice_data = dict(data)

    due_date = invoice_data["due_date"]
    if isinstance(due_date, date):
        invoice_data["due_date"] = due_date.isoformat()

    with get_connection() as connection:
        patient = connection.execute(
            "SELECT id FROM patients WHERE id = ?",
            (invoice_data["patient_id"],),
        ).fetchone()

        if patient is None:
            raise ValueError("Patient not found.")

        appointment_id = invoice_data.get("appointment_id")
        if appointment_id is not None:
            appointment = connection.execute(
                "SELECT id, patient_id FROM appointments WHERE id = ?",
                (appointment_id,),
            ).fetchone()

            if appointment is None:
                raise ValueError("Appointment not found.")

            if appointment["patient_id"] != invoice_data["patient_id"]:
                raise ValueError(
                    "Appointment does not belong to the specified patient."
                )

    try:
        return billing_repository.create_invoice(invoice_data)
    except sqlite3.IntegrityError as exc:
        message = str(exc).lower()
        if "invoice" in message and "unique" in message:
            raise ValueError("Invoice number already exists.") from exc
        raise ValueError("Invoice could not be created due to invalid data.") from exc


def get_invoice(invoice_id: int) -> dict[str, Any]:
    invoice = billing_repository.get_invoice(invoice_id)
    if invoice is None:
        raise ValueError("Invoice not found.")

    invoice["payments"] = billing_repository.list_payments(invoice_id)
    return invoice


def list_invoices(
    patient_id: int | None = None,
    status: str | None = None,
) -> list[dict[str, Any]]:
    allowed_statuses = {"Unpaid", "Partially Paid", "Paid"}

    if status is not None and status not in allowed_statuses:
        raise ValueError("Invalid invoice status.")

    if patient_id is not None:
        with get_connection() as connection:
            patient = connection.execute(
                "SELECT id FROM patients WHERE id = ?",
                (patient_id,),
            ).fetchone()

        if patient is None:
            raise ValueError("Patient not found.")

    return billing_repository.list_invoices(patient_id, status)


def record_payment(
    invoice_id: int,
    data: dict[str, Any],
) -> dict[str, Any]:
    invoice = billing_repository.get_invoice(invoice_id)
    if invoice is None:
        raise ValueError("Invoice not found.")

    balance = invoice["balance_due_paisa"]
    if balance <= 0:
        raise ValueError("This invoice has already been paid.")

    amount = data["amount_paisa"]
    if amount > balance:
        raise ValueError(
            f"Payment exceeds the outstanding balance of {balance} paisa."
        )

    payment_data = dict(data)
    payment_data["invoice_id"] = invoice_id

    try:
        payment = billing_repository.create_payment(payment_data)
    except sqlite3.IntegrityError as exc:
        raise ValueError("Payment could not be recorded.") from exc

    updated_invoice = billing_repository.get_invoice(invoice_id)
    if updated_invoice is None:
        raise ValueError("Invoice not found after payment.")

    if updated_invoice["balance_due_paisa"] == 0:
        status = "Paid"
    elif updated_invoice["amount_paid_paisa"] > 0:
        status = "Partially Paid"
    else:
        status = "Unpaid"

    billing_repository.update_invoice_status(invoice_id, status)

    return {
        **payment,
        "invoice_status": status,
        "amount_paid_paisa": updated_invoice["amount_paid_paisa"],
        "balance_due_paisa": updated_invoice["balance_due_paisa"],
    }
