from collections.abc import Callable
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette import status

from app.auth.dependencies import require_roles
from app.schemas.vitals import (
    VitalsCreateSchema,
    VitalsResponseSchema,
    VitalsSummarySchema,
)
from app.services import vitals_service


class Validation400Route(APIRoute):
    """Return HTTP 400 for request validation failures on Vitals routes."""

    def get_route_handler(self) -> Callable:
        original_handler = super().get_route_handler()

        async def custom_handler(request: Request) -> Response:
            try:
                return await original_handler(request)
            except RequestValidationError as exc:
                errors = [
                    {
                        "field": ".".join(str(part) for part in error["loc"]),
                        "message": error["msg"],
                        "type": error["type"],
                    }
                    for error in exc.errors()
                ]

                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "detail": "Request validation failed",
                        "errors": errors,
                    },
                )

        return custom_handler


router = APIRouter(
    tags=["Vitals"],
    route_class=Validation400Route,
)


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return service status and the current UTC timestamp."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post(
    "/vitals",
    response_model=VitalsResponseSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "doctor", "receptionist"))],
)
def create_vitals(payload: VitalsCreateSchema) -> dict:
    """Validate and store a patient vitals record."""
    try:
        return vitals_service.record_vitals(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/patients/{patient_id}/vitals",
    response_model=list[VitalsResponseSchema],
    dependencies=[Depends(require_roles("admin", "doctor", "receptionist"))],
)
def get_patient_vitals(
    patient_id: str,
    limit: int | None = Query(default=None, ge=1),
) -> list[dict]:
    """Return historical vitals records, newest first."""
    try:
        return vitals_service.get_vitals_history(patient_id, limit)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/patients/{patient_id}/summary",
    response_model=VitalsSummarySchema,
    dependencies=[Depends(require_roles("admin", "doctor", "receptionist"))],
)
def get_patient_vitals_summary(patient_id: str) -> dict:
    """Return average measurements and the total record count."""
    try:
        return vitals_service.get_vitals_summary(patient_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
