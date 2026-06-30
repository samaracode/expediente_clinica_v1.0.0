import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pdfkit
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.services.export_service import ExportService

router = APIRouter()


def get_export_service(db: Session = Depends(get_db)) -> ExportService:
    return ExportService(db)


def _jinja_env() -> Environment:
    templates_path = Path(__file__).parent.parent.parent / "templates"
    return Environment(loader=FileSystemLoader(str(templates_path)), autoescape=True)


@router.get("/{admission_id}/export/pdf")
def export_admission_pdf(
    admission_id: int,
    bg: BackgroundTasks,
    service: ExportService = Depends(get_export_service),
    _: object = Depends(get_current_user),
):
    ctx = service.get_admission_export_context(admission_id)

    generated_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    ctx["generated_at"] = generated_at

    env = _jinja_env()
    template = env.get_template("admission_report.html")
    html = template.render(**ctx)

    options = {
        "page-size": "A4",
        "margin-top": "0mm",
        "margin-right": "0mm",
        "margin-bottom": "0mm",
        "margin-left": "0mm",
        "encoding": "UTF-8",
        "no-outline": None,
        "enable-local-file-access": None,
    }

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        pdfkit.from_string(html, tmp_path, options=options)
    except Exception as exc:
        os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {exc}") from exc

    bg.add_task(os.unlink, tmp_path)
    admission = ctx["admission"]
    filename = f"expediente_{admission.admission_number}.pdf"
    return FileResponse(path=tmp_path, media_type="application/pdf", filename=filename)
