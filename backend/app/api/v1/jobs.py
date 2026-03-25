from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.job import JobCreate, JobImportPreview, JobImportRequest, JobRead, JobUpdate
from app.services.ai_service import AIService
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/import-url", response_model=JobImportPreview)
def import_job_from_url(
    body: JobImportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = AIService(db)
    result = svc.import_job_from_url(current_user.id, body.url)
    db.commit()
    return result


@router.get("", response_model=list[JobRead])
def list_jobs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = JobService(db)
    return svc.list_for_user(current_user.id)


@router.post("", response_model=JobRead, status_code=201)
def create_job(
    body: JobCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    svc = JobService(db)
    job = svc.create(current_user.id, body)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobRead)
def get_job(
    job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    svc = JobService(db)
    return svc.get_or_404(job_id, current_user.id)


@router.patch("/{job_id}", response_model=JobRead)
def update_job(
    job_id: int,
    body: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = JobService(db)
    job = svc.update(job_id, current_user.id, body)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    svc = JobService(db)
    svc.delete(job_id, current_user.id)
    db.commit()
