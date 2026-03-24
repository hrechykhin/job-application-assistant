from datetime import datetime

from pydantic import BaseModel

from app.models.application import ApplicationStatus
from app.schemas.job import JobRead


class ApplicationCreate(BaseModel):
    job_id: int
    cv_id: int | None = None
    notes: str | None = None
    applied_at: datetime | None = None
    deadline: datetime | None = None
    follow_up_date: datetime | None = None
    interview_at: datetime | None = None


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    notes: str | None = None
    cv_id: int | None = None
    applied_at: datetime | None = None
    deadline: datetime | None = None
    follow_up_date: datetime | None = None
    interview_at: datetime | None = None


class ApplicationRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    job_id: int
    cv_id: int | None
    status: ApplicationStatus
    notes: str | None
    applied_at: datetime | None
    deadline: datetime | None
    follow_up_date: datetime | None
    interview_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ApplicationReadWithJob(ApplicationRead):
    job: JobRead | None = None


class ApplicationStats(BaseModel):
    total: int
    by_status: dict[str, int]
    interview_rate: float
    offer_rate: float
