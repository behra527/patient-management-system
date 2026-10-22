from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.routing import APIRoute
from pydantic import ValidationError

from app.auth.dependencies import get_current_user, require_roles
from app.schemas.billing import (
    InvoiceCreate,
    InvoiceDetailResponse,
    InvoiceResponse,
    PaymentCreate,
)
from app.services import billing_service


class Validation400Route(APIRoute):
    def get_route_handler(self):
        original_handler = super().get_route_handler()

        async def custom_handler(request):
            try:
                return await original_handler(request)
            except ValidationError as exc:
                raise HTTPException(
                    status_code=400,
                    detail=exc.errors(include_url=False),
                ) from exc

        return custom_handler


router = APIRouter(
    prefix="/billing",
    tags=["Billing & Invoices"],
    route_class=Validation400Route,
)


@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice(
    payload: InvoiceCreate,
    current_user=Depends(require_roles("admin", "receptionist")),
):
    try:
        return billing_service.create_invoice(payload.model_dump())
    except ValueError as exc:
        message = str(exc)
        code = 404 if message in {"Patient not found.", "Appointment not found."} else 409
        raise HTTPException(status_code=code, detail=message) from exc


@router.get("/invoices", response_model=list[InvoiceResponse])
def list_invoices(
    patient_id: int | None = Query(default=None, gt=0),
    invoice_status: str | None = Query(default=None, alias="status"),
    current_user=Depends(get_current_user),
):
    try:
        return billing_service.list_invoices(patient_id, invoice_status)
    except ValueError as exc:
        message = str(exc)
        code = 404 if message == "Patient not found." else 400
        raise HTTPException(status_code=code, detail=message) from exc


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceDetailResponse,
)
def get_invoice(
    invoice_id: int,
    current_user=Depends(get_current_user),
):
    try:
        return billing_service.get_invoice(invoice_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/invoices/{invoice_id}/payments",
    status_code=status.HTTP_201_CREATED,
)
def record_payment(
    invoice_id: int,
    payload: PaymentCreate,
    current_user=Depends(require_roles("admin", "receptionist")),
):
    try:
        return billing_service.record_payment(
            invoice_id,
            payload.model_dump(),
        )
    except ValueError as exc:
        message = str(exc)
        code = 404 if message == "Invoice not found." else 400
        raise HTTPException(status_code=code, detail=message) from exc
