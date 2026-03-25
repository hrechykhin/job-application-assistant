from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.limiter import limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
@limiter.limit("10/minute")
def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    svc = AuthService(db)
    user = svc.register(body.email, body.password, body.full_name)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    svc = AuthService(db)
    return svc.login(body.email, body.password)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    svc = AuthService(db)
    return svc.refresh(body.refresh_token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user
