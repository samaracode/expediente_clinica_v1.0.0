from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.file import File as FileModel
from app.models.user import User
from app.schemas.file import FileOut
from app.services import storage_service

router = APIRouter()


def _build_out(f: FileModel, db: Session) -> FileOut:
    url = storage_service.get_file_url(f.id, f.s3_bucket, f.s3_key)
    return FileOut(
        id=f.id,
        file_name=f.file_name,
        mime_type=f.mime_type,
        entity_type=f.entity_type,
        entity_id=f.entity_id,
        uploaded_by_id=f.uploaded_by_id,
        uploaded_at=f.uploaded_at,
        url=url,
    )


@router.post("", response_model=FileOut, status_code=201)
async def upload_file(
    file: UploadFile = File(..., description="Archivo a subir (imagen o PDF)"),
    entity_type: Optional[str] = Form(None, description="Tipo de entidad asociada, ej. 'medication_order'"),
    entity_id: Optional[int] = Form(None, description="ID de la entidad asociada"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Sube un archivo (multipart/form-data).

    Campos del form:
    - **file**: binario del archivo (jpeg, png, webp o pdf).
    - **entity_type** *(opcional)*: tipo de entidad a la que se adjunta (ej. `medication_order`).
    - **entity_id** *(opcional)*: ID de esa entidad.

    Devuelve los metadatos del archivo creado, incluyendo la URL de acceso.
    """
    content = await file.read()
    mime_type = file.content_type or ""

    try:
        s3_bucket, s3_key = storage_service.store_file(
            content=content,
            original_filename=file.filename or "archivo",
            mime_type=mime_type,
        )
    except ValueError as exc:
        # Distinguir entre error de mime type (400) y tamaño excedido (413)
        msg = str(exc)
        if "Tipo de archivo no permitido" in msg:
            raise HTTPException(status_code=400, detail=msg)
        raise HTTPException(status_code=413, detail=msg)

    record = FileModel(
        s3_key=s3_key,
        s3_bucket=s3_bucket,
        file_name=file.filename or "archivo",
        mime_type=mime_type,
        entity_type=entity_type,
        entity_id=entity_id,
        uploaded_by_id=current_user.id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return _build_out(record, db)


@router.get("/{file_id}", response_model=FileOut)
def get_file_metadata(
    file_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Devuelve los metadatos de un archivo y la URL para acceder a él.

    - Backend **local**: la URL apunta a `GET /files/{id}/content`.
    - Backend **S3**: la URL es una URL prefirmada con validez de 1 hora.
    """
    record = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return _build_out(record, db)


@router.get("/{file_id}/content")
def serve_file_content(
    file_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Sirve el contenido binario del archivo (solo disponible en backend local).

    Para el backend S3, usar la URL prefirmada devuelta por `GET /files/{id}`.
    """
    record = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")

    if record.s3_bucket != storage_service.LOCAL_BACKEND_MARKER:
        raise HTTPException(
            status_code=400,
            detail="Este endpoint solo está disponible para almacenamiento local. "
                   "Usá la URL prefirmada devuelta por GET /files/{id}.",
        )

    try:
        content = storage_service.read_local(record.s3_key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Contenido del archivo no encontrado en disco")

    return Response(
        content=content,
        media_type=record.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{record.file_name}"'},
    )
