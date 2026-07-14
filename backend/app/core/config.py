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

    # Orígenes CORS permitidos (frontend). Coma-separados.
    # En producción incluir la URL de Vercel, p.ej.:
    #   CORS_ORIGINS=https://zoe-clinic.vercel.app
    CORS_ORIGINS: str = "http://localhost:3005,http://127.0.0.1:3005"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # Configuración de la cookie de sesión.
    # En producción el frontend (Vercel) y la API (Render) están en dominios
    # distintos sobre HTTPS -> la cookie debe ser cross-site:
    #   COOKIE_SECURE=true  y  COOKIE_SAMESITE=none
    # En desarrollo local (HTTP, mismo host) se dejan en false / lax.
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"

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

    # AWS / S3 (compatible con Cloudflare R2, Backblaze B2, MinIO, etc.)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "zoe-clinic-files"
    # Endpoint S3 personalizado. Vacío = AWS S3 estándar.
    # Para Cloudflare R2: https://<account_id>.r2.cloudflarestorage.com
    S3_ENDPOINT_URL: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Asistente "Ask AI" (consulta de datos por lenguaje natural).
    # ------------------------------------------------------------------ #
    # Proveedor del modelo: "anthropic" (Claude), "deepseek", "gemini" o "groq".
    # Permite probar otro proveedor sin tocar código, solo cambiando esta
    # variable (y reiniciando el backend).
    ASSISTANT_PROVIDER: str = "anthropic"

    # -- Anthropic (Claude) -- #
    # Llave de la API de Anthropic. Si está vacía y el proveedor es "anthropic",
    # el asistente responde que no está configurado (no rompe el resto del sistema).
    ANTHROPIC_API_KEY: Optional[str] = None
    # Modelo por defecto: Haiku 4.5 (barato y rápido para consultas de datos).
    ASSISTANT_MODEL_ANTHROPIC: str = "claude-haiku-4-5"

    # -- DeepSeek -- #
    # Llave de la API de DeepSeek (https://platform.deepseek.com). DeepSeek
    # expone una API compatible con el formato de OpenAI.
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    # "deepseek-chat" (modelo general) o "deepseek-reasoner" (con razonamiento).
    ASSISTANT_MODEL_DEEPSEEK: str = "deepseek-chat"

    # -- Gemini (Google AI Studio) -- #
    # Llave gratuita: https://aistudio.google.com/apikey (sin tarjeta).
    # AVISO DE PRIVACIDAD: en el free tier, Google puede usar las peticiones
    # para mejorar sus modelos. No usar con datos reales de residentes/PHI —
    # solo para pruebas o para el modo "cómo usar el sistema" (manual).
    GEMINI_API_KEY: Optional[str] = None
    ASSISTANT_MODEL_GEMINI: str = "gemini-2.0-flash"

    # -- Groq -- #
    # Llave gratuita: https://console.groq.com/keys (sin tarjeta). Groq expone
    # una API compatible con el formato de OpenAI y sirve modelos open-weight
    # (Llama, etc.) sobre hardware propio (LPU), muy rápido. Free tier con
    # límites de requests por minuto/día, igual que Gemini.
    GROQ_API_KEY: Optional[str] = None
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    ASSISTANT_MODEL_GROQ: str = "llama-3.3-70b-versatile"

    # Tope de gasto mensual en USD (aplica al proveedor activo). Al superarlo,
    # el asistente se desactiva solo y pide contactar al administrador.
    # Se reinicia solo cada mes. Con Gemini (free tier, costo $0) este tope
    # prácticamente nunca se alcanza por dinero — el límite real es el rate
    # limit del free tier, que la API devuelve como error 429.
    ASSISTANT_MONTHLY_BUDGET_USD: float = 10.0
    # Prompt caching del prefijo estable (system + tools). Activo por defecto
    # porque la app cambia poco; se puede desactivar para depurar costos.
    # Nota: hoy solo tiene efecto con el proveedor Anthropic (prompt caching
    # nativo de Claude); DeepSeek, Gemini y Groq cachean automáticamente en su
    # propio backend.
    ASSISTANT_PROMPT_CACHE: bool = True

    @property
    def assistant_model(self) -> str:
        """Modelo efectivo según el proveedor activo."""
        if self.ASSISTANT_PROVIDER == "deepseek":
            return self.ASSISTANT_MODEL_DEEPSEEK
        if self.ASSISTANT_PROVIDER == "gemini":
            return self.ASSISTANT_MODEL_GEMINI
        if self.ASSISTANT_PROVIDER == "groq":
            return self.ASSISTANT_MODEL_GROQ
        return self.ASSISTANT_MODEL_ANTHROPIC

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
