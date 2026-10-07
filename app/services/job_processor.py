from datetime import datetime

from app.database.database import SessionLocal
from app.database.models import GenerationJob, Certificate
from app.services.certificate_generator import generate_certificate


def process_generation_job(job_id: int) -> None:
    """
    Process all certificates belonging to a generation job.

    Each certificate is processed independently so that
    one failure does not stop the remaining certificates.
    """

    db = SessionLocal()

    try:
        job = db.query(GenerationJob).filter(
            GenerationJob.id == job_id
        ).first()

        if not job:
            return

        job.status = "PROCESSING"
        db.commit()

        certificates = (
            db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .all()
        )

        for certificate in certificates:
            try:
                file_path = generate_certificate(
                    recipient_name=certificate.recipient_name,
                    event_name=job.event_name,
                    certificate_title=job.certificate_title,
                    issuer=job.issuer,
                    certificate_id=certificate.id,
                )

                certificate.status = "COMPLETED"
                certificate.file_path = file_path
                certificate.error_message = None

                job.completed += 1

            except Exception as exc:
                certificate.status = "FAILED"
                certificate.error_message = str(exc)

                job.failed += 1

            db.commit()

        if job.failed == 0:
            job.status = "COMPLETED"
        elif job.completed > 0:
            job.status = "COMPLETED_WITH_ERRORS"
        else:
            job.status = "FAILED"

        job.completed_at = datetime.utcnow()

        db.commit()

    finally:
        db.close()