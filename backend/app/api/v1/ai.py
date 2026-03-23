from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import (
    CoverLetterRequest,
    CoverLetterResult,
    CVTailoringRequest,
    CVTailoringResult,
    JobMatchRequest,
    JobMatchResult,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])


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
