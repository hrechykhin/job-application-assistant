import logging
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.integrations import storage
from app.models.cv import CV
from app.repositories.cv_repository import CVRepository
from app.utils.cv_parser import extract_text, validate_upload

logger = logging.getLogger(__name__)


class CVService:
    def __init__(self, db: Session) -> None:
        self.repo = CVRepository(db)

    def upload(self, user_id: int, file: UploadFile) -> CV:
        file_bytes = file.file.read()
        filename = file.filename or "upload"
        content_type = file.content_type or "application/octet-stream"

        try:
            validate_upload(filename, content_type, len(file_bytes))
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

        try:
            extracted = extract_text(file_bytes, filename)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

        file_key = f"cvs/{user_id}/{uuid.uuid4()}/{filename}"
        try:
            storage.save(file_bytes, file_key)
        except Exception as e:
            logger.error("File storage failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, detail="File storage unavailable."
            )

        return self.repo.create(
            user_id=user_id,
            original_filename=filename,
            file_key=file_key,
            extracted_text=extracted,
        )

    def list_for_user(self, user_id: int) -> list[CV]:
        return self.repo.list_by_user(user_id)

    def get_or_404(self, cv_id: int, user_id: int) -> CV:
        cv = self.repo.get_by_id_and_user(cv_id, user_id)
        if not cv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV not found.")
        return cv

    def delete(self, cv_id: int, user_id: int) -> None:
        cv = self.get_or_404(cv_id, user_id)
        try:
            storage.delete(cv.file_key)
        except Exception as e:
            logger.warning("Could not delete file: %s", e)
        self.repo.delete(cv)
