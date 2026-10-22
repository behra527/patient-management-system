import sqlite3

from app.repositories import doctor_repository


def create_doctor(data: dict) -> dict:
    try:
        return doctor_repository.create_doctor(data)
    except sqlite3.IntegrityError as error:
        message = str(error).lower()
        if "doctors.email" in message:
            raise ValueError("A doctor with this email already exists") from error
        if "doctors.license_number" in message:
            raise ValueError("A doctor with this license number already exists") from error
        raise ValueError("Doctor data violates a database constraint") from error


def get_doctor(doctor_id: int) -> dict | None:
    return doctor_repository.get_doctor(doctor_id)


def list_doctors() -> list[dict]:
    return doctor_repository.list_doctors()


def update_doctor(doctor_id: int, data: dict) -> dict | None:
    try:
        return doctor_repository.update_doctor(doctor_id, data)
    except sqlite3.IntegrityError as error:
        message = str(error).lower()
        if "doctors.email" in message:
            raise ValueError("A doctor with this email already exists") from error
        if "doctors.license_number" in message:
            raise ValueError("A doctor with this license number already exists") from error
        raise ValueError("Doctor data violates a database constraint") from error


def deactivate_doctor(doctor_id: int) -> dict | None:
    return doctor_repository.deactivate_doctor(doctor_id)
