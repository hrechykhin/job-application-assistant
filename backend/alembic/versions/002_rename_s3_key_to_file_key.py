"""Rename cvs.s3_key to file_key

Revision ID: 002
Revises: 001
Create Date: 2026-03-23

"""

from collections.abc import Sequence

from alembic import op

revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("cvs", "s3_key", new_column_name="file_key")


def downgrade() -> None:
    op.alter_column("cvs", "file_key", new_column_name="s3_key")
