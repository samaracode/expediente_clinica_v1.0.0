# Patch JSONB to JSON for SQLite compatibility — MUST be before any model import
from sqlalchemy.dialects import postgresql as _pg
from sqlalchemy import types as _sa_types

_pg.JSONB = _sa_types.JSON

import io
import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException

from app.models.file import File as FileModel
from app.services import storage_service
from app.services.storage_service import (
    validate_upload,
    store_local,
    read_local,
    store_file,
    get_file_url,
    LOCAL_BACKEND_MARKER,
    ALLOWED_MIME_TYPES,
)
from app.core.config import settings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_content(mb: float) -> bytes:
    return b"x" * int(mb * 1024 * 1024)


# ---------------------------------------------------------------------------
# validate_upload — unit tests (no BD)
# ---------------------------------------------------------------------------

class TestValidateUpload:
    def test_valid_jpeg(self):
        validate_upload(b"data", "image/jpeg")  # no lanza

    def test_valid_png(self):
        validate_upload(b"data", "image/png")

    def test_valid_webp(self):
        validate_upload(b"data", "image/webp")

    def test_valid_pdf(self):
        validate_upload(b"data", "application/pdf")

    def test_invalid_mime_raises(self):
        with pytest.raises(ValueError, match="Tipo de archivo no permitido"):
            validate_upload(b"data", "text/plain")

    def test_invalid_mime_svg_raises(self):
        with pytest.raises(ValueError, match="Tipo de archivo no permitido"):
            validate_upload(b"data", "image/svg+xml")

    def test_empty_mime_raises(self):
        with pytest.raises(ValueError, match="Tipo de archivo no permitido"):
            validate_upload(b"data", "")

    def test_size_over_limit_raises(self):
        big = _make_content(settings.MAX_UPLOAD_MB + 1)
        with pytest.raises(ValueError, match="tamaño máximo"):
            validate_upload(big, "image/jpeg")

    def test_size_exactly_at_limit_ok(self):
        # Exactly MAX_UPLOAD_MB is still valid (boundary inclusive)
        exact = _make_content(settings.MAX_UPLOAD_MB)
        validate_upload(exact, "image/jpeg")  # no lanza

    def test_size_just_over_limit_raises(self):
        over = _make_content(settings.MAX_UPLOAD_MB) + b"1"
        with pytest.raises(ValueError, match="tamaño máximo"):
            validate_upload(over, "image/jpeg")


# ---------------------------------------------------------------------------
# store_local / read_local — unit tests (usa tmp dir real)
# ---------------------------------------------------------------------------

class TestLocalStorage:
    def test_store_creates_file(self, tmp_path):
        with patch.object(settings, "LOCAL_STORAGE_DIR", str(tmp_path)):
            bucket, key = store_local(b"hello", "test.jpg")
        assert bucket == LOCAL_BACKEND_MARKER
        assert key.endswith("/test.jpg")
        dest = os.path.join(str(tmp_path), key)
        assert os.path.exists(dest)

    def test_read_returns_content(self, tmp_path):
        with patch.object(settings, "LOCAL_STORAGE_DIR", str(tmp_path)):
            _, key = store_local(b"hello file", "foto.png")
            data = read_local(key)
        assert data == b"hello file"

    def test_read_missing_file_raises(self, tmp_path):
        with patch.object(settings, "LOCAL_STORAGE_DIR", str(tmp_path)):
            with pytest.raises(FileNotFoundError):
                read_local("nonexistent/file.jpg")

    def test_store_unique_keys(self, tmp_path):
        with patch.object(settings, "LOCAL_STORAGE_DIR", str(tmp_path)):
            _, key1 = store_local(b"a", "foto.jpg")
            _, key2 = store_local(b"b", "foto.jpg")
        assert key1 != key2


# ---------------------------------------------------------------------------
# store_file — integración con validación
# ---------------------------------------------------------------------------

class TestStoreFile:
    def test_local_backend_stores_ok(self, tmp_path):
        with patch.object(settings, "STORAGE_BACKEND", "local"), \
             patch.object(settings, "LOCAL_STORAGE_DIR", str(tmp_path)):
            bucket, key = store_file(b"img", "photo.jpg", "image/jpeg")
        assert bucket == LOCAL_BACKEND_MARKER
        assert key.endswith("/photo.jpg")

    def test_invalid_mime_raises_before_storage(self, tmp_path):
        with patch.object(settings, "STORAGE_BACKEND", "local"), \
             patch.object(settings, "LOCAL_STORAGE_DIR", str(tmp_path)):
            with pytest.raises(ValueError, match="Tipo de archivo no permitido"):
                store_file(b"data", "malware.exe", "application/x-msdownload")

    def test_oversized_raises_before_storage(self, tmp_path):
        big = _make_content(settings.MAX_UPLOAD_MB + 1)
        with patch.object(settings, "STORAGE_BACKEND", "local"), \
             patch.object(settings, "LOCAL_STORAGE_DIR", str(tmp_path)):
            with pytest.raises(ValueError, match="tamaño máximo"):
                store_file(big, "big.pdf", "application/pdf")


# ---------------------------------------------------------------------------
# FileModel — tests de integración con BD SQLite
# ---------------------------------------------------------------------------

# Importar conftest para reutilizar la fixture `db`
# (conftest.py ya importa todos los modelos necesarios)

class TestFileModel:
    def test_create_file_record(self, db):
        """Verifica que el modelo File se persiste correctamente."""
        record = FileModel(
            s3_key="abc123/foto.jpg",
            s3_bucket=LOCAL_BACKEND_MARKER,
            file_name="foto.jpg",
            mime_type="image/jpeg",
            entity_type="medication_order",
            entity_id=42,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        assert record.id is not None
        assert record.s3_key == "abc123/foto.jpg"
        assert record.s3_bucket == LOCAL_BACKEND_MARKER
        assert record.entity_type == "medication_order"
        assert record.entity_id == 42

    def test_get_file_url_local(self, db):
        """get_file_url devuelve ruta interna para backend local."""
        record = FileModel(
            s3_key="abc/file.pdf",
            s3_bucket=LOCAL_BACKEND_MARKER,
            file_name="file.pdf",
            mime_type="application/pdf",
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        url = get_file_url(record.id, record.s3_bucket, record.s3_key)
        assert url == f"/api/v1/files/{record.id}/content"

    def test_file_not_found_in_db(self, db):
        """Querying un ID inexistente devuelve None."""
        result = db.query(FileModel).filter(FileModel.id == 9999).first()
        assert result is None

    def test_uploaded_by_id_fk(self, db, make_user):
        """uploaded_by_id referencia correctamente a users."""
        user = make_user()
        record = FileModel(
            s3_key="xyz/imagen.png",
            s3_bucket=LOCAL_BACKEND_MARKER,
            file_name="imagen.png",
            mime_type="image/png",
            uploaded_by_id=user.id,
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        assert record.uploaded_by_id == user.id
