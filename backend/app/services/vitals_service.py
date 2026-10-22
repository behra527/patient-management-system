from typing import Any

from app.repositories import vitals_repository
from app.schemas.vitals import VitalsCreateSchema


def record_vitals(
    payload: VitalsCreateSchema,
) -> dict[str, Any]:
    """Validate and persist a patient's vitals record."""
    validated_data = payload.model_dump()

    return vitals_repository.create_vitals(validated_data)


def get_vitals_history(
    patient_id: str,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Retrieve a patient's historical vitals records."""
    normalized_patient_id = _normalize_patient_id(patient_id)

    if limit is not None and limit < 1:
        raise ValueError("limit must be greater than zero")

    return vitals_repository.get_patient_vitals(
        patient_id=normalized_patient_id,
        limit=limit,
    )


def get_vitals_summary(patient_id: str) -> dict[str, Any]:
    """Return aggregate vitals metrics for a patient."""
    normalized_patient_id = _normalize_patient_id(patient_id)

    return vitals_repository.get_patient_vitals_summary(
        normalized_patient_id
    )


def _normalize_patient_id(patient_id: str) -> str:
    """Reject empty patient identifiers and normalize surrounding whitespace."""
    if not isinstance(patient_id, str) or not patient_id.strip():
        raise ValueError("patient_id must not be empty")

    return patient_id.strip()
