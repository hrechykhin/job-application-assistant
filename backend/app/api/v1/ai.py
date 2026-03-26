from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.repositories.ai_usage_log_repository import AIUsageLogRepository
from app.schemas.ai import (
    AIQuotaRead,
    CoverLetterRequest,
    CoverLetterResult,
    CVTailoringRequest,
    CVTailoringResult,
    JobMatchRequest,
    JobMatchResult,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/quota", response_model=AIQuotaRead)
def get_quota(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = AIUsageLogRepository(db)
    used = repo.count_today(current_user.id)
    limit = settings.AI_MAX_REQUESTS_PER_DAY
    now = datetime.now(UTC)
    resets_at = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return AIQuotaRead(used=used, limit=limit, remaining=max(0, limit - used), resets_at=resets_at)


@router.post("/job-match", response_model=JobMatchResult)
def analyze_job_match(
    body: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = AIService(db)
    result = svc.analyze_job_match(current_user.id, body.cv_id, body.job_id)
    db.commit()
    return result


@router.post("/cv-tailoring", response_model=CVTailoringResult)
def generate_cv_tailoring(
    body: CVTailoringRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = AIService(db)
    result = svc.generate_cv_tailoring(current_user.id, body.cv_id, body.job_id)
    db.commit()
    return result


@router.post("/cover-letter", response_model=CoverLetterResult)
def generate_cover_letter(
    body: CoverLetterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = AIService(db)
    result = svc.generate_cover_letter(current_user.id, body.cv_id, body.job_id, body.tone)
    db.commit()
    return result
