"""Add pipeline statuses: SCREENING, TEST_TASK, TECHNICAL_INTERVIEW, TEAM_INTERVIEW

Revision ID: 006
Revises: 005
Create Date: 2026-05-25 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "006"
down_revision: str | None = "005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'SCREENING' AFTER 'APPLIED'")
    op.execute("ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'TEST_TASK' AFTER 'SCREENING'")
    op.execute(
        "ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'TECHNICAL_INTERVIEW' AFTER 'TEST_TASK'"
    )
    op.execute(
        "ALTER TYPE applicationstatus ADD VALUE IF NOT EXISTS 'TEAM_INTERVIEW' AFTER 'TECHNICAL_INTERVIEW'"
    )
    # Rename existing INTERVIEW rows to TEAM_INTERVIEW
    op.execute("UPDATE applications SET status = 'TEAM_INTERVIEW' WHERE status = 'INTERVIEW'")
    # Rename the enum value (requires PostgreSQL 10+)
    op.execute("ALTER TYPE applicationstatus RENAME VALUE 'INTERVIEW' TO 'INTERVIEW_DEPRECATED'")


def downgrade() -> None:
    op.execute("ALTER TYPE applicationstatus RENAME VALUE 'INTERVIEW_DEPRECATED' TO 'INTERVIEW'")
    op.execute("UPDATE applications SET status = 'INTERVIEW' WHERE status = 'TEAM_INTERVIEW'")
    op.execute("""
        UPDATE applications
        SET status = 'INTERVIEW'
        WHERE status IN ('SCREENING', 'TEST_TASK', 'TECHNICAL_INTERVIEW')
    """)
    op.execute("""
        CREATE TYPE applicationstatus_new AS ENUM ('SAVED', 'APPLIED', 'INTERVIEW', 'OFFER', 'REJECTED')
    """)
    op.execute("""
        ALTER TABLE applications
        ALTER COLUMN status TYPE applicationstatus_new
        USING status::text::applicationstatus_new
    """)
    op.execute("DROP TYPE applicationstatus")
    op.execute("ALTER TYPE applicationstatus_new RENAME TO applicationstatus")
