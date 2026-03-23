import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.integrations.ai_client import (
    PROMPT_VERSION,
    build_cover_letter_prompt,
    build_cv_tailoring_prompt,
    build_job_match_prompt,
    get_ai_client,
)
from app.models.ai_analysis import AnalysisType
from app.repositories.ai_analysis_repository import AIAnalysisRepository
from app.repositories.cv_repository import CVRepository
from app.repositories.job_repository import JobRepository
from app.schemas.ai import CoverLetterResult, CVTailoringResult, JobMatchResult

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, db: Session) -> None:
        self.cv_repo = CVRepository(db)
        self.job_repo = JobRepository(db)
        self.analysis_repo = AIAnalysisRepository(db)
        self.db = db

    def _get_cv_text(self, cv_id: int, user_id: int) -> str:
        cv = self.cv_repo.get_by_id_and_user(cv_id, user_id)
        if not cv:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CV not found.")
        if not cv.extracted_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="CV has no extracted text. Re-upload the file.",
            )
        return cv.extracted_text

    def _get_job_text(self, job_id: int, user_id: int):
        job = self.job_repo.get_by_id_and_user(job_id, user_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
        return job

    def analyze_job_match(self, user_id: int, cv_id: int, job_id: int) -> JobMatchResult:
        cached = self.analysis_repo.get_cached(user_id, job_id, cv_id, AnalysisType.JOB_MATCH)
        if cached and cached.prompt_version == PROMPT_VERSION:
            return JobMatchResult(**cached.result_json)

        cv_text = self._get_cv_text(cv_id, user_id)
        job = self._get_job_text(job_id, user_id)
        client = get_ai_client()

        try:
            system, user_msg = build_job_match_prompt(cv_text, job.description)
            raw = client.chat(system, user_msg)
        except Exception as e:
            logger.error("AI job match failed: %s", e)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable.")

        result = JobMatchResult(**raw)
        self.analysis_repo.create(user_id, job_id, cv_id, AnalysisType.JOB_MATCH, raw, PROMPT_VERSION)
        return result

    def generate_cv_tailoring(self, user_id: int, cv_id: int, job_id: int) -> CVTailoringResult:
        cached = self.analysis_repo.get_cached(user_id, job_id, cv_id, AnalysisType.CV_TAILORING)
        if cached and cached.prompt_version == PROMPT_VERSION:
            return CVTailoringResult(**cached.result_json)

        cv_text = self._get_cv_text(cv_id, user_id)
        job = self._get_job_text(job_id, user_id)
        client = get_ai_client()

        try:
            system, user_msg = build_cv_tailoring_prompt(cv_text, job.description)
            raw = client.chat(system, user_msg)
        except Exception as e:
            logger.error("AI CV tailoring failed: %s", e)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable.")

        result = CVTailoringResult(**raw)
        self.analysis_repo.create(user_id, job_id, cv_id, AnalysisType.CV_TAILORING, raw, PROMPT_VERSION)
        return result

    def generate_cover_letter(self, user_id: int, cv_id: int, job_id: int, tone: str = "professional") -> CoverLetterResult:
        cv_text = self._get_cv_text(cv_id, user_id)
        job = self._get_job_text(job_id, user_id)
        client = get_ai_client()

        try:
            system, user_msg = build_cover_letter_prompt(
                cv_text, job.description, job.company_name, job.title, tone
            )
            raw = client.chat(system, user_msg)
        except Exception as e:
            logger.error("AI cover letter failed: %s", e)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable.")

        result = CoverLetterResult(**raw)
        self.analysis_repo.create(user_id, job_id, cv_id, AnalysisType.COVER_LETTER, raw, PROMPT_VERSION)
        return result
