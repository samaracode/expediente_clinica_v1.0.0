import os
from typing import Optional
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Cargar desde backend/.env si existe, si no busca en el ambiente
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    DATABASE_URL: str

    # Almacenamiento de archivos
    # STORAGE_BACKEND: "local" para desarrollo (disco), "s3" para producción.
    STORAGE_BACKEND: str = "local"
    # Directorio raíz para almacenamiento local. Se crea automáticamente si no existe.
    LOCAL_STORAGE_DIR: str = "/tmp/zoe_uploads"
    # Tamaño máximo de archivo en MB (validación en upload endpoint).
    MAX_UPLOAD_MB: int = 10

    # Módulo de medicamentos
    # Minutos de margen antes de marcar una toma scheduled como vencida
    MED_OMITTED_MARGIN_MIN: int = 60

    # AWS / S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "zoe-clinic-files"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> str:
        if isinstance(v, str):
            # En caso de usar postgresql:// en lugar de postgresql+psycopg2://
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+psycopg2://", 1)
            return v
        raise ValueError("DATABASE_URL must be a valid connection string")

settings = Settings()
