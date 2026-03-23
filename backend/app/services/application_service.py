from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.application import Application
from app.repositories.application_repository import ApplicationRepository
from app.schemas.application import ApplicationCreate, ApplicationStats, ApplicationUpdate


class ApplicationService:
    def __init__(self, db: Session) -> None:
        self.repo = ApplicationRepository(db)

    def create(self, user_id: int, data: ApplicationCreate) -> Application:
        return self.repo.create(
            user_id=user_id,
            job_id=data.job_id,
            cv_id=data.cv_id,
            notes=data.notes,
            applied_at=data.applied_at,
        )

    def list_for_user(self, user_id: int) -> list[Application]:
        return self.repo.list_by_user(user_id)

    def get_or_404(self, app_id: int, user_id: int) -> Application:
        app = self.repo.get_by_id_and_user(app_id, user_id)
        if not app:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
        return app

    def update(self, app_id: int, user_id: int, data: ApplicationUpdate) -> Application:
        app = self.get_or_404(app_id, user_id)
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        return self.repo.update(app, **updates)

    def delete(self, app_id: int, user_id: int) -> None:
        app = self.get_or_404(app_id, user_id)
        self.repo.delete(app)

    def get_stats(self, user_id: int) -> ApplicationStats:
        raw = self.repo.stats_by_user(user_id)
        return ApplicationStats(**raw)
