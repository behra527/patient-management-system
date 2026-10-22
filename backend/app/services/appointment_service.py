from datetime import date, datetime, time, timedelta

from app.repositories import appointment_repository as repository


def create_appointment(data: dict) -> dict:
    appointment_date = date.fromisoformat(str(data["appointment_date"]))
    parsed_time = time.fromisoformat(str(data["appointment_time"]))
    if parsed_time.second or parsed_time.microsecond:
        raise ValueError("Appointment time must use HH:MM format")
    data["appointment_time"] = parsed_time.strftime("%H:%M")
    if appointment_date < date.today():
        raise ValueError("Appointments cannot be booked in the past")

    from app.database.connection import get_connection

    with get_connection() as connection:
        patient = connection.execute(
            "SELECT id FROM patients WHERE id = ?",
            (data["patient_id"],),
        ).fetchone()
        if patient is None:
            raise ValueError("Patient not found")

        doctor = connection.execute(
            "SELECT status FROM doctors WHERE id = ?",
            (data["doctor_id"],),
        ).fetchone()
        if doctor is None:
            raise ValueError("Doctor not found")
        if doctor["status"] != "Active":
            raise ValueError("Appointments require an active doctor")

    start = datetime.combine(
        appointment_date,
        datetime.strptime(str(data["appointment_time"]), "%H:%M").time(),
    )
    end = start + timedelta(minutes=data["duration_minutes"])

    for existing in repository.find_doctor_conflict(
        data["doctor_id"],
        appointment_date.isoformat(),
        str(data["appointment_time"]),
    ):
        existing_start = datetime.combine(
            appointment_date,
            datetime.strptime(existing["appointment_time"], "%H:%M").time(),
        )
        existing_end = existing_start + timedelta(
            minutes=existing["duration_minutes"]
        )
        if start < existing_end and existing_start < end:
            raise ValueError("Doctor already has an overlapping appointment")

    return repository.create_appointment(data)


def get_appointment(appointment_id: int) -> dict | None:
    return repository.get_appointment(appointment_id)


def list_appointments(
    patient_id: int | None = None,
    doctor_id: int | None = None,
    appointment_status: str | None = None,
) -> list[dict]:
    return repository.list_appointments(
        patient_id, doctor_id, appointment_status
    )


def update_appointment_status(
    appointment_id: int, new_status: str
) -> dict | None:
    appointment = repository.get_appointment(appointment_id)
    if appointment is None:
        return None

    current_status = appointment["status"]
    if current_status != "Scheduled":
        raise ValueError("Only scheduled appointments can change status")

    return repository.update_appointment_status(appointment_id, new_status)
