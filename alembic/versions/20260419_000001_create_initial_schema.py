"""create initial schema

Revision ID: 20260419_000001
Revises: 
Create Date: 2026-04-19 00:00:01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260419_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("telegram_id", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=False),
        sa.Column("service_interval", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("telegram_id"),
    )
    op.create_table(
        "cars",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.telegram_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_car_per_user"),
    )
    op.create_table(
        "maintenances",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=False),
        sa.Column("performed_at", sa.Date(), nullable=False),
        sa.Column("odo", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["car_id"], ["cars.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "refuelings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("odo", sa.Integer(), nullable=False),
        sa.Column("filing_volume", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["car_id"], ["cars.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("refuelings")
    op.drop_table("maintenances")
    op.drop_table("cars")
    op.drop_table("users")
