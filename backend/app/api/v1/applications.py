from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationReadWithJob, ApplicationStats, ApplicationUpdate
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationReadWithJob])
def list_applications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = ApplicationService(db)
    return svc.list_for_user(current_user.id)


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(
    body: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = ApplicationService(db)
    app = svc.create(current_user.id, body)
    db.commit()
    db.refresh(app)
    return app


@router.get("/stats", response_model=ApplicationStats)
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = ApplicationService(db)
    return svc.get_stats(current_user.id)


@router.get("/{app_id}", response_model=ApplicationReadWithJob)
def get_application(app_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = ApplicationService(db)
    return svc.get_or_404(app_id, current_user.id)


@router.patch("/{app_id}", response_model=ApplicationRead)
def update_application(
    app_id: int,
    body: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    svc = ApplicationService(db)
    app = svc.update(app_id, current_user.id, body)
    db.commit()
    db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=204)
def delete_application(app_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    svc = ApplicationService(db)
    svc.delete(app_id, current_user.id)
    db.commit()
