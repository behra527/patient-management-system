from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

DoctorStatus = Literal["Active", "Inactive", "On Leave"]


class DoctorCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    specialty: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=20)
    license_number: str = Field(min_length=2, max_length=50)
    status: DoctorStatus = "Active"

    @field_validator("full_name", "specialty", "license_number")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        return value.strip() if value and value.strip() else None


class DoctorUpdate(DoctorCreate):
    pass


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    specialty: str
    email: EmailStr
    phone: str | None
    license_number: str
    status: DoctorStatus
    created_at: datetime
    updated_at: datetime
