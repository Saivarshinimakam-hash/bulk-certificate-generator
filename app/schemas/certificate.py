from pydantic import BaseModel, EmailStr, Field


class RecipientCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr


class GenerationJobCreate(BaseModel):
    event_name: str = Field(..., min_length=2, max_length=255)
    certificate_title: str = Field(..., min_length=2, max_length=255)
    issuer: str = Field(..., min_length=2, max_length=255)
    recipients: list[RecipientCreate] = Field(
        ...,
        min_length=1,
        max_length=1000,
    )