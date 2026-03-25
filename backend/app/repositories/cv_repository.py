from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.cv import CV


class CVRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, cv_id: int) -> CV | None:
        return self.db.get(CV, cv_id)

    def get_by_id_and_user(self, cv_id: int, user_id: int) -> CV | None:
        return self.db.scalar(select(CV).where(CV.id == cv_id, CV.user_id == user_id))

    def list_by_user(self, user_id: int, limit: int = 50, offset: int = 0) -> list[CV]:
        return list(
            self.db.scalars(
                select(CV)
                .where(CV.user_id == user_id)
                .order_by(CV.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
        )

    def create(
        self, user_id: int, original_filename: str, file_key: str, extracted_text: str | None = None
    ) -> CV:
        cv = CV(
            user_id=user_id,
            original_filename=original_filename,
            file_key=file_key,
            extracted_text=extracted_text,
        )
        self.db.add(cv)
        self.db.flush()
        return cv

    def delete(self, cv: CV) -> None:
        self.db.delete(cv)
        self.db.flush()
