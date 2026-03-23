"""Rename cvs.s3_key to file_key

Revision ID: 002
Revises: 001
Create Date: 2026-03-23

"""
from typing import Sequence, Union
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("cvs", "s3_key", new_column_name="file_key")


def downgrade() -> None:
    op.alter_column("cvs", "file_key", new_column_name="s3_key")
