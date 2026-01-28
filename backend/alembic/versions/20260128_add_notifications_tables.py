"""Add device tokens and transit subscriptions

Revision ID: 20260128_add_notifications_tables
Revises: add_notification_prefs
Create Date: 2026-01-28 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260128_add_notifications_tables"
down_revision: Union[str, None] = "add_notification_prefs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "device_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("platform", sa.String(length=20), nullable=False, server_default="ios"),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("token", name="uq_device_tokens_token"),
    )
    op.create_index("ix_device_tokens_user_id", "device_tokens", ["user_id"])

    op.create_table(
        "transit_subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("profile_id", sa.Integer(), sa.ForeignKey("profiles.id"), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_transit_subscriptions_profile_id", "transit_subscriptions", ["profile_id"])
    op.create_index("ix_transit_subscriptions_email", "transit_subscriptions", ["email"])


def downgrade() -> None:
    op.drop_index("ix_transit_subscriptions_email", table_name="transit_subscriptions")
    op.drop_index("ix_transit_subscriptions_profile_id", table_name="transit_subscriptions")
    op.drop_table("transit_subscriptions")

    op.drop_index("ix_device_tokens_user_id", table_name="device_tokens")
    op.drop_table("device_tokens")
