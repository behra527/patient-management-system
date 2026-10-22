from datetime import date, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

AppointmentStatus = Literal["Scheduled", "Completed", "Cancelled"]


class AppointmentCreate(BaseModel):
    patient_id: int = Field(gt=0)
    doctor_id: int = Field(gt=0)
    appointment_date: date
    appointment_time: time
    duration_minutes: int = Field(default=30, ge=15, le=240)
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Reason must contain at least 3 characters")
        return value

    @field_validator("appointment_time")
    @classmethod
    def validate_time_precision(cls, value: time) -> time:
        if value.second or value.microsecond:
            raise ValueError("Appointment time must use HH:MM format")
        return value


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    duration_minutes: int
    reason: str
    status: AppointmentStatus
    created_at: str
    updated_at: str
