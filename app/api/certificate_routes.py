from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import Certificate

router = APIRouter(
    prefix="/api/certificates",
    tags=["Certificates"],
)


@router.get("/{certificate_id}/download")
def download_certificate(
    certificate_id: int,
    db: Session = Depends(get_db),
):
    certificate = (
        db.query(Certificate)
        .filter(Certificate.id == certificate_id)
        .first()
    )

    if not certificate:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found",
        )

    if certificate.status != "COMPLETED":
        raise HTTPException(
            status_code=409,
            detail="Certificate is not available",
        )

    if not certificate.file_path:
        raise HTTPException(
            status_code=404,
            detail="Certificate file not found",
        )

    return FileResponse(
        certificate.file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.id}.pdf",
    )