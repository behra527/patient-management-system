from collections.abc import Callable
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.auth.dependencies import require_roles
from app.schemas.doctor import DoctorCreate, DoctorResponse, DoctorUpdate
from app.services import doctor_service


class Validation400Route(APIRoute):
    """Return HTTP 400 for request validation failures."""

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
    prefix="/doctors",
    tags=["Doctors"],
    route_class=Validation400Route,
)

DoctorId = Annotated[int, Path(gt=0)]
READ_ROLES = ["admin", "doctor", "receptionist"]


@router.post(
    "/",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles("admin"))],
)
def create_doctor(doctor: DoctorCreate) -> dict:
    try:
        return doctor_service.create_doctor(doctor.model_dump(mode="json"))
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get(
    "/",
    response_model=list[DoctorResponse],
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
def list_doctors() -> list[dict]:
    return doctor_service.list_doctors()


@router.get(
    "/{doctor_id}",
    response_model=DoctorResponse,
    dependencies=[Depends(require_roles(*READ_ROLES))],
)
def get_doctor(doctor_id: DoctorId) -> dict:
    doctor = doctor_service.get_doctor(doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.put(
    "/{doctor_id}",
    response_model=DoctorResponse,
    dependencies=[Depends(require_roles("admin"))],
)
def update_doctor(doctor_id: DoctorId, doctor: DoctorUpdate) -> dict:
    try:
        updated = doctor_service.update_doctor(
            doctor_id, doctor.model_dump(mode="json")
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    if updated is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return updated


@router.patch(
    "/{doctor_id}/deactivate",
    response_model=DoctorResponse,
    dependencies=[Depends(require_roles("admin"))],
)
def deactivate_doctor(doctor_id: DoctorId) -> dict:
    doctor = doctor_service.deactivate_doctor(doctor_id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

