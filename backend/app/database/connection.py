
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from app.core.config import DATABASE_PATH


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Provide a SQLite connection and manage its lifecycle."""
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    """Create application tables if they do not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL
                    CHECK (length(trim(full_name)) > 0),
                date_of_birth TEXT NOT NULL,
                gender TEXT NOT NULL
                    CHECK (gender IN ('Male', 'Female', 'Other')),
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                ),
                updated_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                )
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE
                    CHECK (length(trim(username)) BETWEEN 3 AND 50),
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL
                    CHECK (role IN ('admin', 'doctor', 'receptionist')),
                is_active INTEGER NOT NULL DEFAULT 1
                    CHECK (is_active IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                )
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL
                    CHECK (length(trim(full_name)) BETWEEN 2 AND 100),
                specialty TEXT NOT NULL
                    CHECK (length(trim(specialty)) BETWEEN 2 AND 100),
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                phone TEXT,
                license_number TEXT NOT NULL COLLATE NOCASE UNIQUE,
                status TEXT NOT NULL DEFAULT 'Active'
                    CHECK (status IN ('Active', 'Inactive', 'On Leave')),
                created_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                ),
                updated_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                )
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS vitals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL
                    CHECK (length(trim(patient_id)) > 0),
                age INTEGER NOT NULL
                    CHECK (age BETWEEN 0 AND 120),
                systolic INTEGER NOT NULL
                    CHECK (systolic BETWEEN 50 AND 300),
                diastolic INTEGER NOT NULL
                    CHECK (diastolic BETWEEN 30 AND 200),
                glucose_level REAL NOT NULL
                    CHECK (glucose_level > 0),
                recorded_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                )
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL DEFAULT 30
                    CHECK (duration_minutes BETWEEN 15 AND 240),
                reason TEXT NOT NULL
                    CHECK (length(trim(reason)) BETWEEN 3 AND 500),
                status TEXT NOT NULL DEFAULT 'Scheduled'
                    CHECK (status IN ('Scheduled', 'Completed', 'Cancelled')),
                created_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                ),
                updated_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                ),
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_appointments_doctor_schedule
            ON appointments (doctor_id, appointment_date, status)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_appointments_patient_date
            ON appointments (patient_id, appointment_date)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_number TEXT NOT NULL COLLATE NOCASE UNIQUE,
                patient_id INTEGER NOT NULL,
                appointment_id INTEGER,
                description TEXT NOT NULL
                    CHECK (length(trim(description)) BETWEEN 3 AND 500),
                total_amount_paisa INTEGER NOT NULL CHECK (total_amount_paisa > 0),
                due_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Unpaid'
                    CHECK (status IN ('Unpaid', 'Partially Paid', 'Paid')),
                created_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                ),
                updated_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                ),
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (appointment_id) REFERENCES appointments(id)
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                amount_paisa INTEGER NOT NULL CHECK (amount_paisa > 0),
                payment_method TEXT NOT NULL
                    CHECK (payment_method IN ('Cash', 'Card', 'Bank Transfer', 'Online')),
                reference TEXT,
                paid_at TEXT NOT NULL DEFAULT (
                    strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
                ),
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_invoices_patient
            ON invoices (patient_id, created_at DESC)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_payments_invoice
            ON payments (invoice_id, paid_at DESC)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_vitals_patient_recorded
            ON vitals (patient_id, recorded_at DESC, id DESC)
            """
        )


