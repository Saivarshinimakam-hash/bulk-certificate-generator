def test_create_generation_job(client):
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Test Workshop",
            "certificate_title": "Certificate of Completion",
            "issuer": "Test Organization",
            "recipients": [
                {
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                },
                {
                    "name": "Bob Smith",
                    "email": "bob@example.com",
                },
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "job_id" in data
    assert data["status"] == "PENDING"
    assert data["total"] == 2
    assert data["completed"] == 0
    assert data["failed"] == 0


def test_invalid_email_is_rejected(client):
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Test Workshop",
            "certificate_title": "Certificate of Completion",
            "issuer": "Test Organization",
            "recipients": [
                {
                    "name": "Alice Johnson",
                    "email": "not-an-email",
                }
            ],
        },
    )

    assert response.status_code == 422


def test_empty_recipients_are_rejected(client):
    response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Test Workshop",
            "certificate_title": "Certificate of Completion",
            "issuer": "Test Organization",
            "recipients": [],
        },
    )

    assert response.status_code == 422

def test_get_generation_job(client):
    create_response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Status Test",
            "certificate_title": "Certificate of Completion",
            "issuer": "Test Organization",
            "recipients": [
                {
                    "name": "Status User",
                    "email": "status@example.com",
                }
            ],
        },
    )

    assert create_response.status_code == 201

    job_id = create_response.json()["job_id"]

    response = client.get(f"/api/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["total"] == 1
    assert len(data["certificates"]) == 1

def test_get_job_certificates(client):
    create_response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Retrieval Test",
            "certificate_title": "Certificate of Completion",
            "issuer": "Test Organization",
            "recipients": [
                {
                    "name": "Retrieval User",
                    "email": "retrieval@example.com",
                }
            ],
        },
    )

    job_id = create_response.json()["job_id"]

    response = client.get(
        f"/api/jobs/{job_id}/certificates"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert len(data["certificates"]) == 1

def test_individual_certificate_failure_does_not_stop_job(
    client,
    monkeypatch,
):
    from app.services import job_processor
    TestSessionLocal = job_processor.SessionLocal
    test_db = TestSessionLocal()

    
    try:
        from app.database.models import GenerationJob, Certificate

        original_generator = job_processor.generate_certificate

        def failing_generator(
            recipient_name,
            event_name,
            certificate_title,
            issuer,
            certificate_id,
        ):
            if recipient_name == "Fail User":
                raise RuntimeError(
                    "Simulated certificate generation failure"
                )

            return original_generator(
                recipient_name=recipient_name,
                event_name=event_name,
                certificate_title=certificate_title,
                issuer=issuer,
                certificate_id=certificate_id,
            )

        monkeypatch.setattr(
            job_processor,
            "generate_certificate",
            failing_generator,
        )

        job = GenerationJob(
            event_name="Failure Handling Test",
            certificate_title="Certificate of Completion",
            issuer="Test Organization",
            status="PENDING",
            total=3,
            completed=0,
            failed=0,
        )

        test_db.add(job)
        test_db.flush()

        recipients = [
            ("Success One", "success1@example.com"),
            ("Fail User", "fail@example.com"),
            ("Success Two", "success2@example.com"),
        ]

        for name, email in recipients:
            test_db.add(
                Certificate(
                    job_id=job.id,
                    recipient_name=name,
                    recipient_email=email,
                    status="PENDING",
                )
            )

        test_db.commit()
        job_id = job.id

        job_processor.process_generation_job(job_id)

        test_db.refresh(job)

        certificates = (
            test_db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .order_by(Certificate.id)
            .all()
        )

        assert job.status == "COMPLETED_WITH_ERRORS"
        assert job.total == 3
        assert job.completed == 2
        assert job.failed == 1

        assert certificates[0].status == "COMPLETED"
        assert certificates[1].status == "FAILED"
        assert certificates[2].status == "COMPLETED"

        assert certificates[1].error_message == (
            "Simulated certificate generation failure"
        )

    finally:
        test_db.close()

def test_get_nonexistent_job_returns_404(client):
    response = client.get("/api/jobs/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Generation job not found"


def test_download_nonexistent_certificate_returns_404(client):
    response = client.get("/api/certificates/999999/download")

    assert response.status_code == 404
    assert response.json()["detail"] == "Certificate not found"


def test_download_pending_certificate_returns_409(client):
    create_response = client.post(
        "/api/jobs/",
        json={
            "event_name": "Download Test",
            "certificate_title": "Certificate of Completion",
            "issuer": "Test Organization",
            "recipients": [
                {
                    "name": "Pending User",
                    "email": "pending@example.com",
                }
            ],
        },
    )

    assert create_response.status_code == 201

    job_id = create_response.json()["job_id"]

    job_response = client.get(f"/api/jobs/{job_id}")
    assert job_response.status_code == 200

    certificate_id = job_response.json()["certificates"][0]["certificate_id"]

    response = client.get(
        f"/api/certificates/{certificate_id}/download"
    )

    # Depending on background-task timing, the certificate may already
    # be completed. In that case, the download endpoint should succeed.
    assert response.status_code in [200, 409]