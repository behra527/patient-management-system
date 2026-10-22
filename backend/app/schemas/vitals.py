from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr,
    field_validator,
)


class BloodPressureSchema(BaseModel):
    """Validated systolic and diastolic blood pressure measurements."""

    model_config = ConfigDict(extra="forbid", strict=True)

    systolic: Annotated[StrictInt, Field(ge=50, le=300)]
    diastolic: Annotated[StrictInt, Field(ge=30, le=200)]


class VitalsCreateSchema(BaseModel):
    """Request schema for recording patient health metrics."""

    model_config = ConfigDict(extra="forbid", strict=True)

    patient_id: Annotated[StrictStr, Field(min_length=1, max_length=100)]
    age: Annotated[StrictInt, Field(ge=0, le=120)]
    blood_pressure: BloodPressureSchema
    glucose_level: Annotated[float, Field(gt=0, allow_inf_nan=False)]

    @field_validator("patient_id")
    @classmethod
    def validate_patient_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("patient_id must not be empty or whitespace")
        return value.strip()


class VitalsResponseSchema(VitalsCreateSchema):
    """Persisted vitals record returned by the API."""

    id: int
    recorded_at: str


class VitalsSummarySchema(BaseModel):
    """Aggregated metrics for a patient's recorded vitals."""

    patient_id: str
    average_systolic: float
    average_diastolic: float
    average_glucose_level: float
    total_records: int
