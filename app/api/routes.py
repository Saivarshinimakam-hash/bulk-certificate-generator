from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import GenerationJob, Certificate
from app.schemas.certificate import GenerationJobCreate
from app.services.job_processor import process_generation_job

router = APIRouter(prefix="/api/jobs", tags=["Generation Jobs"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_generation_job(
    request: GenerationJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job = GenerationJob(
        event_name=request.event_name,
        certificate_title=request.certificate_title,
        issuer=request.issuer,
        status="PENDING",
        total=len(request.recipients),
        completed=0,
        failed=0,
    )

    db.add(job)
    db.flush()

    for recipient in request.recipients:
        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status="PENDING",
        )
        db.add(certificate)

    db.commit()
    db.refresh(job)

    background_tasks.add_task(
        process_generation_job,
        job.id,
    )

    return {
        "job_id": job.id,
        "status": job.status,
        "total": job.total,
        "completed": job.completed,
        "failed": job.failed,
    }


@router.get("/{job_id}")
def get_generation_job(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(GenerationJob)
        .filter(GenerationJob.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found",
        )

    certificates = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .all()
    )

    return {
        "job_id": job.id,
        "event_name": job.event_name,
        "certificate_title": job.certificate_title,
        "issuer": job.issuer,
        "status": job.status,
        "total": job.total,
        "completed": job.completed,
        "failed": job.failed,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "certificates": [
            {
                "certificate_id": certificate.id,
                "recipient_name": certificate.recipient_name,
                "recipient_email": certificate.recipient_email,
                "status": certificate.status,
                "error_message": certificate.error_message,
            }
            for certificate in certificates
        ],
    }


@router.get("/{job_id}/certificates")
def get_job_certificates(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = (
        db.query(GenerationJob)
        .filter(GenerationJob.id == job_id)
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Generation job not found",
        )

    certificates = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .all()
    )

    return {
        "job_id": job.id,
        "certificates": [
            {
                "certificate_id": certificate.id,
                "recipient_name": certificate.recipient_name,
                "recipient_email": certificate.recipient_email,
                "status": certificate.status,
                "download_url": (
                    f"/api/certificates/{certificate.id}/download"
                    if certificate.status == "COMPLETED"
                    else None
                ),
                "error_message": certificate.error_message,
            }
            for certificate in certificates
        ],
    }