from datetime import datetime

from pydantic import BaseModel


class CVRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int
    original_filename: str
    file_key: str
    created_at: datetime
    has_text: bool = False

    @classmethod
    def from_orm_with_text_flag(cls, cv: object) -> "CVRead":
        obj = cls.model_validate(cv)
        obj.has_text = bool(getattr(cv, "extracted_text", None))
        return obj


class CVReadWithText(CVRead):
    extracted_text: str | None = None
