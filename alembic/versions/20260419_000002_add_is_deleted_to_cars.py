"""add is_deleted to cars

Revision ID: 20260419_000002
Revises: 20260419_000001
Create Date: 2026-04-19 12:30:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260419_000002"
down_revision = "20260419_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("cars") as batch_op:
        batch_op.add_column(
            sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false())
        )


def downgrade() -> None:
    with op.batch_alter_table("cars") as batch_op:
        batch_op.drop_column("is_deleted")
