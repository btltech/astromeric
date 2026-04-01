"""Add time_confidence and data_quality columns to profiles

Revision ID: add_time_confidence_data_quality
Revises: add_notification_prefs
Create Date: 2026-04-01
"""
from alembic import op
import sqlalchemy as sa

revision = "add_time_confidence_data_quality"
down_revision = "add_notification_prefs"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("profiles") as batch_op:
        batch_op.add_column(
            sa.Column("time_confidence", sa.String(20), nullable=True, server_default="unknown")
        )
        batch_op.add_column(
            sa.Column("data_quality", sa.String(20), nullable=True)
        )


def downgrade():
    with op.batch_alter_table("profiles") as batch_op:
        batch_op.drop_column("time_confidence")
        batch_op.drop_column("data_quality")
