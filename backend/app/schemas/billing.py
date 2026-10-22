from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


PaymentMethod = Literal["Cash", "Card", "Bank Transfer", "Online"]
InvoiceStatus = Literal["Unpaid", "Partially Paid", "Paid"]


class InvoiceCreate(BaseModel):
    invoice_number: str = Field(min_length=3, max_length=50)
    patient_id: int = Field(gt=0)
    appointment_id: int | None = Field(default=None, gt=0)
    description: str = Field(min_length=3, max_length=500)
    total_amount_paisa: int = Field(gt=0)
    due_date: date

    @field_validator("invoice_number", "description")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be empty.")
        return value


class PaymentCreate(BaseModel):
    amount_paisa: int = Field(gt=0)
    payment_method: PaymentMethod
    reference: str | None = Field(default=None, max_length=100)

    @field_validator("reference")
    @classmethod
    def strip_reference(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    amount_paisa: int
    payment_method: PaymentMethod
    reference: str | None
    paid_at: datetime


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    patient_id: int
    appointment_id: int | None
    description: str
    total_amount_paisa: int
    amount_paid_paisa: int
    balance_due_paisa: int
    due_date: date
    status: InvoiceStatus
    created_at: datetime
    updated_at: datetime


class InvoiceDetailResponse(InvoiceResponse):
    payments: list[PaymentResponse] = Field(default_factory=list)
