"""Add Apple Sign-In fields to User

Revision ID: add_apple_signin_fields
Revises: add_notification_prefs
Create Date: 2026-01-26 22:40:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_apple_signin_fields'
down_revision = 'add_notification_prefs'
branch_labels = None
depends_on = None


def upgrade():
    # Use IF NOT EXISTS to be idempotent (columns may already exist)
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS external_id VARCHAR")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(20)")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_external_id ON users(external_id)")
    # Make hashed_password nullable for Apple users (safe to run again)
    op.execute("ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL")


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('hashed_password',
                              existing_type=sa.String(),
                              nullable=False)
        batch_op.drop_index('ix_users_external_id')
        batch_op.drop_column('full_name')
        batch_op.drop_column('auth_provider')
        batch_op.drop_column('external_id')
