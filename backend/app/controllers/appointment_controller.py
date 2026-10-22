from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.auth.dependencies import require_roles
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentStatus,
    AppointmentStatusUpdate,
)
from app.services import appointment_service


class Validation400Route(APIRoute):
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
    prefix="/appointments",
    tags=["Appointments"],
    route_class=Validation400Route,
)
AppointmentId = Annotated[int, Path(gt=0)]


@router.post(
    "/",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin", "receptionist"))],
)
def create_appointment(payload: AppointmentCreate) -> dict:
    try:
        return appointment_service.create_appointment(
            payload.model_dump(mode="json")
        )
    except ValueError as error:
        message = str(error)
        code = 409 if "overlapping" in message else 400
        if message in ("Patient not found", "Doctor not found"):
            code = 404
        raise HTTPException(status_code=code, detail=message) from error


@router.get(
    "/",
    response_model=list[AppointmentResponse],
    dependencies=[Depends(require_roles("admin", "doctor", "receptionist"))],
)
def list_appointments(
    patient_id: int | None = Query(default=None, gt=0),
    doctor_id: int | None = Query(default=None, gt=0),
    appointment_status: AppointmentStatus | None = Query(default=None, alias="status"),
) -> list[dict]:
    return appointment_service.list_appointments(
        patient_id, doctor_id, appointment_status
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
    dependencies=[Depends(require_roles("admin", "doctor", "receptionist"))],
)
def get_appointment(appointment_id: AppointmentId) -> dict:
    appointment = appointment_service.get_appointment(appointment_id)
    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.patch(
    "/{appointment_id}/status",
    response_model=AppointmentResponse,
    dependencies=[Depends(require_roles("admin", "doctor", "receptionist"))],
)
def update_appointment_status(
    appointment_id: AppointmentId,
    payload: AppointmentStatusUpdate,
) -> dict:
    try:
        appointment = appointment_service.update_appointment_status(
            appointment_id, payload.status
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    if appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment
