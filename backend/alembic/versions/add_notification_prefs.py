"""Add notification preferences to user

Revision ID: add_notification_prefs
Revises: 981736acf625
Create Date: 2026-01-13 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_notification_prefs"
down_revision: Union[str, None] = "981736acf625"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add notification preference columns to users table with check for existing columns
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("users")]
    print(f"DEBUG: Found columns in users: {columns}")

    if "alert_mercury_retrograde" not in columns:
        print("DEBUG: Adding alert_mercury_retrograde")
        op.add_column(
            "users",
            sa.Column(
                "alert_mercury_retrograde",
                sa.Boolean(),
                nullable=False,
                server_default="true",
            ),
        )
    else:
        print("DEBUG: alert_mercury_retrograde already exists, skipping")

    if "alert_frequency" not in columns:
        print("DEBUG: Adding alert_frequency")
        op.add_column(
            "users",
            sa.Column(
                "alert_frequency",
                sa.String(length=20),
                nullable=False,
                server_default="every_retrograde",
            ),
        )
    else:
        print("DEBUG: alert_frequency already exists, skipping")

    if "last_retrograde_alert" not in columns:
        print("DEBUG: Adding last_retrograde_alert")
        op.add_column(
            "users", sa.Column("last_retrograde_alert", sa.DateTime(), nullable=True)
        )
    else:
        print("DEBUG: last_retrograde_alert already exists, skipping")


def downgrade() -> None:
    # Remove notification preference columns
    op.drop_column("users", "last_retrograde_alert")
    op.drop_column("users", "alert_frequency")
    op.drop_column("users", "alert_mercury_retrograde")
