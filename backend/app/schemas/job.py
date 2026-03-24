from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_validator


class JobCreate(BaseModel):
    company_name: str
    title: str
    location: str | None = None
    job_url: str | None = None
    description: str


class JobUpdate(BaseModel):
    company_name: str | None = None
    title: str | None = None
    location: str | None = None
    job_url: str | None = None
    description: str | None = None


class JobImportRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def must_be_http(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class JobImportPreview(BaseModel):
    title: str
    company_name: str
    location: str | None = None
    description: str


class JobRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    company_name: str
    title: str
    location: str | None
    job_url: str | None
    description: str
    created_at: datetime
    updated_at: datetime
