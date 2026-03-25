"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "cvs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("s3_key", sa.String(512), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cvs_id", "cvs", ["id"])
    op.create_index("ix_cvs_user_id", "cvs", ["user_id"])

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("job_url", sa.String(2048), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jobs_id", "jobs", ["id"])
    op.create_index("ix_jobs_user_id", "jobs", ["user_id"])

    op.execute(
        "CREATE TYPE applicationstatus AS ENUM ('SAVED', 'APPLIED', 'INTERVIEW', 'OFFER', 'REJECTED')"
    )
    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("cv_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "SAVED",
                "APPLIED",
                "INTERVIEW",
                "OFFER",
                "REJECTED",
                name="applicationstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="SAVED",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["cv_id"], ["cvs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_applications_id", "applications", ["id"])
    op.create_index("ix_applications_user_id", "applications", ["user_id"])
    op.create_index("ix_applications_status", "applications", ["status"])

    op.execute("CREATE TYPE analysistype AS ENUM ('JOB_MATCH', 'CV_TAILORING', 'COVER_LETTER')")
    op.create_table(
        "ai_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("cv_id", sa.Integer(), nullable=False),
        sa.Column(
            "analysis_type",
            postgresql.ENUM(
                "JOB_MATCH", "CV_TAILORING", "COVER_LETTER", name="analysistype", create_type=False
            ),
            nullable=False,
        ),
        sa.Column("prompt_version", sa.String(32), nullable=False, server_default="v1"),
        sa.Column("result_json", postgresql.JSONB(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["cv_id"], ["cvs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_analyses_id", "ai_analyses", ["id"])
    op.create_index("ix_ai_analyses_user_id", "ai_analyses", ["user_id"])
    op.create_index("ix_ai_analyses_analysis_type", "ai_analyses", ["analysis_type"])


def downgrade() -> None:
    op.drop_table("ai_analyses")
    op.execute("DROP TYPE analysistype")
    op.drop_table("applications")
    op.execute("DROP TYPE applicationstatus")
    op.drop_table("jobs")
    op.drop_table("cvs")
    op.drop_table("users")
