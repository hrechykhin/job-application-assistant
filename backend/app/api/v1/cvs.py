from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.cv import CVRead
from app.services.cv_service import CVService

router = APIRouter(prefix="/cvs", tags=["cvs"])


@router.get("", response_model=list[CVRead])
def list_cvs(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = CVService(db)
    return [CVRead.from_orm_with_text_flag(cv) for cv in svc.list_for_user(current_user.id)]


@router.post("", response_model=CVRead, status_code=201)
def upload_cv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = CVService(db)
    cv = svc.upload(current_user.id, file)
    db.commit()
    db.refresh(cv)
    return CVRead.from_orm_with_text_flag(cv)


@router.get("/download/{cv_id}")
def download_cv(
    cv_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    svc = CVService(db)
    cv = svc.get_or_404(cv_id, current_user.id)
    file_path = Path(settings.STORAGE_PATH) / cv.file_key
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(str(file_path), filename=cv.original_filename)


@router.delete("/{cv_id}", status_code=204)
def delete_cv(
    cv_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    svc = CVService(db)
    svc.delete(cv_id, current_user.id)
    db.commit()
