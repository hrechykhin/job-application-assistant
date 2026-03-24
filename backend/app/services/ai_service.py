import logging
from html.parser import HTMLParser

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.ai_client import (
    PROMPT_VERSION,
    build_cover_letter_prompt,
    build_cv_tailoring_prompt,
    build_job_import_prompt,
    build_job_match_prompt,
    get_ai_client,
)
from app.models.ai_analysis import AnalysisType
from app.repositories.ai_analysis_repository import AIAnalysisRepository
from app.repositories.ai_usage_log_repository import AIUsageLogRepository
from app.repositories.cv_repository import CVRepository
from app.repositories.job_repository import JobRepository
from app.schemas.ai import CoverLetterResult, CVTailoringResult, JobMatchResult
from app.schemas.job import JobImportPreview


class _TextExtractor(HTMLParser):
    """Minimal HTML-to-text converter using the stdlib parser."""

    _SKIP_TAGS = {"script", "style", "head", "nav", "footer", "header", "noscript"}

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._depth = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self._SKIP_TAGS:
            self._depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS and self._depth > 0:
            self._depth -= 1

    def handle_data(self, data: str) -> None:
        if self._depth == 0:
            text = data.strip()
            if text:
                self._parts.append(text)

    def get_text(self) -> str:
        return " ".join(self._parts)

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, db: Session) -> None:
        self.cv_repo = CVRepository(db)
        self.job_repo = JobRepository(db)
        self.analysis_repo = AIAnalysisRepository(db)
        self.usage_repo = AIUsageLogRepository(db)
        self.db = db

    def _check_ai_enabled(self) -> None:
        if not settings.AI_ENABLED:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI features are currently disabled.",
            )

    def _check_quota(self, user_id: int) -> None:
        today_count = self.usage_repo.count_today(user_id)
        if today_count >= settings.AI_MAX_REQUESTS_PER_DAY:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily AI limit of {settings.AI_MAX_REQUESTS_PER_DAY} requests reached. Try again tomorrow.",
            )

    def _validate_cv_text(self, cv_text: str) -> None:
        if len(cv_text) > settings.AI_MAX_CV_CHARS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"CV text too long ({len(cv_text)} chars). Maximum allowed: {settings.AI_MAX_CV_CHARS}.",
            )

    def _validate_job_text(self, job_text: str) -> None:
        if len(job_text) > settings.AI_MAX_JOB_CHARS:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Job description too long ({len(job_text)} chars). Maximum allowed: {settings.AI_MAX_JOB_CHARS}.",
            )

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

        self._check_ai_enabled()
        self._check_quota(user_id)

        cv_text = self._get_cv_text(cv_id, user_id)
        job = self._get_job_text(job_id, user_id)
        self._validate_cv_text(cv_text)
        self._validate_job_text(job.description)

        client = get_ai_client()
        try:
            system, user_msg = build_job_match_prompt(cv_text, job.description)
            response = client.chat(system, user_msg)
        except Exception as e:
            logger.error("AI job match failed: %s", e)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable.")

        result = JobMatchResult(**response.data)
        self.analysis_repo.create(user_id, job_id, cv_id, AnalysisType.JOB_MATCH, response.data, PROMPT_VERSION)
        self.usage_repo.create(user_id, AnalysisType.JOB_MATCH.value, response.model, response.prompt_tokens, response.completion_tokens)
        return result

    def generate_cv_tailoring(self, user_id: int, cv_id: int, job_id: int) -> CVTailoringResult:
        cached = self.analysis_repo.get_cached(user_id, job_id, cv_id, AnalysisType.CV_TAILORING)
        if cached and cached.prompt_version == PROMPT_VERSION:
            return CVTailoringResult(**cached.result_json)

        self._check_ai_enabled()
        self._check_quota(user_id)

        cv_text = self._get_cv_text(cv_id, user_id)
        job = self._get_job_text(job_id, user_id)
        self._validate_cv_text(cv_text)
        self._validate_job_text(job.description)

        client = get_ai_client()
        try:
            system, user_msg = build_cv_tailoring_prompt(cv_text, job.description)
            response = client.chat(system, user_msg)
        except Exception as e:
            logger.error("AI CV tailoring failed: %s", e)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable.")

        result = CVTailoringResult(**response.data)
        self.analysis_repo.create(user_id, job_id, cv_id, AnalysisType.CV_TAILORING, response.data, PROMPT_VERSION)
        self.usage_repo.create(user_id, AnalysisType.CV_TAILORING.value, response.model, response.prompt_tokens, response.completion_tokens)
        return result

    def import_job_from_url(self, user_id: int, url: str) -> JobImportPreview:
        self._check_ai_enabled()
        self._check_quota(user_id)

        try:
            response = httpx.get(url, timeout=10, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.warning("Failed to fetch URL %s: %s", url, e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Could not fetch the URL.")

        extractor = _TextExtractor()
        extractor.feed(response.text)
        page_text = extractor.get_text()

        if not page_text.strip():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No readable text found at the URL.")

        client = get_ai_client()
        try:
            system, user_msg = build_job_import_prompt(page_text)
            ai_response = client.chat(system, user_msg)
        except Exception as e:
            logger.error("AI job import failed: %s", e)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable.")

        self.usage_repo.create(user_id, "JOB_IMPORT", ai_response.model, ai_response.prompt_tokens, ai_response.completion_tokens)
        return JobImportPreview(**ai_response.data)

    def generate_cover_letter(self, user_id: int, cv_id: int, job_id: int, tone: str = "professional") -> CoverLetterResult:
        self._check_ai_enabled()
        self._check_quota(user_id)

        cv_text = self._get_cv_text(cv_id, user_id)
        job = self._get_job_text(job_id, user_id)
        self._validate_cv_text(cv_text)
        self._validate_job_text(job.description)

        client = get_ai_client()
        try:
            system, user_msg = build_cover_letter_prompt(
                cv_text, job.description, job.company_name, job.title, tone
            )
            response = client.chat(system, user_msg)
        except Exception as e:
            logger.error("AI cover letter failed: %s", e)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="AI service unavailable.")

        result = CoverLetterResult(**response.data)
        self.analysis_repo.create(user_id, job_id, cv_id, AnalysisType.COVER_LETTER, response.data, PROMPT_VERSION)
        self.usage_repo.create(user_id, AnalysisType.COVER_LETTER.value, response.model, response.prompt_tokens, response.completion_tokens)
        return result
