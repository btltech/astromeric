"""Add notification preferences to user

Revision ID: add_notification_prefs
Revises: 981736acf625
Create Date: 2026-01-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_notification_prefs'
down_revision: Union[str, None] = '981736acf625'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add notification preference columns to users table
    op.add_column('users', sa.Column('alert_mercury_retrograde', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('alert_frequency', sa.String(length=20), nullable=False, server_default='every_retrograde'))
    op.add_column('users', sa.Column('last_retrograde_alert', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove notification preference columns
    op.drop_column('users', 'last_retrograde_alert')
    op.drop_column('users', 'alert_frequency')
    op.drop_column('users', 'alert_mercury_retrograde')
