"""Add device tokens and transit subscriptions

Revision ID: notif_tables_20260128
Revises: add_notification_prefs
Create Date: 2026-01-28 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "notif_tables_20260128"
down_revision: Union[str, None] = "add_notification_prefs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use raw SQL with IF NOT EXISTS so this is idempotent (tables may already exist)
    op.execute("""
        CREATE TABLE IF NOT EXISTS device_tokens (
            id SERIAL PRIMARY KEY,
            token VARCHAR NOT NULL,
            platform VARCHAR(20) NOT NULL DEFAULT 'ios',
            user_id VARCHAR REFERENCES users(id),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT uq_device_tokens_token UNIQUE (token)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_device_tokens_user_id ON device_tokens(user_id)")

    op.execute("""
        CREATE TABLE IF NOT EXISTS transit_subscriptions (
            id SERIAL PRIMARY KEY,
            profile_id INTEGER NOT NULL REFERENCES profiles(id),
            email VARCHAR NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_transit_subscriptions_profile_id ON transit_subscriptions(profile_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_transit_subscriptions_email ON transit_subscriptions(email)")


def downgrade() -> None:
    op.drop_index("ix_transit_subscriptions_email", table_name="transit_subscriptions")
    op.drop_index("ix_transit_subscriptions_profile_id", table_name="transit_subscriptions")
    op.drop_table("transit_subscriptions")

    op.drop_index("ix_device_tokens_user_id", table_name="device_tokens")
    op.drop_table("device_tokens")
