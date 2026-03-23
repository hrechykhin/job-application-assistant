from datetime import datetime

from pydantic import BaseModel, HttpUrl


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
