from datetime import datetime
from enum import StrEnum

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AnalysisType(StrEnum):
    JOB_MATCH = "JOB_MATCH"
    CV_TAILORING = "CV_TAILORING"
    COVER_LETTER = "COVER_LETTER"


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    cv_id: Mapped[int] = mapped_column(ForeignKey("cvs.id", ondelete="CASCADE"), nullable=False)
    analysis_type: Mapped[AnalysisType] = mapped_column(
        Enum(AnalysisType, name="analysistype"), nullable=False, index=True
    )
    prompt_version: Mapped[str] = mapped_column(String(32), default="v1", nullable=False)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    cv: Mapped["CV"] = relationship("CV", back_populates="ai_analyses")
    job: Mapped["Job"] = relationship("Job", back_populates="ai_analyses")
