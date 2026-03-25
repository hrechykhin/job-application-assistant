"""Add deadline, follow_up_date, interview_at to applications

Revision ID: 004
Revises: 003
Create Date: 2026-03-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: str | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("applications", sa.Column("deadline", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "applications", sa.Column("follow_up_date", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "applications", sa.Column("interview_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("applications", "interview_at")
    op.drop_column("applications", "follow_up_date")
    op.drop_column("applications", "deadline")
