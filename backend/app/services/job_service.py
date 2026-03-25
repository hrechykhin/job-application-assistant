from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.job import Job
from app.repositories.job_repository import JobRepository
from app.schemas.job import JobCreate, JobUpdate


class JobService:
    def __init__(self, db: Session) -> None:
        self.repo = JobRepository(db)

    def create(self, user_id: int, data: JobCreate) -> Job:
        return self.repo.create(user_id=user_id, **data.model_dump())

    def list_for_user(self, user_id: int) -> list[Job]:
        return self.repo.list_by_user(user_id)

    def get_or_404(self, job_id: int, user_id: int) -> Job:
        job = self.repo.get_by_id_and_user(job_id, user_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
        return job

    def update(self, job_id: int, user_id: int, data: JobUpdate) -> Job:
        job = self.get_or_404(job_id, user_id)
        return self.repo.update(
            job, **{k: v for k, v in data.model_dump().items() if v is not None}
        )

    def delete(self, job_id: int, user_id: int) -> None:
        job = self.get_or_404(job_id, user_id)
        self.repo.delete(job)
