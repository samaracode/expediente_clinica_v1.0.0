from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import app.db.base  # noqa: F401 — registers all ORM models with SQLAlchemy mapper
from app.api.v1.router import api_router

app = FastAPI(
    title="Expediente Clínico ZOE - API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = [
    "http://localhost:3005",
    "http://127.0.0.1:3005",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "message": "Expediente Clínico ZOE API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8005, reload=True)
