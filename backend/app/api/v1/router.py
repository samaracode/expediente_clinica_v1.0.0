from fastapi import APIRouter
from app.api.v1 import auth, residents, admissions, consents, personal_items, economic_situation

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(residents.router, prefix="/residents", tags=["Residents"])
api_router.include_router(admissions.router, prefix="/admissions", tags=["Admissions"])
api_router.include_router(consents.router, prefix="/admissions", tags=["Consents"])
api_router.include_router(personal_items.router, prefix="/admissions", tags=["Personal Items"])
api_router.include_router(economic_situation.router, prefix="/admissions", tags=["Economic Situation"])
