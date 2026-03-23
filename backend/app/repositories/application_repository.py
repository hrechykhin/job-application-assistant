from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.application import Application, ApplicationStatus


class ApplicationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, app_id: int) -> Application | None:
        return self.db.get(Application, app_id)

    def get_by_id_and_user(self, app_id: int, user_id: int) -> Application | None:
        return self.db.scalar(
            select(Application).where(Application.id == app_id, Application.user_id == user_id)
        )

    def list_by_user(self, user_id: int, limit: int = 200, offset: int = 0) -> list[Application]:
        return list(
            self.db.scalars(
                select(Application)
                .options(joinedload(Application.job))
                .where(Application.user_id == user_id)
                .order_by(Application.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
        )

    def create(self, user_id: int, job_id: int, cv_id: int | None, notes: str | None, applied_at: datetime | None) -> Application:
        app = Application(
            user_id=user_id,
            job_id=job_id,
            cv_id=cv_id,
            notes=notes,
            applied_at=applied_at,
            status=ApplicationStatus.SAVED,
        )
        self.db.add(app)
        self.db.flush()
        return app

    def update(self, app: Application, **fields) -> Application:
        for key, value in fields.items():
            setattr(app, key, value)
        self.db.flush()
        return app

    def delete(self, app: Application) -> None:
        self.db.delete(app)
        self.db.flush()

    def stats_by_user(self, user_id: int) -> dict:
        rows = self.db.execute(
            select(Application.status, func.count(Application.id))
            .where(Application.user_id == user_id)
            .group_by(Application.status)
        ).all()

        by_status = {r[0].value: r[1] for r in rows}
        total = sum(by_status.values())
        applied = sum(v for k, v in by_status.items() if k in ("APPLIED", "INTERVIEW", "OFFER", "REJECTED"))
        interviews = by_status.get("INTERVIEW", 0) + by_status.get("OFFER", 0)
        offers = by_status.get("OFFER", 0)

        return {
            "total": total,
            "by_status": by_status,
            "interview_rate": round(interviews / applied, 2) if applied else 0.0,
            "offer_rate": round(offers / applied, 2) if applied else 0.0,
        }
