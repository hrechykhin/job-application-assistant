from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_usage_log import AIUsageLog


class AIUsageLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count_today(self, user_id: int) -> int:
        start_of_day = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        stmt = (
            select(func.count())
            .select_from(AIUsageLog)
            .where(
                AIUsageLog.user_id == user_id,
                AIUsageLog.created_at >= start_of_day,
            )
        )
        return self.db.execute(stmt).scalar_one()

    def create(
        self,
        user_id: int,
        analysis_type: str,
        model: str | None,
        prompt_tokens: int | None,
        completion_tokens: int | None,
    ) -> AIUsageLog:
        record = AIUsageLog(
            user_id=user_id,
            analysis_type=analysis_type,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        self.db.add(record)
        self.db.flush()
        return record
