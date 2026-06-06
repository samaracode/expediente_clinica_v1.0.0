from fastapi import APIRouter
from app.api.v1 import auth, residents, admissions

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(residents.router, prefix="/residents", tags=["Residents"])
api_router.include_router(admissions.router, prefix="/admissions", tags=["Admissions"])
