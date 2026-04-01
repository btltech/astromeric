"""Add time_confidence and data_quality columns to profiles

Revision ID: add_time_confidence_data_quality
Revises: add_notification_prefs
Create Date: 2026-04-01
"""
from alembic import op
import sqlalchemy as sa

revision = "add_time_confidence_data_quality"
down_revision = "merge_notification_heads"
branch_labels = None
depends_on = None


def upgrade():
    # Use IF NOT EXISTS to be idempotent (columns may already exist)
    op.execute("ALTER TABLE profiles ADD COLUMN IF NOT EXISTS time_confidence VARCHAR(20) DEFAULT 'unknown'")
    op.execute("ALTER TABLE profiles ADD COLUMN IF NOT EXISTS data_quality VARCHAR(20)")


def downgrade():
    with op.batch_alter_table("profiles") as batch_op:
        batch_op.drop_column("time_confidence")
        batch_op.drop_column("data_quality")
