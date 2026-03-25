from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job import Job


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, job_id: int) -> Job | None:
        return self.db.get(Job, job_id)

    def get_by_id_and_user(self, job_id: int, user_id: int) -> Job | None:
        return self.db.scalar(select(Job).where(Job.id == job_id, Job.user_id == user_id))

    def list_by_user(self, user_id: int, limit: int = 100, offset: int = 0) -> list[Job]:
        return list(
            self.db.scalars(
                select(Job)
                .where(Job.user_id == user_id)
                .order_by(Job.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
        )

    def create(self, user_id: int, **fields) -> Job:
        job = Job(user_id=user_id, **fields)
        self.db.add(job)
        self.db.flush()
        return job

    def update(self, job: Job, **fields) -> Job:
        for key, value in fields.items():
            if value is not None:
                setattr(job, key, value)
        self.db.flush()
        return job

    def delete(self, job: Job) -> None:
        self.db.delete(job)
        self.db.flush()
