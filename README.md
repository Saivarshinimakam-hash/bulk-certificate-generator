# Bulk Certificate Generator API

A backend API for generating certificates in bulk from a predefined certificate template.

The system accepts a single bulk generation request containing recipient details, creates a generation job, processes certificates in the background, tracks progress and failures, and provides APIs to retrieve generated certificates.

## Features

- Bulk certificate generation through a single API request
- Input validation using Pydantic
- Background processing using FastAPI BackgroundTasks
- Individual certificate status tracking
- Job-level progress tracking
- Failure isolation: one failed certificate does not stop the remaining certificates
- PDF certificate generation using ReportLab
- SQLite relational database using SQLAlchemy
- Certificate download endpoint
- Automated API and service tests using pytest

## Tech Stack

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- ReportLab
- pytest
- Uvicorn

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── api/
│   │   ├── routes.py
│   │   └── certificate_routes.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   └── models.py
│   │
│   ├── schemas/
│   │   └── certificate.py
│   │
│   ├── services/
│   │   ├── certificate_generator.py
│   │   └── job_processor.py
│   │
│   └── main.py
│
├── generated/
├── templates/
├── tests/
│   ├── conftest.py
│   ├── test_jobs.py
│   └── test_generation.py
│
├── .gitignore
├── README.md
└── requirements.txt