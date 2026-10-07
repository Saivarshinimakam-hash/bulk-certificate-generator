from pathlib import Path

from app.services.certificate_generator import generate_certificate


def test_certificate_generation():
    file_path = generate_certificate(
        recipient_name="Test User",
        event_name="Test Event",
        certificate_title="Certificate of Completion",
        issuer="Test Organization",
        certificate_id=99999,
    )

    path = Path(file_path)

    assert path.exists()
    assert path.suffix == ".pdf"
    assert path.stat().st_size > 0

    path.unlink()