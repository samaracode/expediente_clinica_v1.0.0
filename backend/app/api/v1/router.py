from fastapi import APIRouter
from app.api.v1 import (
    auth,
    residents,
    admissions,
    consents,
    personal_items,
    economic_situation,
    medical,
    therapeutic,
    social_work,
    psychology,
    occupational_therapy,
    treatment,
    exit_passes,
    daily_logs,
    users,
    professionals,
    reports,
    consultations,
    relatives,
    export,
    notifications,
    files,
    allergies,
    medication_slots,
)
from app.api.v1.medications import (
    medications_router,
    admissions_medication_router,
    orders_router,
    administrations_router,
)
from app.api.v1.attendance import attendance_router, admissions_attendance_router

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(residents.router, prefix="/residents", tags=["Residents"])
api_router.include_router(admissions.router, prefix="/admissions", tags=["Admissions"])
api_router.include_router(consents.router, prefix="/admissions", tags=["Consents"])
api_router.include_router(personal_items.router, prefix="/admissions", tags=["Personal Items"])
api_router.include_router(economic_situation.router, prefix="/admissions", tags=["Economic Situation"])
api_router.include_router(medical.router, prefix="/admissions", tags=["Medical"])
api_router.include_router(therapeutic.router, prefix="/admissions", tags=["Therapeutic"])
api_router.include_router(social_work.router, prefix="/admissions", tags=["Social Work"])
api_router.include_router(psychology.router, prefix="/admissions", tags=["Psychology"])
api_router.include_router(occupational_therapy.router, prefix="/admissions", tags=["Occupational Therapy"])
api_router.include_router(treatment.router, prefix="/admissions", tags=["Treatment Plan"])
api_router.include_router(exit_passes.router, prefix="/admissions", tags=["Exit Passes"])
api_router.include_router(daily_logs.router, prefix="/admissions", tags=["Daily Logs"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(professionals.router, prefix="/professionals", tags=["Professionals"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(consultations.router, prefix="/admissions", tags=["Consultations"])
api_router.include_router(relatives.router, prefix="/residents", tags=["Relatives"])
api_router.include_router(export.router, prefix="/admissions", tags=["Export"])
api_router.include_router(notifications.router, tags=["Notifications"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])

# Módulo de Medicamentos (MAR) — Fase 1B
api_router.include_router(medications_router, prefix="/medications", tags=["Medications"])
api_router.include_router(admissions_medication_router, prefix="/admissions", tags=["Medication Orders"])
api_router.include_router(orders_router, prefix="/medication-orders", tags=["Medication Orders"])
api_router.include_router(administrations_router, prefix="/medication-administrations", tags=["Medication Administrations"])
api_router.include_router(allergies.router, prefix="/residents", tags=["Allergies"])
api_router.include_router(medication_slots.router, prefix="/settings", tags=["Settings"])

# Módulo de Asistencia — Fase 2
api_router.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
api_router.include_router(admissions_attendance_router, prefix="/admissions", tags=["Attendance"])
