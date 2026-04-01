"""Merge notification branch heads

Revision ID: merge_notification_heads
Revises: 20260128_add_notifications_tables, add_apple_signin_fields
Create Date: 2026-04-01

"""
from typing import Union

revision: str = "merge_notification_heads"
down_revision: Union[tuple, None] = (
    "20260128_add_notifications_tables",
    "add_apple_signin_fields",
)
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
