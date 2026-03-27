from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_verification_token(self, token: str) -> User | None:
        return self.db.scalar(select(User).where(User.verification_token == token))

    def create(self, email: str, hashed_password: str, full_name: str | None = None) -> User:
        user = User(email=email, hashed_password=hashed_password, full_name=full_name)
        self.db.add(user)
        self.db.flush()
        return user

    def set_verification_token(self, user: User, token: str, expires_at: datetime) -> None:
        user.verification_token = token
        user.verification_token_expires_at = expires_at
        self.db.flush()

    def mark_verified(self, user: User) -> None:
        user.is_active = True
        user.verification_token = None
        user.verification_token_expires_at = None
        self.db.flush()

    def update(self, user: User, **fields) -> User:
        for key, value in fields.items():
            if value is not None:
                setattr(user, key, value)
        self.db.flush()
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.flush()
