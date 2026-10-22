
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.billing_controller import router as billing_router
from app.controllers.auth_controller import router as auth_router
from app.controllers.appointment_controller import router as appointment_router
from app.controllers.doctor_controller import router as doctor_router
from app.controllers.patient_controller import router as patient_router
from app.controllers.vitals_controller import router as vitals_router
from app.database.connection import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(
    title="Patient Record Management API",
    description="API for managing patient records.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for the Next.js frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers.
app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(vitals_router)
app.include_router(auth_router)
app.include_router(appointment_router)
app.include_router(billing_router)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "Patient Record Management API",
    }
