from fastapi import FastAPI

from app.database.database import Base, engine
from app.database import models
from app.api.routes import router
from app.api.certificate_routes import router as certificate_router
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator API",
    description="Backend API for bulk certificate generation.",
    version="1.0.0",
)

app.include_router(router)
app.include_router(certificate_router)

@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }