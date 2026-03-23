from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_analysis import AIAnalysis, AnalysisType


class AIAnalysisRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_cached(self, user_id: int, job_id: int, cv_id: int, analysis_type: AnalysisType) -> AIAnalysis | None:
        return self.db.scalar(
            select(AIAnalysis)
            .where(
                AIAnalysis.user_id == user_id,
                AIAnalysis.job_id == job_id,
                AIAnalysis.cv_id == cv_id,
                AIAnalysis.analysis_type == analysis_type,
            )
            .order_by(AIAnalysis.created_at.desc())
        )

    def create(
        self,
        user_id: int,
        job_id: int,
        cv_id: int,
        analysis_type: AnalysisType,
        result_json: dict,
        prompt_version: str = "v1",
    ) -> AIAnalysis:
        record = AIAnalysis(
            user_id=user_id,
            job_id=job_id,
            cv_id=cv_id,
            analysis_type=analysis_type,
            result_json=result_json,
            prompt_version=prompt_version,
        )
        self.db.add(record)
        self.db.flush()
        return record

    def list_by_user_and_job(self, user_id: int, job_id: int) -> list[AIAnalysis]:
        return list(
            self.db.scalars(
                select(AIAnalysis)
                .where(AIAnalysis.user_id == user_id, AIAnalysis.job_id == job_id)
                .order_by(AIAnalysis.created_at.desc())
            )
        )
