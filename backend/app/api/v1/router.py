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
)

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
