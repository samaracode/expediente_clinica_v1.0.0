"""
Servicio de almacenamiento de archivos.

Soporta dos backends seleccionables por configuración (STORAGE_BACKEND):
  - "local": guarda en disco, bajo LOCAL_STORAGE_DIR.
  - "s3": sube a AWS S3.

Mapeo a los campos s3_key / s3_bucket del modelo File:
  - Backend LOCAL:
      s3_bucket = "local"            (constante que identifica el backend)
      s3_key    = "<uuid>/<filename>" (ruta relativa dentro de LOCAL_STORAGE_DIR)
  - Backend S3:
      s3_bucket = settings.S3_BUCKET_NAME
      s3_key    = "<uuid>/<filename>"  (key en el bucket S3)
"""

import io
import os
import uuid
from typing import Tuple

from app.core.config import settings

# Tipos MIME permitidos para subida de archivos
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}

# Constante usada en s3_bucket para el backend local
LOCAL_BACKEND_MARKER = "local"


def validate_upload(content: bytes, mime_type: str) -> None:
    """
    Valida mime_type y tamaño del archivo.
    Lanza ValueError con mensaje en español si no cumple.
    """
    if mime_type not in ALLOWED_MIME_TYPES:
        tipos = ", ".join(sorted(ALLOWED_MIME_TYPES))
        raise ValueError(
            f"Tipo de archivo no permitido: '{mime_type}'. "
            f"Tipos aceptados: {tipos}."
        )
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise ValueError(
            f"El archivo excede el tamaño máximo permitido de {settings.MAX_UPLOAD_MB} MB "
            f"({len(content) // (1024 * 1024)} MB recibidos)."
        )


def _build_key(original_filename: str) -> str:
    """Genera una clave única con UUID para evitar colisiones."""
    uid = uuid.uuid4().hex
    safe_name = os.path.basename(original_filename)
    return f"{uid}/{safe_name}"


# ---------------------------------------------------------------------------
# Backend: LOCAL
# ---------------------------------------------------------------------------

def store_local(content: bytes, original_filename: str) -> Tuple[str, str]:
    """
    Guarda el archivo en disco bajo LOCAL_STORAGE_DIR.
    Devuelve (s3_bucket, s3_key) siguiendo la convención del modelo.
    """
    key = _build_key(original_filename)
    dest_path = os.path.join(settings.LOCAL_STORAGE_DIR, key)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(content)
    return LOCAL_BACKEND_MARKER, key


def read_local(s3_key: str) -> bytes:
    """Lee un archivo desde almacenamiento local."""
    path = os.path.join(settings.LOCAL_STORAGE_DIR, s3_key)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado en disco: {s3_key}")
    with open(path, "rb") as f:
        return f.read()


def build_local_url(file_id: int) -> str:
    """URL de descarga para el backend local (ruta de la propia API)."""
    return f"/api/v1/files/{file_id}/content"


# ---------------------------------------------------------------------------
# Backend: S3 (compatible con AWS S3 y Cloudflare R2 / cualquier S3-compatible)
# ---------------------------------------------------------------------------

def _s3_client():
    """
    Crea un cliente boto3 S3.

    Si S3_ENDPOINT_URL está configurado (p.ej. Cloudflare R2), apunta ahí;
    de lo contrario usa AWS S3 estándar. La API es idéntica en ambos casos.
    """
    try:
        import boto3  # type: ignore
    except ImportError:
        raise RuntimeError("boto3 no está instalado. Instalá con: pip install boto3")

    return boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL or None,
    )


def store_s3(content: bytes, original_filename: str) -> Tuple[str, str]:
    """
    Sube el archivo a S3 (o R2).
    Devuelve (s3_bucket, s3_key).
    Requiere boto3 y credenciales configuradas.
    """
    key = _build_key(original_filename)
    _s3_client().put_object(
        Bucket=settings.S3_BUCKET_NAME,
        Key=key,
        Body=content,
    )
    return settings.S3_BUCKET_NAME, key


def build_presigned_url(s3_bucket: str, s3_key: str, expires_in: int = 3600) -> str:
    """
    Genera una URL prefirmada para acceso temporal al archivo.
    Funciona igual en AWS S3 y Cloudflare R2.
    expires_in: segundos de validez (default 1 hora).
    """
    return _s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": s3_bucket, "Key": s3_key},
        ExpiresIn=expires_in,
    )


# ---------------------------------------------------------------------------
# Fachada pública
# ---------------------------------------------------------------------------

def store_file(content: bytes, original_filename: str, mime_type: str) -> Tuple[str, str]:
    """
    Valida y almacena el archivo en el backend configurado.
    Devuelve (s3_bucket, s3_key) para persistir en el modelo File.
    Lanza ValueError si mime_type o tamaño no son válidos.
    """
    validate_upload(content, mime_type)
    if settings.STORAGE_BACKEND == "s3":
        return store_s3(content, original_filename)
    return store_local(content, original_filename)


def get_file_url(file_id: int, s3_bucket: str, s3_key: str) -> str:
    """
    Devuelve la URL de acceso al archivo según el backend.
    - Local: URL interna de la API (/api/v1/files/{id}/content).
    - S3:    URL prefirmada de AWS con validez de 1 hora.
    """
    if s3_bucket == LOCAL_BACKEND_MARKER:
        return build_local_url(file_id)
    return build_presigned_url(s3_bucket, s3_key)
